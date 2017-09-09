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

        self.resource = base.Base(token="token",
                                  channel="testChannel",
                                  bot_name="theBender",
                                  working_dir="/test",
                                  grammar="grammar",
                                  path="bender_path",
                                  reply="testing 1.2.3",
                                  slack_unread=True)

    def test__init__(self):
        # Channel info
        self.assertEqual(self.resource.channel, "testChannel")
        self.assertEqual(self.resource.channel_id, "C024BE91L")
        self.assertEqual(self.resource.channel_type, "channels")
        # Bot info
        self.assertEqual(self.resource.bot, "theBender")
        # Misc
        self.assertEqual(self.resource.grammar, "grammar")
        self.assertTrue(self.resource.slack_unread)
        self.assertEqual(self.resource.working_dir, "/test")

    @mock.patch('base.fail_unless')
    @mock.patch('base.Base._filter')
    @mock.patch('base.Base._get_channel_group_info')
    @mock.patch('base.Base._call_api')
    def test_mandatory(self, mock_call_api, mock_get_channel_group_info, mock_filter, mock_fail_unless):
        def fake_fail_unless(c, m):
            if not c:
                raise OSError
        self.script_dir = os.path.dirname(__file__)
        with open('{}/responses/users.json'.format(self.script_dir)) as user_json_file:
            mock_call_api.return_value = json.load(user_json_file)
        mock_get_channel_group_info.return_value = "C024BE91L", "channels"
        mock_filter.return_value = "U01B12FDS"
        mock_fail_unless.side_effect = fake_fail_unless

        self.assertRaises(OSError, base.Base, token="token",
                                              channel="testChannel",
                                              bot_name="theBender",
                                              mention=False,
                                              grammar=False)

    def test_remove_bot_id(self):
        bot_id = "U01B12FDS"
        self.assertEqual("", self.resource._remove_bot_id("<@U01B12FDS>  ", bot_id))
        self.assertEqual("", self.resource._remove_bot_id("  <@U01B12FDS>", bot_id))
        self.assertEqual("", self.resource._remove_bot_id("  <@U01B12FDS> ", bot_id))
        self.assertEqual("Hi", self.resource._remove_bot_id("<@U01B12FDS> Hi ", bot_id))
        self.assertIsNone(self.resource._remove_bot_id("@U01B12FDS Hi", bot_id))
        self.assertIsNone(self.resource._remove_bot_id("< @U01B12FDS > Hi", bot_id))

    def test_msg_grammar_with_mention(self):
        self.resource.bot_id = "U01B12FDS"
        self.resource.mention = True
        # Check mention msg
        self.resource.grammar = False
        self.assertIsNone(self.resource._msg_grammar("@U01B12FDS Hi"))
        self.assertIsNotNone(self.resource._msg_grammar("<@U01B12FDS> superApp  deploy  live  1.2"))
        # Check with grammar
        self.resource.grammar = "^(superApp)\s+(deploy)\s+(live|staging)\s+(\S+)($|\s+)"
        self.assertIsNone(self.resource._msg_grammar("theBender superApp deploy live 1.2"))
        self.assertIsNotNone(self.resource._msg_grammar("<@U01B12FDS> superApp  deploy  live  1.2"))
        self.assertIsNone(self.resource._msg_grammar("<@U01B12FDS> superApp2 deploy dev 1.1 extra"))

    def test_msg_grammar_without_mention(self):
        self.resource.mention = False
        self.resource.grammar = "^(calculon)\s+(superApp)\s+(deploy)\s+(live|staging)\s+(\S+)($|\s+)"
        self.assertIsNone(self.resource._msg_grammar("calculon superApp deploy dev 1.2"))
        self.assertIsNotNone(self.resource._msg_grammar("calculon superApp  deploy  live  1.2"))
        self.assertIsNone(self.resource._msg_grammar("<@calculon> superApp2 deploy dev 1.1 extra"))


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
