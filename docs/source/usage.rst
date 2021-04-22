Usage
=====

The lambda reads each tag of each RDS, EC2, Bucket and Stack instance, and when it finds the tag named

* **Saving**, if the value is ``Enabled``, it checks the following points
* **Stop**, if the instance status, hour and crontab value matches, it will stop the instance
* **Delete**, if the instance status, hour and crontab value matches, it will delete the instance
* **Start**, if the instance status, hour and crontab value matches, it will start the instance

You can define 4 tags types on your instace:

* Key=Saving,Value=Enabled
* Key=Stop,Value='``0 18 . . .``'
* Key=Delete,Value='``0 18 . . .``'
* Key=Start,Value='``0 8 . . .``'

and

* if you have added deleted protection on your object, you can force the deletion by **force** property
* if you need to split the load by one lambda per service, you can uncommented the lambda functions and **invoke_lambda** property
* you can decide which AWS services manage by **services_name** property
* the default **timezone** is ``Etc/GMT``

Search the **bold word** in the `serverless.yaml <https://github.com/bilardi/aws-saving/blob/master/serverless.yaml>`_ file,
or see below for an example.

Example
#######

You need an infrastructure with

* a bucket for loading your data
* a RDS instance where loading the bucket data
* an EC2 instance where installing your software
* a RDS cluster where loading the ETL data
* a domain with an user of SageMaker Studio
* a lambda for managing the saving costs

This system is not necessary 24H but only 2 hours in the morning from 8:00 AM and the developers work until 6:00 PM

* the EC2 and RDS instances in production can be started at 7:30 AM and stopped at 10:30 AM
* the stacks in staging (*) can be deleted at 6:00 PM
* the apps created by user of SageMaker Studio can be deleted at 6:00PM

The tags that you have to add to your objects are

* Key=Saving,Value=Enabled for all stacks, EC2 and RDS instances
* Key=Start,Value='``30 7 . . .``' for EC2 and RDS instances in production
* Key=Stop,Value='``30 10 . . .``' for EC2 and RDS instances in production
* Key=Delete,Value='``0 18 . . .``' for all stacks in staging (*)
* Key=Stop,Value='``0 18 . . .``' for all apps in that domain of SageMaker Studio

(*) or any other non-production environment that you can re-deploy as needed.
