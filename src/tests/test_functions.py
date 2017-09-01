''' Testing functions '''
import os
import re
from unittest import TestCase

from functions import *
import mock

class FunctionsTest(TestCase):

    @mock.patch('functions.template_str')
    def test_template_with_regex(self, mock_template_str):
        # Simply return t, e
        mock_template_str.side_effect = lambda t, e: (t, e)
        # Test subgroups
        regex = re.compile(r"^(Bender)\s(Rodriguez)")
        regex = regex.match("Bender Rodriguez")
        text, env = template_with_regex("STR", regex)
        self.assertEqual("STR", text)
        self.assertEqual({'regex': ('Bender', 'Rodriguez')}, env)
        # Test named subgroups
        regex = re.compile(r"^(?P<FIRST>Bender)\s(?P<LAST>Rodriguez)")
        regex = regex.match("Bender Rodriguez")
        text, env = template_with_regex("STR2", regex)
        self.assertEqual("STR2", text)
        self.assertEqual({'regex': {'FIRST': 'Bender', 'LAST': 'Rodriguez'}}, env)

    @mock.patch('functions.fail_unless')
    def test_template_str_simple(self, mock_fail_unless):
        # Simple template no variables "pass through"
        string = "Hi Man"
        templated_string = template_str(string, {})
        self.assertEqual("Hi Man", templated_string)
        mock_fail_unless.assert_not_called()

        # Simple templating using variables
        string = "Hi {{ Title }}. {{ Name }} status: {{ Status | string }}"
        variables = {"Title": "Mr", "Name": "Adham", "Status": True}
        templated_string = template_str(string, variables)
        self.assertEqual("Hi Mr. Adham status: True", templated_string)
        mock_fail_unless.assert_not_called()

    @mock.patch('functions.fail_unless')
    def test_template_str_environment_variables(self, mock_fail_unless):
        # Check merge with os.ENV
        os.environ["BUILD_NUM"] = "10"
        string = "http//127.0.0.1/build?name={{build_name}}&num={{ ENV['BUILD_NUM'] }}"
        variables = {"build_name": "bender"}
        templated_string = template_str(string, variables)
        self.assertEqual("http//127.0.0.1/build?name=bender&num=10", templated_string)
        mock_fail_unless.assert_not_called()

    @mock.patch('functions.fail_unless')
    def test_template_str_error(self, mock_fail_unless):
        # Template error
        string = "Hi {{ Title }}. {{ Name"
        no_return = template_str(string, {})
        mock_fail_unless.assert_called()
        self.assertIsNone(no_return)
        # Undefined variable error
        string = "Hi {{ Title }}. {{ Name}}"
        no_return = template_str(string, {"Title": "Mr."})
        mock_fail_unless.assert_called()
        self.assertIsNone(no_return)
        # Undefined OS env
        string = "http//127.0.0.1/build?date={{ ENV['BUILD_DATE'] }}"
        no_return = template_str(string, {})
        mock_fail_unless.assert_called()
        self.assertIsNone(no_return)

    @mock.patch('functions.print', create=True)
    def test_fail_unless(self, mock_print):
        fail_unless(True, "Not")
        mock_print.assert_not_called()

        with self.assertRaises(SystemExit) as value_error:
            fail_unless(False, "FIRE")
        mock_print.assert_called()
        self.assertEqual(value_error.exception.code, 1)
        ## Can't manage to check one argument only :(
        #mock_print.assert_called_with("FIRE", file=mock.ANY, mode=mock.ANY)

    @mock.patch('functions.fail_unless')
    def test_read_if_exists(self, mock_fail_unless):
        base_path = "/Bcbc/x"
        content = "SOMETHING"
        return_val = read_if_exists(base_path, content)
        self.assertEqual(return_val, "SOMETHING")
        mock_fail_unless.assert_not_called()

        content = "content1\ncontent2\n"
        return_val = read_if_exists(os.path.dirname(__file__), "responses/file.txt")
        mock_fail_unless.assert_not_called()
        self.assertEqual(return_val, content)

    def test_list_get(self):
        self.assertEqual(list_get([0,1,2], 1, True), 1)
        self.assertTrue(list_get([0,1,2], -1, True))
        self.assertIsNone(list_get([0,1,2], 4))
