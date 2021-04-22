import unittest
import json
import datetime
import tests.helper as hlp
from aws_saving.cloudformation import Cloudformation

class CloudformationClient():
    resources = ['aurora','bucket','ec2','sagemaker-domain','sagemaker-user-profile']
    resources_type = ['AWS::RDS::DBCluster','AWS::S3::Bucket','AWS::EC2::Instance','AWS::SageMaker::Domain','AWS::SageMaker::UserProfile']
    resources_id = ['aurora','bucket','i-01234567890','d-abcdefghijkl','user|d-abcdefghijkl']
    ds = None
    lsr = {}
    def __init__(self):
        with open('tests/cloudformation-describe-stacks.json') as json_file:
            self.ds = json.load(json_file)
        for resource in self.resources:
            with open('tests/cloudformation-list-stack-resources.' + resource + '.json') as json_file:
                self.lsr[resource] = json.load(json_file)
    def describe_stacks(self):
        return self.ds
    def list_stack_resources(self, StackName):
        if isinstance(StackName, str):
            return self.lsr[StackName]
        raise ValueError
    def update_termination_protection(self, EnableTerminationProtection, StackName):
        if isinstance(EnableTerminationProtection, bool) and isinstance(StackName, str):
            return
        raise ValueError
    def delete_stack(self, StackName):
        if isinstance(StackName, str):
            return
        raise ValueError

class S3():
    ne = False
    def empty_bucket(self, name):
        if isinstance(name, str):
            print('Deleting all resources of ' + name)
    def already_exists(self, name):
        if isinstance(name, str) and self.ne is False:
            return True
        if self.ne is True:
            return False
        raise ValueError
    def set_not_exists_simulation(self, boolean):
        self.ne = boolean

class Rds():
    ne = False
    def already_exists(self, name):
        if isinstance(name, str) and self.ne is False:
            return True
        if self.ne is True:
            return False
        raise ValueError
    def set_not_exists_simulation(self, boolean):
        self.ne = boolean

class SagemakerStudio():
    def empty_user_profile(self, name, even):
        if isinstance(name, str) and isinstance(even, bool):
            if even == True:
                print('Deleting all resources of ' + name)
            else:
                print('Deleting all resources of ' + name + ' except JupyterServer')
    def empty_domain(self, name):
        if isinstance(name, str):
            print('Deleting all resources of ' + name)

class TestService(unittest.TestCase, Cloudformation):
    s = None

    def __init__(self, *args, **kwargs):
        self.s = Cloudformation({})
        self.s.stack = CloudformationClient()
        self.s.s3 = S3()
        self.s.rds = Rds()
        self.s.sagemaker_studio = SagemakerStudio()
        unittest.TestCase.__init__(self, *args, **kwargs)

    def get_output(self, event = {}):
        with hlp.captured_output() as (out, err):
            self.s.run(event)
        return out.getvalue().strip()

    def test_get_instances(self):
        instances = self.s.get_instances()
        self.assertEqual(instances[0]['StackName'], 'aurora')
        self.assertEqual(instances[1]['StackName'], 'bucket')
        self.assertEqual(instances[2]['StackName'], 'ec2')

    def test_get_that_resourses_type(self):
        for resource in self.s.stack.resources:
            resources_list = self.s.stack.list_stack_resources(resource)
            resource_index = self.s.stack.resources.index(resource)
            resource_type = self.s.stack.resources_type[resource_index]
            resource_id = self.s.stack.resources_id[resource_index]
            self.assertEqual(self.s.get_that_resourses_type(resources_list['StackResourceSummaries'], resource_type), [resource_id])

    def test_get_not_existent_resources(self):
        self.s.s3.set_not_exists_simulation(False)
        resources_list = self.s.stack.list_stack_resources('bucket')
        self.assertEqual(self.s.get_not_existent_resources(resources_list['StackResourceSummaries']), [])
        self.s.s3.set_not_exists_simulation(True)
        self.assertEqual(self.s.get_not_existent_resources(resources_list['StackResourceSummaries']), ['bucket'])
        self.s.rds.set_not_exists_simulation(False)
        resources_list = self.s.stack.list_stack_resources('aurora')
        self.assertEqual(self.s.get_not_existent_resources(resources_list['StackResourceSummaries']), [])
        self.s.rds.set_not_exists_simulation(True)
        self.assertEqual(self.s.get_not_existent_resources(resources_list['StackResourceSummaries']), ['aurora', 'aurora-1', 'aurora-2'])

    def test_empty_buckets(self):
        with hlp.captured_output() as (out, err):
            self.s.empty_buckets(['bucket'])
        self.assertEqual(out.getvalue().strip(), "Deleting all resources of bucket")

    def test_empty_sagemaker_domains(self):
        with hlp.captured_output() as (out, err):
            self.s.empty_sagemaker_domains(['sagemaker-domain-id'])
        self.assertEqual(out.getvalue().strip(), "Deleting all resources of sagemaker-domain-id")

    def test_empty_sagemaker_user_profile(self):
        with hlp.captured_output() as (out, err):
            self.s.empty_sagemaker_user_profile(['sagemaker-user-profile-id'])
        self.assertEqual(out.getvalue().strip(), "Deleting all resources of sagemaker-user-profile-id except JupyterServer")
        with hlp.captured_output() as (out, err):
            self.s.empty_sagemaker_user_profile(['sagemaker-user-profile-id'], False)
        self.assertEqual(out.getvalue().strip(), "Deleting all resources of sagemaker-user-profile-id except JupyterServer")
        with hlp.captured_output() as (out, err):
            self.s.empty_sagemaker_user_profile(['sagemaker-user-profile-id'], True)
        self.assertEqual(out.getvalue().strip(), "Deleting all resources of sagemaker-user-profile-id")

    def test_run(self):
        now = datetime.datetime.now()

        for stack in self.s.stack.ds['Stacks']:
            stack['StackStatus'] = 'CREATE_COMPLETE'
        self.s.s3.set_not_exists_simulation(False)
        self.s.rds.set_not_exists_simulation(False)
        test = now.replace(hour=8, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "aurora\nbucket\nec2\nsagemaker-domain\nsagemaker-user-profile")
        self.assertEqual(self.get_output({"force":["aurora"]}), "aurora\nbucket\nec2\nsagemaker-domain\nsagemaker-user-profile")
        test = now.replace(hour=18, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "aurora\nWarning: modify the EnableTerminationProtection value to false for deleting aurora\nbucket\nDeleting all resources of bucket\nDeleting bucket\nec2\nDeleting ec2\nsagemaker-domain\nsagemaker-user-profile\nManagement of the stop of all non taggable resources of sagemaker-user-profile\nDeleting all resources of user|d-abcdefghijkl except JupyterServer")
        self.assertEqual(self.get_output({"force":["aurora"]}), "aurora\nDisabled Termination for aurora\nDeleting aurora\nbucket\nDeleting all resources of bucket\nDeleting bucket\nec2\nDeleting ec2\nsagemaker-domain\nsagemaker-user-profile\nManagement of the stop of all non taggable resources of sagemaker-user-profile\nDeleting all resources of user|d-abcdefghijkl except JupyterServer")

        for stack in self.s.stack.ds['Stacks']:
            stack['StackStatus'] = 'DELETE_IN_PROGRESS'
        self.s.s3.set_not_exists_simulation(False)
        self.s.rds.set_not_exists_simulation(False)
        test = now.replace(hour=18, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "aurora\nWarning: the StackStatus named DELETE_IN_PROGRESS is not managed\nbucket\nWarning: the StackStatus named DELETE_IN_PROGRESS is not managed\nec2\nWarning: the StackStatus named DELETE_IN_PROGRESS is not managed\nsagemaker-domain\nsagemaker-user-profile\nManagement of the stop of all non taggable resources of sagemaker-user-profile\nDeleting all resources of user|d-abcdefghijkl except JupyterServer")
        self.assertEqual(self.get_output({"force":["aurora"]}), "aurora\nWarning: the StackStatus named DELETE_IN_PROGRESS is not managed\nbucket\nWarning: the StackStatus named DELETE_IN_PROGRESS is not managed\nec2\nWarning: the StackStatus named DELETE_IN_PROGRESS is not managed\nsagemaker-domain\nsagemaker-user-profile\nManagement of the stop of all non taggable resources of sagemaker-user-profile\nDeleting all resources of user|d-abcdefghijkl except JupyterServer")

        for stack in self.s.stack.ds['Stacks']:
            stack['StackStatus'] = 'UPDATE_FAILED'
        self.s.s3.set_not_exists_simulation(False)
        self.s.rds.set_not_exists_simulation(False)
        test = now.replace(hour=18, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "aurora\nWarning: the StackStatus named UPDATE_FAILED is not managed\nbucket\nWarning: the StackStatus named UPDATE_FAILED is not managed\nec2\nWarning: the StackStatus named UPDATE_FAILED is not managed\nsagemaker-domain\nsagemaker-user-profile\nManagement of the stop of all non taggable resources of sagemaker-user-profile\nDeleting all resources of user|d-abcdefghijkl except JupyterServer")
        self.assertEqual(self.get_output({"force":["aurora"]}), "aurora\nWarning: the StackStatus named UPDATE_FAILED is not managed\nbucket\nWarning: the StackStatus named UPDATE_FAILED is not managed\nec2\nWarning: the StackStatus named UPDATE_FAILED is not managed\nsagemaker-domain\nsagemaker-user-profile\nManagement of the stop of all non taggable resources of sagemaker-user-profile\nDeleting all resources of user|d-abcdefghijkl except JupyterServer")

        for stack in self.s.stack.ds['Stacks']:
            stack['StackStatus'] = 'UPDATE_FAILED'
        self.s.s3.set_not_exists_simulation(True)
        self.s.rds.set_not_exists_simulation(True)
        test = now.replace(hour=18, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "aurora\nWarning: the StackStatus named UPDATE_FAILED is not managed\nYou have to skip manually those resources for deleting the stack:\n['aurora', 'aurora-1', 'aurora-2']\nbucket\nWarning: the StackStatus named UPDATE_FAILED is not managed\nYou have to skip manually those resources for deleting the stack:\n['bucket']\nec2\nWarning: the StackStatus named UPDATE_FAILED is not managed\nsagemaker-domain\nsagemaker-user-profile\nManagement of the stop of all non taggable resources of sagemaker-user-profile\nDeleting all resources of user|d-abcdefghijkl except JupyterServer")
        self.assertEqual(self.get_output({"force":["aurora"]}), "aurora\nWarning: the StackStatus named UPDATE_FAILED is not managed\nYou have to skip manually those resources for deleting the stack:\n['aurora', 'aurora-1', 'aurora-2']\nbucket\nWarning: the StackStatus named UPDATE_FAILED is not managed\nYou have to skip manually those resources for deleting the stack:\n['bucket']\nec2\nWarning: the StackStatus named UPDATE_FAILED is not managed\nsagemaker-domain\nsagemaker-user-profile\nManagement of the stop of all non taggable resources of sagemaker-user-profile\nDeleting all resources of user|d-abcdefghijkl except JupyterServer")

if __name__ == '__main__':
    unittest.main()
