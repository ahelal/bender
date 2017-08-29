''' Parse payload options and command line argument'''
from __future__ import print_function

import json
import sys
import os

from base import fail_unless


class PayLoad(object):
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
            self._parse_payload()
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

    def _parse_payload(self):
        # Version send by concourses in check and get
        self.args["version"] = self.payload.get("version")
        try:
            # Mandatory source configs
            self.args["slack_token"] = self.source["slack_token"]
            self.args["channel"] = self.source["channel"]
        except KeyError as value_error:
            fail_unless(False, "Source config '{}' required".format(value_error))
        # Optional source configs
        self.args["bot_name"] = self.source.get("bot_name", "bender")
        self.args["grammar"] = self.source.get("grammar")
        self.args["template"] = self.source.get("template")
        self.args["template_filename"] = self.source.get("template_filename", "template_file.txt")
        self.args["slack_unread"] = self.source.get("slack_unread", False)
        # Optional params config
        self.args["path"] = self.params.get("path")
        self.args["reply"] = self.params.get("reply")
