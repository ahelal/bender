''' Testing base class'''
import json
import os
import re
from unittest import TestCase

import mock

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
        self.resource = base.Base(token="token", channel="testChannel", bot_name="theBender", working_dir="/test",
                                  grammar=self.grammar, path="bender_path", reply="testing 1.2.3", slack_unread=True)

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
        self.assertTrue(self.resource.slack_unread)
        self.assertEqual(self.resource.working_dir, "/test")

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
