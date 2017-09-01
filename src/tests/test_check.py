import json
import os
from unittest import TestCase

import mock

import check_op


class CheckTest(TestCase):

    @mock.patch('check_op.Check._filter')
    @mock.patch('check_op.Check._get_channel_group_info')
    @mock.patch('check_op.Check._call_api')
    def setUp(self, mock_call_api, mock_get_channel_group_info, mock_filter):

        self.script_dir = os.path.dirname(__file__)
        with open('{}/responses/users.json'.format(self.script_dir)) as f:
            mock_call_api.return_value = json.load(f)
        mock_get_channel_group_info.return_value = "C024BE91L", "channels"
        mock_filter.return_value = "U01B12FDS"

        self.grammar = "^(superApp)\s+(deploy)\s+(live|staging)\s+(\S+)($|\s+)"
        self.resource = check_op.Check(token="token", channel="testChannel", bot="theBender",
                                       grammar=self.grammar, path="bender_path", reply="testing 1.2.3")
    def test__init__(self):
        self.assertEqual(self.resource.checked_msg, [])

    @mock.patch('check_op.Check._call_api')
    def test_check_logic_unread_no_msg(self, mock_call_api):
        mock_call_api.return_value = {"ok": True, "latest": "1358547726.000003", "messages": [], "has_more": False,
                                      "unread_count_display": 0}
        mark_ts = self.resource.check_logic_unread()
        mock_call_api.assert_called()
        self.assertFalse(mark_ts)

        # # Not working yet
        # self.resource.check_output()
        # self.assertTrue(mock_print.called)
        # mock_print.assert_called_with('[]')

        # self.resource.checked_msg = [{"id_ts": "1358546512.010007", "v": "2"},
        #                              {"id_ts": "1328546512.010007", "v": "0"},
        #                              {"id_ts": "1328546512.110007", "v": "1"}]

        # self.resource.check_output()
        # mock_print.assert_called()
        # self.assertItemsEqual([{"id_ts": "1328546512.010007", "v": "0"},
        #                        {"id_ts": "1328546512.110007", "v": "1"},
        #                        {"id_ts": "1358546512.010007", "v": "2"}], self.resource.checked_msg)


    # @mock.patch('base.Base._call_api')
    # def test_check_logic_unread_many(self, mock_call_api):
    #     with open('{}/responses/messages_many.json'.format(self.script_dir)) as json_file:
    #         mock_call_api.return_value = json.load(json_file)

    #     mark_ts = self.resource.check_logic_unread()
    #     mock_call_api.assert_called()
    #     self.assertFalse(mark_ts)

    @mock.patch('check_op.json.dumps')
    @mock.patch('check_op.print', create=True)
    def test_check_output(self, mock_print, mock_json_dumps):
        self.resource.checked_msg = [1, 2, 3]
        # Simply return x
        mock_json_dumps.side_effect = lambda x, indent=0, sort_keys=0: x
        self.resource.check_output()
        mock_json_dumps.assert_called()
        mock_print.assert_called_with([1, 2, 3])

    @mock.patch('check_op.Check._call_api')
    def test_mark_read(self, mock_call_api):
        self.resource._mark_read("123")
        self.assertTrue(mock_call_api.called)
        mock_call_api.assert_called_with(
            'channels.mark', channel='C024BE91L', ts='123')


    @mock.patch('check_op.Check._msg_grammar')
    def test_filter_msgs(self, mock_msg_grammer):
        with open('{}/responses/messages.json'.format(self.script_dir)) as json_file:
            messages = json.load(json_file)
        # Skipping return of message type not "message" so our index is less then actual message.
        mock_msg_grammer.side_effect = [False, messages["messages"][2], False, messages["messages"][5], False]
        self.resource._filter_msgs(messages["messages"], len(messages["messages"]))
        check_msgs = [{'id_ts': u'1358546512.010007'}, {'id_ts': u'1358546515.010007'}]
        self.assertItemsEqual(check_msgs, self.resource.checked_msg)
