import json
import mock
import os
import sys
from unittest import TestCase

import out_op


class OutTest(TestCase):

    @mock.patch('out_op.read_content_from_file')
    @mock.patch('out_op.Out._filter')
    @mock.patch('out_op.Out._get_channel_group_info')
    @mock.patch('out_op.Out._call_api')
    def setUp(self, mock_call_api, mock_get_channel_group_info, mock_filter, mock_read_content_from_file):
        with open('{}/responses/users.json'.format(os.path.dirname(__file__))) as f:
            mock_call_api.return_value = json.load(f)
        mock_get_channel_group_info.return_value = "C024BE91L", "channels"
        mock_filter.return_value = "U01B12FDS"
        mock_read_content_from_file.return_value = '{"version": 1, "metadata": [1], "original_msg": "HI"}'

        self.grammar = "^(superApp)\\s+(deploy)\\s+(live|staging)\\s+(\\S+)($|\\s+)"
        self.resource = out_op.Out(token="token",
                                   channel="testChannel",
                                   bot="theBender",
                                   working_dir="/tmp",
                                   grammar=self.grammar,
                                   path="bender_path",
                                   reply="testing 1.2.3",
                                   reply_thread="reply_thread")

    def test__init__(self):
        # Channel info
        self.assertEqual(self.resource.path, "bender_path")
        self.assertEqual(self.resource.reply, "testing 1.2.3")
        self.assertEqual(self.resource.reply_thread, "reply_thread")
        self.assertEqual(self.resource.working_dir, "/tmp")

        self.assertEqual(self.resource.version, 1)
        self.assertEqual(self.resource.metadata, [1])
        self.assertEqual(self.resource.original_msg, "HI")

    @mock.patch('out_op.json.dumps')
    @mock.patch('out_op.print', create=True)
    def test_out_output(self, mock_print, mock_json_dumps):
        self.resource.version = {"ts": "123"}
        self.resource.metadata = [{"a": 1, "b": 2}]
        # Simply return x
        mock_json_dumps.side_effect = lambda x, indent=0, sort_keys=0: x
        self.resource.out_output()
        mock_json_dumps.assert_called()
        mock_print.assert_called_with({'version': {'ts': '123'}, 'metadata': [{'a': 1, 'b': 2}]})
