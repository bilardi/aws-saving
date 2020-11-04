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

    def test_cloudformation(self):
        output = self.lambda_client.invoke(
                    FunctionName='saving-{}'.format(os.environ.get('STAGE')),
                    InvocationType='RequestResponse', #|'Event'|'DryRun',
                    Payload=json.dumps({'services_name': ['cloudformation']})
                )
        self.assertEqual(output['StatusCode'], 200)
        # print(output['Payload'].read())
        with self.assertRaises(KeyError):
            self.assertEqual(output['FunctionError'], 'Unhandled')

if __name__ == '__main__':
    unittest.main()
