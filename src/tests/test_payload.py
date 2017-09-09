import sys
from unittest import TestCase

import mock

import payload


class PayloadTest(TestCase):

    @mock.patch('payload.os.path.isdir')
    @mock.patch('payload.fail_unless')
    @mock.patch('payload.PayLoad._get_payload')
    def test_get_dir_from_argv(self, mock_get_payload, mock_fail_unless, mock_os_path):
        sys.argv = ["a"]
        argv_return = payload.PayLoad._get_dir_from_argv()
        mock_fail_unless.assert_not_called()
        self.assertFalse(argv_return)

        sys.argv = ["a", "b"]
        mock_os_path.return_value = False
        argv_return = payload.PayLoad._get_dir_from_argv()
        mock_fail_unless.assert_called()

        mock_fail_unless.reset_mock()
        sys.argv = ["a", "/x"]
        mock_os_path.return_value = True
        argv_return = payload.PayLoad._get_dir_from_argv()
        self.assertEqual(argv_return, "/x")

    @mock.patch('payload.fail_unless')
    @mock.patch('payload.PayLoad._get_payload')
    def test_parse_payload_no_source(self, mock_get_payload, mock_fail_unless):
        mock_get_payload.side_effect = [{}]
        payload.PayLoad()
        mock_fail_unless.assert_called()

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

    @mock.patch('payload.PayLoad._get_dir_from_argv')
    @mock.patch('payload.fail_unless')
    @mock.patch('payload.PayLoad._get_payload')
    def test_parse_payload_defaults(self, mock_get_payload, mock_fail_unless, mock_get_dir_from_argv):
        mock_get_dir_from_argv.return_value = "/tmp"
        mock_get_payload.side_effect = [{'source': {"slack_token": "slack_token", "channel": "channel"}}]
        py = payload.PayLoad()
        mock_fail_unless.assert_not_called()
        self.assertEqual(py.args["slack_token"], "slack_token")
        self.assertEqual(py.args["channel"], "channel")
        self.assertEqual(py.args["template_filename"], "template_file.txt")
        self.assertEqual(py.args["version"], {})
        self.assertFalse(py.args["slack_unread"])
        self.assertTrue(py.args['mention'])
        self.assertTrue(py.args['as_user'])
        self.assertIsNone(py.args["bot_icon_emoji"])
        self.assertIsNone(py.args["bot_icon_url"])
        self.assertIsNone(py.args["template"])
        self.assertIsNone(py.args["grammar"])
        self.assertIsNone(py.args["path"])
        self.assertIsNone(py.args["reply"])
        self.assertTrue(py.args["reply_thread"])

    @mock.patch('payload.PayLoad._get_dir_from_argv')
    @mock.patch('payload.fail_unless')
    @mock.patch('payload.PayLoad._get_payload')
    def test_parse_payload_values(self, mock_get_payload, mock_fail_unless, mock_get_dir_from_argv):
        mock_get_dir_from_argv.return_value = "/tmp"
        mock_get_payload.side_effect = [{'params': {'path': 'path', 'reply': 'reply', 'reply_attachments': 'reply_attachments',
                                                    'reply_thread': 'reply_thread'},
                                         'source': {'bot_name': 'bot_name',
                                                    'channel': 'channel',
                                                    'grammar': 'grammar',
                                                    'slack_token': 'slack_token',
                                                    'template': 'template',
                                                    'mention': 'mention',
                                                    'as_user': 'as_user',
                                                    'bot_icon_emoji': 'bot_icon_emoji',
                                                    'bot_icon_url': 'bot_icon_url',
                                                    'template_filename': 'template_filename',
                                                    'slack_unread': True},
                                         'version': 'version'}]
        py = payload.PayLoad()
        mock_fail_unless.assert_not_called()
        self.assertEqual(py.args["slack_token"], "slack_token")
        self.assertEqual(py.args["channel"], "channel")
        self.assertEqual(py.args["template_filename"], "template_filename")
        self.assertTrue(py.args["slack_unread"])

        self.assertEqual(py.args["mention"], "mention")
        self.assertEqual(py.args["as_user"], "as_user")
        self.assertEqual(py.args["bot_icon_emoji"], "bot_icon_emoji")
        self.assertEqual(py.args["bot_icon_url"], "bot_icon_url")

        self.assertEqual(py.args["template"], "template")
        self.assertEqual(py.args["version"], "version")
        self.assertEqual(py.args["grammar"], "grammar")
        self.assertEqual(py.args["path"], "path")
        self.assertEqual(py.args["reply"], "reply")
        self.assertEqual(py.args["reply_attachments"], "reply_attachments")
        self.assertEqual(py.args["reply_thread"], "reply_thread")
