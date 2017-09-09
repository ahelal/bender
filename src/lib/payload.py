''' Parse payload options and command line argument'''
from __future__ import print_function

import json
import sys
import os

from functions import fail_unless

class PayLoad(object): # pylint: disable=too-few-public-methods
    ''' Payload class '''

    def __init__(self):
        self.payload = self._get_payload()
        self.args = {}
        try:
            self.source = self.payload["source"]
        except KeyError:
            fail_unless(False, "Source not configured.")
        else:
            self.params = self.payload.get("params", {})
            self.parse_payload()
        # argument pass with dir
        self.args["working_dir"] = self._get_dir_from_argv()

    @staticmethod
    def _get_payload():
        ''' Return a dict after serializing the JSON payload from STDIN '''
        try:
            payload = json.load(sys.stdin)
        except ValueError as value_error:
            fail_unless(False, "JSON Input error: {}".format(value_error))
        return payload

    @staticmethod
    def _get_dir_from_argv():
        if len(sys.argv) < 2:
            return False

        fail_unless(os.path.isdir(sys.argv[1]), "Invalid dir argument passed '{}'".format(sys.argv[1]))
        return sys.argv[1]

    def parse_payload(self):
        ''' Parse payload passed by concourse'''
        self.args["version"] = self.payload.get("version")
        if self.args["version"] is None:
            self.args["version"] = {}
        try:
            # Mandatory source configs
            self.args["slack_token"] = self.source["slack_token"]
            self.args["channel"] = self.source["channel"]
        except KeyError as value_error:
            fail_unless(False, "Source config '{}' required".format(value_error))
        # Optional source configs
        self.args["bot_name"] = self.source.get("bot_name", "bender")
        self.args["mention"] = self.source.get("mention", True)
        self.args["as_user"] = self.source.get("as_user", True)
        self.args["bot_icon_emoji"] = self.source.get("bot_icon_emoji")
        self.args["bot_icon_url"] = self.source.get("bot_icon_url")
        self.args["grammar"] = self.source.get("grammar")
        self.args["template"] = self.source.get("template")
        self.args["template_filename"] = self.source.get("template_filename", "template_file.txt")
        self.args["slack_unread"] = self.source.get("slack_unread")
        # Optional params config
        self.args["path"] = self.params.get("path")
        self.args["reply"] = self.params.get("reply")
        self.args["reply_attachments"] = self.params.get("reply_attachments")
        self.args["reply_thread"] = self.params.get("reply_thread", True)
