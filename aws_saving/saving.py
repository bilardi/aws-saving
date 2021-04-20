"""The main class for managing your saving

The class accepts a dict with the follow properties:
    'force' (list): list of services identifier that they have to be forced for deleting
    'invoke_lambda' (bool): if True, then invoke one lambda for each service
    'services_name' (list): list of services name
    'timezone' (str): Timezone string name, default is Etc/GMT

Only the last property, 'services_name', it is mandatory. Here's an example:

    >>> import aws_saving.saving as mainClass
    >>> arguments = {}
    >>> arguments['force'] = ['i-01234567890']
    >>> arguments['invoke_lambda'] = False
    >>> arguments['services_name'] = ['ec2']
    >>> arguments['timezone'] = ['Europe/Rome']
    >>> saving = mainClass.Saving(arguments)
    >>> saving.run(arguments)

# license MIT
# author Alessandra Bilardi <alessandra.bilardi@gmail.com>
# see https://github.com/bilardi/aws-saving for details
"""

import json
import boto3
import importlib

class Saving():
    lambda_client = None
    services_name = None

    def __init__(self, event):
        """
        initializes variables
            Args:
                event (list): aws details
                    'services_name' (list): list of services name
                    'invoke_lambda' (bool): if True, then invoke one lambda for each service
        """
        if 'invoke_lambda' in event and event['invoke_lambda'] is True:
            self.lambda_client = boto3.client('lambda')
        self.services_name = event['services_name']


    def get_services_name(self):
        """
        gets the services name saved from services_name element
            Returns:
                List of services name
        """
        return self.services_name

    def print_service_log(self, service_name):
        """
        prints the log message
            Args:
                service_name (string): Name of the service
        """
        print('Running AWS saving on {} service'.format(service_name.upper()))

    def underscore_to_camel_case_capitalized(self, string):
        """
        converts a string of words with underscore like delimiter in camel case capitalized
            Args:
                string (string): String that it could contain underscore
            Returns:
                A CamelCase string capitalized
        """
        first_word, *words = string.split('_')
        return first_word.capitalize() + ''.join(word.capitalize() for word in words)

    def run_services(self, event):
        """
        runs the schedulation for each service implemented
            Args:
                event (list): aws details
                    'force' (list): list of services identifier that they have to be forced for deleting
                    'timezone' (str): Timezone string name, default is Etc/GMT
        """
        for service_name in self.services_name:
            self.print_service_log(service_name)
            load_module = importlib.import_module('aws_saving.' + service_name)
            service_class = getattr(load_module, self.underscore_to_camel_case_capitalized(service_name))
            service = service_class(event)
            service.run(event)

    def invoke_lambdas(self, event):
        """
        runs the schedulation for each service implemented
            Args:
                event (list): aws details
                    'force' (list): list of services identifier that they have to be forced for deleting
                    'timezone' (str): Timezone string name, default is Etc/GMT
        """
        for service_name in self.services_name:
            self.print_service_log(service_name)
            print(
                self.lambda_client.invoke(
                    FunctionName='string',
                    InvocationType='Event', #|'RequestResponse'|'DryRun',
                    Payload=json.dumps(event)
                )
            )

    def run(self, event):
        """
        runs the schedulation for each service implemented
            Args:
                event (list): aws details
                    'force' (list): list of services identifier that they have to be forced for deleting
                    'invoke_lambda' (bool): if True, then invoke one lambda for each service
                    'timezone' (str): Timezone string name, default is Etc/GMT
        """
        print(self.get_services_name())
        if 'invoke_lambda' in event and event['invoke_lambda'] is True:
            self.invoke_lambdas(event)
        else:
            self.run_services(event)

def main(event, context):
    saving = Saving(event)
    saving.run(event)

if __name__ == '__main__':
    main([], None)
