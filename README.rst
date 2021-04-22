Getting started
===============

AWS saving package is implemented for deploying a lambda that you can invoke for stopping, deleting or starting each RDS, EC2, bucket and Stack instance.

The goal is to implement this package for each AWS service can stop, delete and start its instances.

It is part of the `educational repositories <https://github.com/pandle/materials>`_ to learn how to write stardard code and common uses of the TDD.

Prerequisites
#############

You can use `Serverless framework <https://www.serverless.com/framework/docs/providers/aws/guide/installation/>`_ for deploying the lambda function:
if you want to use the guide below, you have to install Serverless framework before and one plugin

.. code-block:: bash

    npm install -g serverless
    npm install serverless-python-requirements
    npm install serverless-cloudformation-sub-variables

If you want to use another AWS tool, you can see the repository `aws-tool-comparison <https://github.com/bilardi/aws-tool-comparison>`_ before to implement your version.

Installation
############

The package is not self-consistent. So you have to download the package by github and to install the requirements before to deploy on AWS:

.. code-block:: bash

    git clone https://github.com/bilardi/aws-saving
    cd aws-saving/
    pip3 install --upgrade -r requirements.txt
    export AWS_PROFILE=your-account
    SLS_DEBUG=* sls deploy --stage production

Or if you want to use this package into your code, you can install by python3-pip:

.. code-block:: bash

    pip3 install aws_saving
    python3
    >>> import aws_saving.saving as Saving
    >>> help(Saving)

Read the documentation on `readthedocs <https://aws-saving.readthedocs.io/en/latest/>`_ for

* Usage
* Development

Change Log
##########

See `CHANGELOG.md <https://github.com/bilardi/aws-saving/blob/master/CHANGELOG.md>`_ for details.

License
#######

This package is released under the MIT license.  See `LICENSE <https://github.com/bilardi/aws-saving/blob/master/LICENSE>`_ for details.
