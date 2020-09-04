"""The class extends the class named Service and it manages the saving for the Amazon S3 service

The class accepts a dict with the follow properties:
    'force' (list): list of services identifier that they have to be forced for deleting
    'timezone' (str): Timezone string name, default is Etc/GMT

Here's an example:

    >>> import aws_saving.s3 as mainClass
    >>> arguments = {}
    >>> arguments['force'] = ['i-01234567890']
    >>> arguments['timezone'] = ['Europe/Rome']
    >>> saving = mainClass.S3(arguments)
    >>> saving.run(arguments)

# license MIT
# author Alessandra Bilardi <alessandra.bilardi@gmail.com>
# see https://github.com/bilardi/aws-saving for details
"""

import boto3
from botocore.exceptions import ClientError
from .service import Service

class S3(Service):
    s3 = None
    s3r = None
    date_tuple = None

    def __init__(self, event):
        self.s3 = boto3.client('s3')
        self.s3r = boto3.resource('s3')
        Service.__init__(self, event)

    def get_instances(self):
        """
        gets the s3 details
            Returns:
                A dictionary of the s3 instances details
            Raise:
                ClientError of botocore.exceptions
        """
        instances_list = self.s3.list_buckets()
        instances = []
        for instance in instances_list['Buckets']:
            try:
                tag_list = self.s3.get_bucket_tagging(Bucket=instance['Name'])
            except ClientError as error:
                if error.response['Error']['Code'] == 'NoSuchTagSet':
                    continue # No tags
                else:
                    raise error
            saving = self.get_value(tag_list['TagSet'], 'saving')
            if saving and saving.lower() == 'enabled':
                instance['DeletionProtection'] = True
                instance['Tags'] = tag_list['TagSet']
                instances.append(instance)
        return instances

    def already_exists(self, name):
        """
        checks if the bucket exists
            Args:
                name (string): the bucket name
            Returns:
                A boolean True if it exists
        """
        try:
            if self.s3.head_bucket(Bucket=name):
                return True
        except:
            print('The bucket named ' + str(name) + ' not exists')
        return False

    def empty_bucket(self, name):
        """
        empties the bucket before the deleting
            Args:
                name (string): the bucket name
        """
        if self.already_exists(name):
            print('Deleting all objects of ' + name)
            bucket = self.s3r.Bucket(name)
            bucket.objects.all().delete()
            # bucket.delete() # only empty bucket

    def run(self, event):
        """
        runs the schedulation
            Args:
                event (dictionary): aws details
                    'force' (list): list of services identifier that they have to be forced for deleting
        """
        instances = self.get_instances()
        for instance in instances:
            print(instance['Name'])
            if self.is_time_to_act(instance['Tags'], 'delete'):
                if self.is_to_be_deleted(event, instance, 'Name', 'DeletionProtection', False):
                    self.empty_bucket(instance['Name'])
                try:
                    print('Deleting ' + instance['Name'])
                    self.s3.delete_bucket(Bucket=instance['Name'])
                except:
                    print('Warning: bucket named ' + instance['Name'] + ' is not empty, you have to force for deleting it')

def main(event, context):
    saving = S3(event)
    saving.run(event)

if __name__ == '__main__':
    main([], None)
