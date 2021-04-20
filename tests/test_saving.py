import unittest
import tests.helper as hlp
from aws_saving.saving import Saving

class TestService(unittest.TestCase, Saving):
    services_name = ["service"]
    event = None
    s = None

    def __init__(self, *args, **kwargs):
        self.event = {'services_name': self.services_name}
        self.s = Saving(self.event)
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_get_services_name(self):
        self.assertEqual(self.s.get_services_name(), self.services_name)

    def test_print_service_log(self):
        with hlp.captured_output() as (out, err):
            self.s.print_service_log("service")
        output = out.getvalue().strip()
        self.assertEqual(output, "Running AWS saving on SERVICE service")

    def test_underscore_to_camel_case_capitalized(self):
        self.assertEqual(self.s.underscore_to_camel_case_capitalized("service"), "Service")
        self.assertEqual(self.s.underscore_to_camel_case_capitalized("service_subservice"), "ServiceSubservice")

    def test_run(self):
        with hlp.captured_output() as (out, err):
            with self.assertRaises(NotImplementedError):
                self.s.run({})
        output = out.getvalue().strip()
        self.assertEqual(output, "['service']\nRunning AWS saving on SERVICE service")

if __name__ == '__main__':
    unittest.main()