import unittest
import json
import datetime
from botocore.exceptions import ClientError
import tests.helper as hlp
from aws_saving.s3 import S3

class S3Client():
    lb = None
    gbt = None
    gbteNoSuchTagSet = None
    es = False
    ne = False
    net = False
    def __init__(self):
        with open('tests/s3-list-buckets.json') as json_file:
            self.lb = json.load(json_file)
        with open('tests/s3-get-bucket-tagging.json') as json_file:
            self.gbt = json.load(json_file)
        with open('tests/s3-get-bucket-tagging.NoSuchTagSet.json') as json_file:
            self.gbteNoSuchTagSet = json.load(json_file)
    def list_buckets(self):
        return self.lb
    def head_bucket(self, Bucket):
        if isinstance(Bucket, str) and self.ne is False:
            return True
        raise ValueError
    def get_bucket_tagging(self, Bucket):
        if self.net is True:
            raise ClientError(self.gbteNoSuchTagSet, 'GetBucketTagging')
        elif isinstance(Bucket, str):
            return self.gbt
        raise ValueError
    def set_except_simulation(self, boolean):
        self.es = boolean
    def set_not_exists_simulation(self, boolean):
        self.ne = boolean
    def set_not_exists_tag_simulation(self, boolean):
        self.net = boolean
    def delete_bucket(self, Bucket):
        if isinstance(Bucket, str) and self.es is False:
            return
        raise ValueError

class S3Resource():
    objects = None
    def __init__(self):
        self.objects = S3Objects()
    def Bucket(self, Bucket):
        if isinstance(Bucket, str):
            return self
    def delete(self):
        return

class S3Objects():
    def all(self):
        return S3All()

class S3All():
    def delete(self):
        return

class TestService(unittest.TestCase, S3):
    s = None

    def __init__(self, *args, **kwargs):
        self.s = S3({})
        self.s.s3 = S3Client()
        self.s.s3r = S3Resource()
        unittest.TestCase.__init__(self, *args, **kwargs)

    def get_output(self, event = {}):
        with hlp.captured_output() as (out, err):
            self.s.run(event)
        return out.getvalue().strip()

    def test_get_instances(self):
        instances = self.s.get_instances()
        self.assertEqual(instances[0]['Name'], 'bucket')

    def test_get_instances_exception(self):
        self.s.s3.set_not_exists_tag_simulation(True)
        instances = self.s.get_instances()
        self.s.s3.set_not_exists_tag_simulation(False)
        self.assertEqual(instances, [])

    def test_already_exists(self):
        self.s.s3.set_not_exists_simulation(False)
        self.assertTrue(self.s.already_exists('bucket-name'))
        self.s.s3.set_not_exists_simulation(True)
        with hlp.captured_output() as (out, err):
            self.assertFalse(self.s.already_exists('bucket-name'))
        self.assertEqual(out.getvalue().strip(), "The bucket named bucket-name not exists")

    def test_empty_bucket(self):
        with hlp.captured_output() as (out, err):
            self.s.empty_bucket('bucket')
        self.assertEqual(out.getvalue().strip(), "Deleting all objects of bucket")
        with hlp.captured_output() as (out, err):
            self.s.empty_bucket(1)
        self.assertEqual(out.getvalue().strip(), "The bucket named 1 not exists")

    def test_run(self):
        now = datetime.datetime.now()
        
        self.s.s3.set_except_simulation(False)
        test = now.replace(hour=8, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "bucket")
        self.assertEqual(self.get_output({"force":["bucket"]}), "bucket")
        test = now.replace(hour=18, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "bucket\nDeleting bucket")
        self.assertEqual(self.get_output({"force":["bucket"]}), "bucket\nDeleting all objects of bucket\nDeleting bucket")

        self.s.s3.set_except_simulation(True)
        test = now.replace(hour=8, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "bucket")
        self.assertEqual(self.get_output({"force":["bucket"]}), "bucket")
        test = now.replace(hour=18, minute=00, day=6)
        self.s.date_tuple = (test.year, test.month, test.day, test.hour, test.minute)
        self.assertEqual(self.get_output(), "bucket\nDeleting bucket\nWarning: bucket named bucket is not empty, you have to force for deleting it")
        self.assertEqual(self.get_output({"force":["bucket"]}), "bucket\nDeleting all objects of bucket\nDeleting bucket\nWarning: bucket named bucket is not empty, you have to force for deleting it")

if __name__ == '__main__':
    unittest.main()