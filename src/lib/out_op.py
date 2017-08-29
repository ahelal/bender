#!/usr/bin/env python
''' The OUT operation for bender resource'''
from __future__ import print_function

import json
import os

from payload import PayLoad
from base import Base, fail_unless, template_with_regex


class Out(Base):
    ''' Out resource'''

    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)
        self.metadata = []
        self.path = kwargs.get("path", False)
        self.reply = kwargs.get("reply", False)
        self.reply_thread = kwargs.get("reply_thread", True)
        self.bender_json_path = '{}/{}/bender.json'.format(self.working_dir, self.path)

    def _reply(self, thread_timestamp, text):
        args = {}
        if thread_timestamp:
            args = {"thread_ts": thread_timestamp}

        self._call_api("chat.postMessage",
                       channel=self.channel_id,
                       text=text,
                       **args)

    def out_logic(self):
        """Concourse resource `out` logic """

        fail_unless(os.path.isfile(self.bender_json_path), "Failed to get version info from file {}".format(self.bender_json_path))
        with open(self.bender_json_path) as bender_file:
            output_data = json.load(bender_file)
        self.version = output_data["version"]
        self.metadata = output_data["metadata"]
        regex = self._msg_grammar(output_data["original_msg"])
        templated_reply = template_with_regex(self.reply, regex)

        if self.reply_thread:
            reply_to_thread = self.version["id_ts"]
        else:
            reply_to_thread = False
        self._reply(reply_to_thread, templated_reply)

    def out_output(self):
        """Concourse resource `out` output """
        output = {"version": self.version, "metadata": self.metadata}
        print(json.dumps(output, indent=4, sort_keys=True))


def main():
    ''' Main `out` entry point'''
    payload = PayLoad()
    fail_unless(payload.args.get("path", False), "path is required")
    fail_unless(payload.args.get("reply", False), "reply is required")

    slack_client = Out(**payload.args)
    slack_client.out_logic()
    slack_client.out_output()

if __name__ == '__main__':
    main()
