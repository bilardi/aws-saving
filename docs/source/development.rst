Development
===========

The environments for development can be many: you can organize a **CI/CD system** with your favorite software.
The primary features of your CI/CD are: having a **complete environment for**

* **development** for each developer, to implement something and for running unit tests 
* **staging** for running unit and integration tests, to check everything before release
* **production**

Run tests
#########

.. code-block:: bash

    cd aws-saving/
    pip3 install --upgrade -r requirements.txt
    python3 -m unittest discover -v

Get services with start/stop features
#####################################

The goal is to implement this package for each AWS service can start and stop its instances.

.. code-block:: bash

    cd aws-saving/
    bash first.skimming.sh
    ls tmp/

Deploy on AWS
#############

.. code-block:: bash

    cd aws-saving/
    export AWS_PROFILE=your-account
    SLS_DEBUG=* sls deploy --stage development

Remove on AWS
#############

The stack has the tags necessary for being deleted itself by the lambda deployed in production.
Or you can run the integration tests passing the name of the STAGE deployed (ie, staging):

.. code-block:: bash

    cd aws-saving/
    export AWS_PROFILE=your-account
    # integration test for removing the stack you have created
    STAGE=staging python3 -m unittest discover -v -p integration_test_only_cloudformation.py

For testing all services, you already have to deploy the stack before run the integration tests below.
There is something missing: with the commands below, the stack deletion reaches the StackStatus value ``DELETE_FAILED``.
So you will have to skip manually RDS resources for deleting the stack (see **TODO** in `cloudformation.py <https://github.com/bilardi/aws-saving/blob/master/aws_saving/cloudformation.py>`_).

.. code-block:: bash

    cd aws-saving/
    export AWS_PROFILE=your-account
    # integration test for removing before s3, ec2, rds instances and then it tries to remove the stack you have created
    STAGE=staging python3 -m unittest discover -v -p integration_test_all_services.py
