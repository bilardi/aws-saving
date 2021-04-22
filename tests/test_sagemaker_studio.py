import unittest
import json
import datetime
from botocore.exceptions import ClientError
import tests.helper as hlp
from aws_saving.sagemaker_studio import SagemakerStudio

class SagemakerClient():
    ld = None
    lup = None
    la = None
    lt = None
    ddd = None
    ddi = None
    es = False
    ne = False
    net = False
    policy = None
    def __init__(self):
        with open('tests/sagemaker-studio-list-domains.json') as json_file:
            self.ld = json.load(json_file)
        with open('tests/sagemaker-studio-list-user-profiles.json') as json_file:
            self.lup = json.load(json_file)
        with open('tests/sagemaker-studio-list-apps.json') as json_file:
            self.la = json.load(json_file)
        with open('tests/sagemaker-studio-list-tags.json') as json_file:
            self.lt = json.load(json_file)
        with open('tests/sagemaker-studio-describe-domain.Deleting.json') as json_file:
            self.ddd = json.load(json_file)
        with open('tests/sagemaker-studio-describe-domain.InService.json') as json_file:
            self.ddi = json.load(json_file)
    def list_domains(self):
        return self.ld
    def list_user_profiles(self, DomainIdEquals):
        if isinstance(DomainIdEquals, str):
            return self.lup
        raise ValueError
    def list_apps(self, DomainIdEquals, UserProfileNameEquals):
        if isinstance(DomainIdEquals, str) and isinstance(UserProfileNameEquals, str):
            return self.la
        raise ValueError
    def list_tags(self, ResourceArn):
        if isinstance(ResourceArn, str):
            if self.net is True:
                return {"Tags":[]}
            return self.lt
        raise ValueError
    def describe_domain(self, DomainId):
        if DomainId == 1:
            return {}
        if self.ne is False:
            return self.ddi
        return self.ddd
    def set_except_simulation(self, boolean):
        self.es = boolean
    def set_not_exists_simulation(self, boolean):
        self.ne = boolean
    def set_not_exists_tag_simulation(self, boolean):
        self.net = boolean
    def set_policy_none(self):
        self.policy = None
    def delete_app(self, DomainId, UserProfileName, AppType, AppName):
        if isinstance(DomainId, str) and isinstance(UserProfileName, str) and isinstance(AppType, str) and isinstance(AppName, str):
            return
        raise ValueError
    def delete_user_profile(self, DomainId, UserProfileName):
        if isinstance(DomainId, str) and isinstance(UserProfileName, str):
            return
        raise ValueError
    def delete_domain(self, DomainId, RetentionPolicy):
        if isinstance(DomainId, str) and isinstance(RetentionPolicy, dict) and self.es is False:
            self.policy = RetentionPolicy['HomeEfsFileSystem']
            return
        raise ValueError

class TestService(unittest.TestCase, SagemakerStudio):
    s = None

    def __init__(self, *args, **kwargs):
        self.s = SagemakerStudio({})
        self.s.sagemaker = SagemakerClient()
        unittest.TestCase.__init__(self, *args, **kwargs)

    def get_output(self, event = {}):
        with hlp.captured_output() as (out, err):
            self.s.run(event)
        return out.getvalue().strip()

    def test_get_instances(self):
        instances = self.s.get_instances()
        self.assertEqual(instances[0]['DomainName'], 'studio')

    def test_get_instances_exception(self):
        self.s.sagemaker.set_not_exists_tag_simulation(True)
        instances = self.s.get_instances()
        self.s.sagemaker.set_not_exists_tag_simulation(False)
        self.assertEqual(instances, [])

    def test_already_exists(self):
        self.s.sagemaker.set_not_exists_simulation(False)
        self.assertTrue(self.s.already_exists('id'))
        self.s.sagemaker.set_not_exists_simulation(True)
        with hlp.captured_output() as (out, err):
            self.assertFalse(self.s.already_exists('domain-id'))
        self.assertEqual(out.getvalue().strip(), "The domain domain-id not exists")

    def test_empty_user_profile(self):
        with hlp.captured_output() as (out, err):
            self.s.empty_user_profile('user|id')
        self.assertEqual(out.getvalue().strip(), "Deleting all objects of user|id\nDeleting app named datascience")
        with hlp.captured_output() as (out, err):
            self.s.empty_user_profile('user|id', False)
        self.assertEqual(out.getvalue().strip(), "Deleting all objects of user|id\nDeleting app named datascience")
        with hlp.captured_output() as (out, err):
            self.s.empty_user_profile('user|id', True)
        self.assertEqual(out.getvalue().strip(), "Deleting all objects of user|id\nDeleting app named default\nDeleting app named datascience")
        with self.assertRaises(ValueError):
            self.s.empty_user_profile('user')

    def test_empty_domain(self):
        with hlp.captured_output() as (out, err):
            self.s.empty_domain('id')
        self.assertEqual(out.getvalue().strip(), "Deleting all objects of id\nDeleting user profile named user\nDeleting app named default\nDeleting app named datascience")
        with hlp.captured_output() as (out, err):
            self.s.empty_domain(1)
        self.assertEqual(out.getvalue().strip(), "The domain 1 not exists")

    def test_stop_apps(self):
        with hlp.captured_output() as (out, err):
            self.s.stop_apps('id')
        self.assertEqual(out.getvalue().strip(), "Deleting all objects of user\nDeleting app named datascience")

    def test_run(self):
        now = datetime.datetime.now()
        
        self.s.sagemaker.lt['Tags'][0]['Key'] = 'Stop'
        self.s.sagemaker.set_policy_none()

        self.s.sagemaker.set_except_simulation(False)
        test = now.replace(hour=8, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "studio")
        self.assertEqual(self.s.sagemaker.policy, None)
        self.assertEqual(self.get_output({"force":["id"]}), "studio")
        self.assertEqual(self.s.sagemaker.policy, None)
        test = now.replace(hour=18, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "studio\nDeleting all objects of user\nDeleting app named datascience")
        self.assertEqual(self.s.sagemaker.policy, None)
        self.assertEqual(self.get_output({"force":["id"]}), "studio\nDeleting all objects of user\nDeleting app named datascience")
        self.assertEqual(self.s.sagemaker.policy, None)

        self.s.sagemaker.set_policy_none()

        self.s.sagemaker.set_except_simulation(True)
        test = now.replace(hour=8, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "studio")
        self.assertEqual(self.s.sagemaker.policy, None)
        self.assertEqual(self.get_output({"force":["id"]}), "studio")
        self.assertEqual(self.s.sagemaker.policy, None)
        test = now.replace(hour=18, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "studio\nDeleting all objects of user\nDeleting app named datascience")
        self.assertEqual(self.s.sagemaker.policy, None)
        self.assertEqual(self.get_output({"force":["id"]}), "studio\nDeleting all objects of user\nDeleting app named datascience")
        self.assertEqual(self.s.sagemaker.policy, None)

        self.s.sagemaker.lt['Tags'][0]['Key'] = 'Delete'
        self.s.sagemaker.set_policy_none()

        self.s.sagemaker.set_except_simulation(False)
        test = now.replace(hour=8, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "studio")
        self.assertEqual(self.s.sagemaker.policy, None)
        self.assertEqual(self.get_output({"force":["id"]}), "studio")
        self.assertEqual(self.s.sagemaker.policy, None)
        test = now.replace(hour=18, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "studio\nDeleting all objects of id\nDeleting user profile named user\nDeleting app named default\nDeleting app named datascience\nDeleting studio")
        self.assertEqual(self.s.sagemaker.policy, 'Retain')
        self.assertEqual(self.get_output({"force":["id"]}), "studio\nDeleting all objects of id\nDeleting user profile named user\nDeleting app named default\nDeleting app named datascience\nDeleting studio")
        self.assertEqual(self.s.sagemaker.policy, 'Delete')

        self.s.sagemaker.set_policy_none()

        self.s.sagemaker.set_except_simulation(True)
        test = now.replace(hour=8, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "studio")
        self.assertEqual(self.s.sagemaker.policy, None)
        self.assertEqual(self.get_output({"force":["id"]}), "studio")
        self.assertEqual(self.s.sagemaker.policy, None)
        test = now.replace(hour=18, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "studio\nDeleting all objects of id\nDeleting user profile named user\nDeleting app named default\nDeleting app named datascience\nDeleting studio\nWarning: domain named studio is not empty, you have to force for deleting it")
        self.assertEqual(self.s.sagemaker.policy, None)
        self.assertEqual(self.get_output({"force":["id"]}), "studio\nDeleting all objects of id\nDeleting user profile named user\nDeleting app named default\nDeleting app named datascience\nDeleting studio\nWarning: domain named studio is not empty, you have to force for deleting it")
        self.assertEqual(self.s.sagemaker.policy, None)

# Apps, "Status": "Deleted"|"Deleting"|"Failed"|"InService"|"Pending"
# Domain and User, "Status": "Deleting"|"Failed"|"InService"|"Pending"|"Updating"|"Update_Failed"|"Delete_Failed",

if __name__ == '__main__':
    unittest.main()