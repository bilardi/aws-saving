import unittest
import tests.helper as hlp
import json
import boto3
import os

class TestService(unittest.TestCase):
    lambda_client = None

    def __init__(self, *args, **kwargs):
        self.lambda_client = boto3.client('lambda')
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_empty(self):
        output = self.lambda_client.invoke(
                    FunctionName='saving-{}'.format(os.environ.get('STAGE')),
                    InvocationType='RequestResponse', #|'Event'|'DryRun',
                    Payload=json.dumps({'services_name': ["service"]})
                )
        self.assertEqual(output['StatusCode'], 200)
        self.assertEqual(output['FunctionError'], 'Unhandled')

    def delete_s3(self):
        output = self.lambda_client.invoke(
                    FunctionName='saving-{}'.format(os.environ.get('STAGE')),
                    InvocationType='RequestResponse', #|'Event'|'DryRun',
                    Payload=json.dumps({'services_name': ['s3']})
                )
        self.assertEqual(output['StatusCode'], 200)
        # print(output['Payload'].read())
        with self.assertRaises(KeyError):
            self.assertEqual(output['FunctionError'], 'Unhandled')

    def delete_ec2(self):
        output = self.lambda_client.invoke(
                    FunctionName='saving-{}'.format(os.environ.get('STAGE')),
                    InvocationType='RequestResponse', #|'Event'|'DryRun',
                    Payload=json.dumps({'services_name': ['ec2']})
                )
        self.assertEqual(output['StatusCode'], 200)
        # print(output['Payload'].read())
        # self.assertEqual(output['FunctionError'], 'Unhandled') # TODO without ec2
        # with self.assertRaises(KeyError):
        #     self.assertEqual(output['FunctionError'], 'Unhandled')

    def delete_rds(self):
        output = self.lambda_client.invoke(
                    FunctionName='saving-{}'.format(os.environ.get('STAGE')),
                    InvocationType='RequestResponse', #|'Event'|'DryRun',
                    Payload=json.dumps({'services_name': ['rds']})
                )
        self.assertEqual(output['StatusCode'], 200)
        # print(output['Payload'].read())
        with self.assertRaises(KeyError):
            self.assertEqual(output['FunctionError'], 'Unhandled')

    def delete_cloudformation(self):
        output = self.lambda_client.invoke(
                    FunctionName='saving-{}'.format(os.environ.get('STAGE')),
                    InvocationType='RequestResponse', #|'Event'|'DryRun',
                    Payload=json.dumps({'services_name': ['cloudformation']})
                )
        self.assertEqual(output['StatusCode'], 200)
        # print(output['Payload'].read())
        # self.assertEqual(output['FunctionError'], 'Unhandled') # see TODO in cloudformation.py
        # with self.assertRaises(KeyError):
        #     self.assertEqual(output['FunctionError'], 'Unhandled')

    def test_not_empty(self):
        self.delete_s3()
        self.delete_ec2()
        self.delete_rds()
        self.delete_cloudformation()

if __name__ == '__main__':
    unittest.main()
