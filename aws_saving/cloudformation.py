"""The class extends the class named Service and it manages the saving for the AWS Cloudformation service

The class accepts a dict with the follow properties:
    'force' (list): list of services identifier that they have to be forced for deleting
    'timezone' (str): Timezone string name, default is Etc/GMT

Here's an example:

    >>> import aws_saving.cloudformation as mainClass
    >>> arguments = {}
    >>> arguments['force'] = ['stack-name']
    >>> arguments['timezone'] = ['Europe/Rome']
    >>> saving = mainclass.Cloudformation(arguments)
    >>> saving.run(arguments)

# license MIT
# author Alessandra Bilardi <alessandra.bilardi@gmail.com>
# see https://github.com/bilardi/aws-saving for details
"""

import boto3
from .service import Service
from .s3 import S3
from .rds import Rds
from .sagemaker_studio import SagemakerStudio

class Cloudformation(Service):
    stack = None
    s3 = None
    rds = None
    sagemaker_studio = None
    date_tuple = None

    def __init__(self, event):
        self.stack = boto3.client('cloudformation')
        self.s3 = S3(event)
        self.rds = Rds(event)
        self.sagemaker_studio = SagemakerStudio(event)
        Service.__init__(self, event)

    def get_instances(self):
        """
        gets the stack details
            Returns:
                A dictionary of the stack instances details
        """
        instances_list = self.stack.describe_stacks()
        instances = []
        for instance in instances_list['Stacks']:
            resources_list = self.stack.list_stack_resources(StackName=instance['StackName'])
            saving = self.get_value(instance['Tags'], 'saving')
            if saving and saving.lower() == 'enabled':
                instance['Resources'] = resources_list['StackResourceSummaries']
                instances.append(instance)
        return instances

    def get_that_resourses_type(self, resources, ResourceType):
        """
        gets the resources with that resource type
            Args:
                resources (list): list of dictionaries, each dictionary contains the details of a resource 
                ResourceType (string): type of resource
            Returns:
                A list of physical resource id with that resource type
        """
        instances = []
        for resource in resources:
            if resource['ResourceType'] == ResourceType:
                instances.append(resource['PhysicalResourceId'])
        return instances

    def get_not_existent_resources(self, resources):
        """
        gets the resources that they do not exist anymore
            Args:
                resources (list): list of dictionaries, each dictionary contains the details of a resource 
            Returns:
                A list of physical resource id that they do not exist anymore
        """
        instances = []
        rds_instance_types = ['AWS::RDS::DBCluster', 'AWS::RDS::DBInstance']
        for resource in resources:
            if resource['ResourceType'] == 'AWS::S3::Bucket' and self.s3.already_exists(resource['PhysicalResourceId']) is False:
                instances.append(resource['PhysicalResourceId'])
            if resource['ResourceType'] in rds_instance_types and self.rds.already_exists(resource['PhysicalResourceId']) is False:
                instances.append(resource['PhysicalResourceId'])
        return instances

    def empty_buckets(self, buckets):
        """
        empties the buckets before the deleting
            Args:
                buckets (list): list of buckets name
        """
        for bucket in buckets:
            self.s3.empty_bucket(bucket)

    def empty_sagemaker_domains(self, domains):
        """
        empties the SageMaker domains before the deleting
            Args:
                domains (list): list of domains name
        """
        for domain in domains:
            self.sagemaker_studio.empty_domain(domain)

    def empty_sagemaker_user_profile(self, user_profiles, even_jupyter_server = False):
        """
        empties the SageMaker user profiles before the deleting
            Args:
                user_profiles (list): list of user profiles name
                even_jupyter_server (boolean): if True, it also deletes app with type JupyterServer 
        """
        for user_profile in user_profiles:
            self.sagemaker_studio.empty_user_profile(user_profile, even_jupyter_server)

    def empty_resources(self, instance):
        """
        empties the resources before the deleting
            Args:
                instance (dictionary): instance details
        """
        self.empty_buckets(self.get_that_resourses_type(instance['Resources'], 'AWS::S3::Bucket'))
        self.empty_sagemaker_domains(self.get_that_resourses_type(instance['Resources'], 'AWS::SageMaker::Domain'))
        self.empty_sagemaker_user_profile(self.get_that_resourses_type(instance['Resources'], 'AWS::SageMaker::UserProfile'), True)

    def run(self, event):
        """
        runs the schedulation
            Args:
                event (dictionary): aws details
                    'force' (list): list of services identifier that they have to be forced for deleting
        """
        instances = self.get_instances()
        for instance in instances:
            print(instance['StackName'])
            if self.is_time_to_act(instance['Tags'], 'delete') and not instance['StackStatus'].startswith('DELETE') and not instance['StackStatus'].endswith('FAILED') and not instance['StackStatus'].endswith('IN_PROGRESS'):
                if self.is_to_be_deleted(event, instance, 'StackName', 'EnableTerminationProtection', False):
                    if 'EnableTerminationProtection' in instance and instance['EnableTerminationProtection'] is True:
                        self.stack.update_termination_protection(EnableTerminationProtection=False, StackName=instance['StackName'])
                        print('Disabled Termination for ' + instance['StackName'])
                    self.empty_resources(instance)
                    print('Deleting ' + instance['StackName'])
                    self.stack.delete_stack(StackName=instance['StackName'])
                else:
                    print('Warning: modify the EnableTerminationProtection value to false for deleting ' + instance['StackName'])
            elif self.is_time_to_act(instance['Tags'], 'delete'):
                print('Warning: the StackStatus named ' + instance['StackStatus'] + ' is not managed')
                # TODO: RetainResources works only with resources with StackStatus != 'DELETE_COMPLETED', so missing a SkipResources property
                not_existent_resources = self.get_not_existent_resources(instance['Resources'])
                if not_existent_resources:
                    print('You have to skip manually those resources for deleting the stack:')
                    print(not_existent_resources)
                # if instance['StackStatus'] == 'DELETE_FAILED':
                #     self.stack.delete_stack(StackName=instance['StackName'], RetainResources=not_existent_resources)
            if self.is_time_to_act(instance['Tags'], 'stop'):
                # exception because sagemaker user profile is missing of tags
                non_taggable_resources = self.get_that_resourses_type(instance['Resources'], 'AWS::SageMaker::UserProfile')
                if non_taggable_resources:
                    print('Management of the stop of all non taggable resources of ' + instance['StackName'])
                    self.empty_sagemaker_user_profile(non_taggable_resources)

def main(event, context):
    saving = Cloudformation(event)
    saving.run(event)

if __name__ == '__main__':
    main([], None)
