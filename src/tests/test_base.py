import json
import mock
import os
import sys
import re
from unittest import TestCase

import base

class BaseTest(TestCase):

    @mock.patch('base.Base._filter')
    @mock.patch('base.Base._get_channel_group_info')
    @mock.patch('base.Base._call_api')
    def setUp(self, mock_call_api, mock_get_channel_group_info, mock_filter):

        self.script_dir = os.path.dirname(__file__)
        with open('{}/responses/users.json'.format(self.script_dir)) as user_json_file:
            mock_call_api.return_value = json.load(user_json_file)
        mock_get_channel_group_info.return_value = "C024BE91L", "channels"
        mock_filter.return_value = "U01B12FDS"

        self.grammar = "^(superApp)\s+(deploy)\s+(live|staging)\s+(\S+)($|\s+)"
        self.resource = base.Base(token="token", channel="testChannel", bot="theBender",
                                  grammar=self.grammar, path="bender_path", reply="testing 1.2.3")

    def test__init__(self):
        # Channel info
        self.assertEqual(self.resource.channel, "testChannel")
        self.assertEqual(self.resource.channel_id, "C024BE91L")
        self.assertEqual(self.resource.channel_type, "channels")
        # Bot info
        self.assertEqual(self.resource.bot, "theBender")
        self.assertEqual(self.resource.bot_id, "U01B12FDS")
        # Misc
        self.assertEqual(self.resource.grammar, self.grammar)

    def test_remove_botname(self):
        bot_id = "U01B12FDS"
        self.assertEqual("", self.resource._remove_botname("<@U01B12FDS>  ", bot_id))
        self.assertEqual("", self.resource._remove_botname("  <@U01B12FDS>", bot_id))
        self.assertEqual("", self.resource._remove_botname("  <@U01B12FDS> ", bot_id))
        self.assertEqual("Hi", self.resource._remove_botname("<@U01B12FDS> Hi ", bot_id))
        self.assertIsNone(self.resource._remove_botname("@U01B12FDS Hi", bot_id))
        self.assertIsNone(self.resource._remove_botname("< @U01B12FDS > Hi", bot_id))

    def test_msg_grammar(self):
        # TODO:, check return value of expression
        self.assertIsNone(self.resource._msg_grammar("theBender superApp deploy live 1.2"))
        self.assertIsNotNone(self.resource._msg_grammar("<@U01B12FDS> superApp  deploy  live  1.2"))
        self.assertIsNone(self.resource._msg_grammar("<@U01B12FDS> superApp2 deploy dev 1.1 extra"))
        # Check direct msg
        self.resource.grammar = False
        self.assertIsNone(self.resource._msg_grammar("@U01B12FDS Hi"))
        self.assertIsNotNone(self.resource._msg_grammar("<@U01B12FDS> superApp  deploy  live  1.2"))
        # Reset the grammar
        self.resource.grammar = self.grammar

    def test_filter(self):
        items = [{"Id": 1, "Name": "One"}, {"Id": 2, "Name": "Two"}, {"Id": 3, "Name": "Three"}]
        self.assertEqual("One", self.resource._filter(items, "Name", "Id", 1))
        self.assertEqual(1, self.resource._filter(items, "Id", "Name", "One"))
        # Non existing filter value
        self.assertIsNone(self.resource._filter(items, "Id", "Name", "Five"))
        # Non existing filter field
        self.assertIsNone(self.resource._filter(items, "Id", "Type", "String"))
        # Non existing return field
        self.assertIsNone(self.resource._filter(items, "Type", "Name", "One"))


    @mock.patch('base.fail_unless')
    @mock.patch('slackclient.SlackClient.api_call')
    def test_call_api(self, mock_slackclient, mock_fail_unless):
        mock_fail_unless.return_value = ""
        # API returned true
        mock_slackclient.return_value = {"ok": True}
        self.resource._call_api("bogus.call", arg1="val1", arg2="val2")
        mock_slackclient.assert_called_with('bogus.call', arg1="val1", arg2="val2")
        self.assertTrue(mock_slackclient.called)


class FunctionsTest(TestCase):

    @mock.patch('base.template_str')
    def test_template_with_regex(self, mock_template_str):
        # Simply return t, e
        mock_template_str.side_effect = lambda t, e: (t, e)
        # Test subgroups
        regex = re.compile(r"^(Bender)\s(Rodriguez)")
        regex = regex.match("Bender Rodriguez")
        text, env = base.template_with_regex("STR", regex)
        self.assertEqual("STR", text)
        self.assertEqual({'regex': ('Bender', 'Rodriguez')}, env)
        # Test named subgroups
        regex = re.compile(r"^(?P<FIRST>Bender)\s(?P<LAST>Rodriguez)")
        regex = regex.match("Bender Rodriguez")
        text, env = base.template_with_regex("STR2", regex)
        self.assertEqual("STR2", text)
        self.assertEqual({'regex': {'FIRST': 'Bender', 'LAST': 'Rodriguez'}}, env)

    @mock.patch('base.fail_unless')
    def test_template_str_simple(self, mock_fail_unless):
        # Simple template no variables "pass through"
        string = "Hi Man"
        templated_string = base.template_str(string, {})
        self.assertEqual("Hi Man", templated_string)
        mock_fail_unless.assert_not_called()

        # Simple templating using variables
        string = "Hi {{ Title }}. {{ Name }} status: {{ Status | string }}"
        variables = {"Title": "Mr", "Name": "Adham", "Status": True}
        templated_string = base.template_str(string, variables)
        self.assertEqual("Hi Mr. Adham status: True", templated_string)
        mock_fail_unless.assert_not_called()

    @mock.patch('base.fail_unless')
    def test_template_str_environment_variables(self, mock_fail_unless):
        # Check merge with os.ENV
        os.environ["BUILD_NUM"] = "10"
        string = "http//127.0.0.1/build?name={{build_name}}&num={{ ENV['BUILD_NUM'] }}"
        variables = {"build_name": "bender"}
        templated_string = base.template_str(string, variables)
        self.assertEqual("http//127.0.0.1/build?name=bender&num=10", templated_string)
        mock_fail_unless.assert_not_called()

    @mock.patch('base.fail_unless')
    def test_template_str_error(self, mock_fail_unless):
        # Template error
        string = "Hi {{ Title }}. {{ Name"
        no_return = base.template_str(string, {})
        mock_fail_unless.assert_called()
        self.assertIsNone(no_return)
        # Undefined variable error
        string = "Hi {{ Title }}. {{ Name}}"
        no_return = base.template_str(string, {"Title": "Mr."})
        mock_fail_unless.assert_called()
        self.assertIsNone(no_return)
        # Undefined OS env
        string = "http//127.0.0.1/build?date={{ ENV['BUILD_DATE'] }}"
        no_return = base.template_str(string, {})
        mock_fail_unless.assert_called()
        self.assertIsNone(no_return)

    @mock.patch('base.print', create=True)
    def test_fail_unless(self, mock_print):
        base.fail_unless(True, "Not")
        mock_print.assert_not_called()

        with self.assertRaises(SystemExit) as value_error:
            base.fail_unless(False, "FIRE")
        mock_print.assert_called()
        self.assertEqual(value_error.exception.code, 1)
        ## Can't manage to check one argument only :(
        #mock_print.assert_called_with("FIRE", file=mock.ANY, mode=mock.ANY)
