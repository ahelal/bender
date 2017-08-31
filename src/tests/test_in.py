''' testing in operation'''
import json
import os
from unittest import TestCase

import mock

import in_op


class InTest(TestCase):

    @mock.patch('in_op.In._filter')
    @mock.patch('in_op.In._get_channel_group_info')
    @mock.patch('in_op.In._call_api')
    def setUp(self, mock_call_api, mock_get_channel_group_info, mock_filter):

        self.script_dir = os.path.dirname(__file__)
        with open('{}/responses/users.json'.format(self.script_dir)) as f:
            mock_call_api.return_value = json.load(f)
        mock_get_channel_group_info.return_value = "C024BE91L", "channels"
        mock_filter.return_value = "U01B12FDS"

        self.grammar = "^(superApp)\s+(deploy)\s+(live|staging)\s+(\S+)($|\s+)"
        self.resource = in_op.In(template="VERSION={{ regex[4] }}", template_filename="template_filename",
                                 grammar=self.grammar, path="bender_path", reply="testing 1.2.3")

    def test__init__(self):

        self.assertEqual(self.resource.template_filename, "template_filename")

    # TODO test_in_logic

    @mock.patch('in_op.write_to_file')
    @mock.patch('in_op.json.dumps')
    @mock.patch('in_op.print', create=True)
    def test_in_output(self, mock_print, mock_json_dumps, mock_write_to_file):
        # Test with no templated_string
        self.resource.templated_string = False
        self.resource.working_dir = "/tmp"
        self.resource.original_msg = "OR"
        self.resource.version = {"ts": "123"}
        self.resource.metadata = [{"a": 1, "b": 2}]
        # Expected output
        output = {'version': {'ts': '123'}, 'metadata': [{'a': 1, 'b': 2}], 'original_msg': 'OR'}
        mock_json_dumps.side_effect = lambda x, indent=0, sort_keys=0: x
        # Call in_output
        self.resource.in_output()
        # Assert
        mock_json_dumps.assert_called()
        mock_print.assert_called_with(output)
        mock_write_to_file.assert_called_once_with(output, "/tmp/bender.json")

        # Test with templated_String
        self.resource.template_filename = "template.txt"
        mock_write_to_file.reset_mock()
        self.resource.templated_string = "TEMPLATED_STRING"
        # Call in_output
        self.resource.in_output()
        mock_write_to_file.assert_any_call(output, "/tmp/bender.json")
        mock_write_to_file.assert_any_call("TEMPLATED_STRING", "/tmp/template.txt")
        self.assertEquals(2, mock_write_to_file.call_count)
