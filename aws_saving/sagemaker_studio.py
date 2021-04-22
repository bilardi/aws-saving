"""The class extends the class named Service and it manages the saving for the Amazon SageMaker Studio service

The class accepts a dict with the follow properties:
    'force' (list): list of services identifier that they have to be forced for deleting
    'timezone' (str): Timezone string name, default is Etc/GMT

Here's an example:

    >>> import aws_saving.sagemaker.studio as mainClass
    >>> arguments = {}
    >>> arguments['force'] = ['i-01234567890']
    >>> arguments['timezone'] = ['Europe/Rome']
    >>> saving = mainClass.Studio(arguments)
    >>> saving.run(arguments)

# license MIT
# author Alessandra Bilardi <alessandra.bilardi@gmail.com>
# see https://github.com/bilardi/aws-saving for details
"""

import boto3
from botocore.exceptions import ClientError
from .service import Service

class SagemakerStudio(Service):
    sagemaker = None
    date_tuple = None

    def __init__(self, event):
        self.sagemaker = boto3.client('sagemaker')
        Service.__init__(self, event)

    def get_instances(self):
        """
        gets the sagemaker studio details
            Returns:
                A dictionary of the domain instances details
            Raise:
                ClientError of botocore.exceptions
        """
        instances_list = self.sagemaker.list_domains()
        instances = []
        for instance in instances_list['Domains']:
            if instance['Status'].lower() != 'deleting':
                tag_list = self.sagemaker.list_tags(ResourceArn=instance['DomainArn'])
                saving = self.get_value(tag_list['Tags'], 'saving')
                if saving and saving.lower() == 'enabled':
                    instance['Tags'] = tag_list['Tags']
                    instances.append(instance)
        return instances

    def really_delete_server(self, even_jupyter_server, app_type):
        """
        checks if really it has to delete that app type
            Args:
                even_jupyter_server (boolean): if True, it also deletes app with type JupyterServer
                app_type (string): app type among JupyterServer, KernelGateway, TensorBoard
            Returns:
                A boolean True if it has to be deleted
        """
        if even_jupyter_server == True:
            return True
        elif app_type == 'JupyterServer':
            return False
        return True

    def delete_apps(self, domain_id, user_profile_name, even_jupyter_server = False):
        """
        deletes the apps
            Args:
                domain_id (string): the domain identifier
                user_profile_name (string): the user profile name
                even_jupyter_server (boolean): if True, it also deletes app with type JupyterServer 
        """
        app_list = self.sagemaker.list_apps(DomainIdEquals=domain_id, UserProfileNameEquals=user_profile_name)
        for app in app_list['Apps']:
            if app['Status'] not in ['Deleted','Deleting'] and self.really_delete_server(even_jupyter_server, app['AppType']):
                print('Deleting app named ' + app['AppName'])
                self.sagemaker.delete_app(
                    DomainId=domain_id,
                    UserProfileName=user_profile_name,
                    AppType=app['AppType'],
                    AppName=app['AppName']
                )

    def stop_apps(self, domain_id):
        """
        deletes the apps except those with type JupyterServer
            Args:
                domain_id (string): the domain identifier
        """
        user_profile_list = self.sagemaker.list_user_profiles(DomainIdEquals=domain_id)
        for user_profile in user_profile_list['UserProfiles']:
            if user_profile['Status'] not in ['Deleting']:
                print('Deleting all objects of ' + user_profile['UserProfileName'])
                self.delete_apps(domain_id, user_profile['UserProfileName'])

    def empty_user_profile(self, user_profile_id, even_jupyter_server = False):
        """
        empties the user profile
            Args:
                user_profile_id (string): the user profile identifier
                even_jupyter_server (boolean): if True, it also deletes app with type JupyterServer 
        """
        [user_profile_name, domain_id] = user_profile_id.split('|')
        print('Deleting all objects of ' + user_profile_id)
        self.delete_apps(domain_id, user_profile_name, even_jupyter_server)

    def delete_user_profiles(self, domain_id):
        """
        deletes the user profiles of a domain
            Args:
                domain_id (string): the domain identifier
        """
        user_profile_list = self.sagemaker.list_user_profiles(DomainIdEquals=domain_id)
        for user_profile in user_profile_list['UserProfiles']:
            print('Deleting user profile named ' + user_profile['UserProfileName'])
            if user_profile['Status'] not in ['Deleting']:
                self.delete_apps(domain_id, user_profile['UserProfileName'], True)
                self.sagemaker.delete_user_profile(
                    DomainId=domain_id,
                    UserProfileName=user_profile['UserProfileName']
                )

    def already_exists(self, domain_id):
        """
        checks if the domain exists
            Args:
                domain_id (string): the domain identifier
            Returns:
                A boolean True if it exists
        """
        try:
            instance = self.sagemaker.describe_domain(DomainId=domain_id)
            if not instance or instance['Status'] in ['Deleting']:
                raise ValueError
            else:
                return True
        except:
            print('The domain ' + str(domain_id) + ' not exists')
        return False

    def empty_domain(self, domain_id):
        """
        empties the domain before the deleting
            Args:
                domain_id (string): the domain identifier
        """
        if self.already_exists(domain_id):
            print('Deleting all objects of ' + domain_id)
            self.delete_user_profiles(domain_id)

    def run(self, event):
        """
        runs the schedulation
            Args:
                event (dictionary): aws details
                    'force' (list): list of services identifier that they have to be forced for deleting
        """
        instances = self.get_instances()
        for instance in instances:
            print(instance['DomainName'])
            if self.is_time_to_act(instance['Tags'], 'delete'):
                self.empty_domain(instance['DomainId'])
                try:
                    print('Deleting ' + instance['DomainName'])
                    retention_policy = 'Retain'
                    if self.is_to_be_deleted(event, instance, 'DomainId', 'Status', 'InService'):
                        retention_policy = 'Delete'
                    self.sagemaker.delete_domain(
                        DomainId=instance['DomainId'],
                        RetentionPolicy={'HomeEfsFileSystem': retention_policy}
                    )
                except:
                    print('Warning: domain named ' + instance['DomainName'] + ' is not empty, you have to force for deleting it')
            if self.is_time_to_act(instance['Tags'], 'stop'):
                self.stop_apps(instance['DomainId'])

def main(event, context):
    saving = Studio(event)
    saving.run(event)

if __name__ == '__main__':
    main([], None)
