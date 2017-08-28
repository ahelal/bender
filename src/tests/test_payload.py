import json
import os
from unittest import TestCase

import mock

import payload


class PayloadTest(TestCase):

    @mock.patch('payload.fail_unless')
    @mock.patch('payload.PayLoad._get_payload')
    def test_parse_payload_no_source(self, mock_get_payload, fail_unless):
        mock_get_payload.side_effect = [{}]
        payload.PayLoad()
        fail_unless.assert_called()

    @mock.patch('payload.fail_unless')
    @mock.patch('payload.PayLoad._get_payload')
    def test_parse_payload_empty_source(self, mock_get_payload, mock_fail_unless):
        mock_get_payload.side_effect = [{'source': {}}]
        payload.PayLoad()
        mock_fail_unless.assert_called()

    @mock.patch('payload.fail_unless')
    @mock.patch('payload.PayLoad._get_payload')
    def test_parse_payload_no_mandatory(self, mock_get_payload, mock_fail_unless):
        mock_get_payload.side_effect = [{'source': {"slack_token": "slack_token"}}]
        payload.PayLoad()
        mock_fail_unless.assert_called()

    @mock.patch('payload.fail_unless')
    @mock.patch('payload.PayLoad._get_payload')
    def test_parse_payload_defaults(self, mock_get_payload, mock_fail_unless):
        mock_get_payload.side_effect = [{'source': {"slack_token": "slack_token", "channel": "channel"}}]
        py = payload.PayLoad()
        mock_fail_unless.assert_not_called()
        self.assertEqual(py.args["slack_token"], "slack_token")
        self.assertEqual(py.args["channel"], "channel")
        self.assertEqual(py.args["template_filename"], "template_file.txt")

        self.assertIsNone(py.args["template"])
        self.assertIsNone(py.args["version"])
        self.assertIsNone(py.args["grammar"])
        self.assertIsNone(py.args["path"])
        self.assertIsNone(py.args["reply"])

    @mock.patch('payload.fail_unless')
    @mock.patch('payload.PayLoad._get_payload')
    def test_parse_payload_values(self, mock_get_payload, mock_fail_unless):
        mock_get_payload.side_effect = [{'params': {'path': 'path', 'reply': 'reply'},
                                         'source': {'bot_name': 'bot_name',
                                                    'channel': 'channel',
                                                    'grammar': 'grammar',
                                                    'slack_token': 'slack_token',
                                                    'template': 'template',
                                                    'template_filename': 'template_filename'},
                                         'version': 'version'}]
        py = payload.PayLoad()
        mock_fail_unless.assert_not_called()
        self.assertEqual(py.args["slack_token"], "slack_token")
        self.assertEqual(py.args["channel"], "channel")
        self.assertEqual(py.args["template_filename"], "template_filename")

        self.assertEqual(py.args["template"], "template")
        self.assertEqual(py.args["version"], "version")
        self.assertEqual(py.args["grammar"], "grammar")
        self.assertEqual(py.args["path"], "path")
        self.assertEqual(py.args["reply"], "reply")
