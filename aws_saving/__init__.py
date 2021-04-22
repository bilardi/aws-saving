"""AWS saving package

This package contains the modules for managing your services timelife and costs.
The package works if you have added some tags on your objects:
see the documentation on https://aws-saving.readthedocs.io/en/latest/

It is part of the educational repositories (https://github.com/pandle/materials)
to learn how to write stardard code and common uses of the TDD.

Package contents two main classes: Saving, the main class, and Service,
the class extended by each class that implements an AWS service.

    >>> import aws_saving
    >>> help(aws_saving)
    >>> import aws_saving.saving as Saving
    >>> help(Saving)

# license MIT
# support https://github.com/bilardi/aws-saving/issues
"""
__version__ = '1.1.0'
__author__ = 'Alessandra Bilardi'
