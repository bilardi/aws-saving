"""The class extends the class named Service and it manages the saving for the Amazon Elastic Container Registry service

The class accepts a dict with the follow properties:
    'force' (list): list of services identifier that they have to be forced for deleting
    'timezone' (str): Timezone string name, default is Etc/GMT

Here's an example:

    >>> import aws_saving.ecr as mainClass
    >>> arguments = {}
    >>> arguments['force'] = ['i-01234567890']
    >>> arguments['timezone'] = ['Europe/Rome']
    >>> saving = mainClass.ECR(arguments)
    >>> saving.run(arguments)

# license MIT
# author Alessandra Bilardi <alessandra.bilardi@gmail.com>
# see https://github.com/bilardi/aws-saving for details
"""

import boto3
from botocore.exceptions import ClientError
from .service import Service

class Ecr(Service):
    ecr = None
    date_tuple = None

    def __init__(self, event):
        self.ecr = boto3.client('ecr')
        Service.__init__(self, event)

    def get_instances(self):
        """
        gets the ecr details
            Returns:
                A dictionary of the ecr instances details
        """
        instances_list = self.ecr.describe_repositories()
        instances = []
        for instance in instances_list['repositories']:
            tag_list = self.ecr.list_tags_for_resource(resourceArn=instance['repositoryArn'])
            if 'tags' in tag_list:
                saving = self.get_value(tag_list['tags'], 'saving')
                if saving and saving.lower() == 'enabled':
                    instance['Tags'] = tag_list['tags']
                    instances.append(instance)
        return instances

    def already_exists(self, name):
        """
        checks if the repository exists
            Args:
                name (string): the repository name
            Returns:
                A boolean True if it exists
        """
        try:
            if self.ecr.describe_repositories(repositoryNames=name):
                return True
        except:
            print('The repository named ' + str(name) + ' not exists')
        return False

    def delete_repository(self, name):
        """
        deletes the repository with also its images
            Args:
                name (string): the repository name
        """
        self.ecr.delete_repository(repositoryName=name, force=True)

    def run(self, event):
        """
        runs the schedulation
            Args:
                event (dictionary): aws details
                    'force' (list): list of services identifier that they have to be forced for deleting
        """
        instances = self.get_instances()
        for instance in instances:
            print(instance['repositoryName'])
            if self.is_time_to_act(instance['Tags'], 'delete'):
                try:
                    print('Deleting ' + instance['repositoryName'])
                    if self.is_to_be_deleted(event, instance, 'repositoryName', 'DeletionProtection', False):
                        self.ecr.delete_repository(repositoryName=instance['repositoryName'], force=True)
                    else:
                        self.ecr.delete_repository(repositoryName=instance['repositoryName'])
                except:
                    print('Warning: repository named ' + instance['repositoryName'] + ' is not empty, you have to force for deleting it')

def main(event, context):
    saving = Ecr(event)
    saving.run(event)

if __name__ == '__main__':
    main([], None)
