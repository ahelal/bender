#!/usr/bin/env python
''' The OUT operation for bender resource'''
from __future__ import print_function

import json
import os
import sys

from payload import PayLoad
from base import Base, fail_unless, template_with_regex


class Out(Base):
    ''' Out resource'''

    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)
        self.metadata = []
        self.path = kwargs.get("path", False)
        self.reply = kwargs.get("reply", False)

    def _reply(self, timestamp, text):
        self._call_api("chat.postMessage",
                       channel=self.channel_id,
                       thread_ts=timestamp,
                       text=text)

    def out_logic(self):
        """Concourse resource `out` logic """
        output_file = '{}/{}/bender.json'.format(sys.argv[1], self.path)
        fail_unless(os.path.isfile(output_file), "Failed to get version info from file {}".format(output_file))

        with open(output_file) as bender_file:
            output_data = json.load(bender_file)
        self.version = output_data["version"]
        self.metadata = output_data["metadata"]
        regex = self._msg_grammar(output_data["original_msg"])
        templated_reply = template_with_regex(self.reply, regex)
        # template reply
        self._reply(self.version["id_ts"], templated_reply)

    def out_output(self):
        """Concourse resource `out` output """
        output = {"version": self.version, "metadata": self.metadata}
        print(json.dumps(output, indent=4, sort_keys=True))


def main():
    payload = PayLoad()
    fail_unless(payload.args.get("path", False), "path is required")
    fail_unless(payload.args.get("reply", False), "reply is required")

    slack_client = Out(**payload.args)
    slack_client.out_logic()
    slack_client.out_output()

if __name__ == '__main__':
    main()
