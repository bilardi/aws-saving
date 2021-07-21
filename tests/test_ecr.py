import unittest
import json
import datetime
from botocore.exceptions import ClientError
import tests.helper as hlp
from aws_saving.ecr import Ecr

class EcrClient():
    drs = None
    ltfr = None
    dr = None
    es = False
    ne = False
    net = False
    def __init__(self):
        with open('tests/ecr-describe-repositories.json') as json_file:
            self.drs = json.load(json_file)
        with open('tests/ecr-list-tags-for-resource.json') as json_file:
            self.ltfr = json.load(json_file)
        with open('tests/ecr-delete-repository.json') as json_file:
            self.dr = json.load(json_file)
    def describe_repositories(self, repositoryNames=''):
        if repositoryNames and isinstance(repositoryNames, str):
            if self.ne is False:
                return True
            raise ValueError
        else:
            return self.drs 
    def list_tags_for_resource(self, resourceArn):
        if isinstance(resourceArn, str) and self.net is False:
            return self.ltfr
        return {}
    def set_except_simulation(self, boolean):
        self.es = boolean
    def set_not_exists_simulation(self, boolean):
        self.ne = boolean
    def set_not_exists_tag_simulation(self, boolean):
        self.net = boolean
    def delete_repository(self, repositoryName, force=False):
        if isinstance(repositoryName, str) and isinstance(force, bool) and self.es is False:
            return
        raise ValueError

class TestService(unittest.TestCase, Ecr):
    s = None

    def __init__(self, *args, **kwargs):
        self.s = Ecr({})
        self.s.ecr = EcrClient()
        unittest.TestCase.__init__(self, *args, **kwargs)

    def get_output(self, event = {}):
        with hlp.captured_output() as (out, err):
            self.s.run(event)
        return out.getvalue().strip()

    def test_get_instances(self):
        instances = self.s.get_instances()
        self.assertEqual(instances[0]['repositoryName'], 'mlops-studio-processing')

    def test_get_instances_exception(self):
        self.s.ecr.set_not_exists_tag_simulation(True)
        instances = self.s.get_instances()
        self.assertEqual(instances, [])
        self.s.ecr.set_not_exists_tag_simulation(False)
        instances = self.s.get_instances()
        self.assertTrue('Tags' in instances[0])

    def test_already_exists(self):
        self.s.ecr.set_not_exists_simulation(False)
        self.assertTrue(self.s.already_exists('mlops-studio-processing'))
        self.s.ecr.set_not_exists_simulation(True)
        with hlp.captured_output() as (out, err):
            self.assertFalse(self.s.already_exists('mlops-studio-processing'))
        self.assertEqual(out.getvalue().strip(), "The repository named mlops-studio-processing not exists")

    def test_run(self):
        now = datetime.datetime.now()
        
        self.s.ecr.set_except_simulation(False)
        test = now.replace(hour=8, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "mlops-studio-processing")
        self.assertEqual(self.get_output({"force":["mlops-studio-processing"]}), "mlops-studio-processing")
        test = now.replace(hour=18, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "mlops-studio-processing\nDeleting mlops-studio-processing")
        self.assertEqual(self.get_output({"force":["mlops-studio-processing"]}), "mlops-studio-processing\nDeleting mlops-studio-processing")

        self.s.ecr.set_except_simulation(True)
        test = now.replace(hour=8, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "mlops-studio-processing")
        self.assertEqual(self.get_output({"force":["mlops-studio-processing"]}), "mlops-studio-processing")
        test = now.replace(hour=18, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "mlops-studio-processing\nDeleting mlops-studio-processing\nWarning: repository named mlops-studio-processing is not empty, you have to force for deleting it")
        self.assertEqual(self.get_output({"force":["mlops-studio-processing"]}), "mlops-studio-processing\nDeleting mlops-studio-processing\nWarning: repository named mlops-studio-processing is not empty, you have to force for deleting it")

if __name__ == '__main__':
    unittest.main()