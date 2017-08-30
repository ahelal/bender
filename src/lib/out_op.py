#!/usr/bin/env python
''' The OUT operation for bender resource'''
from __future__ import print_function

import json

from payload import PayLoad
from base import Base, fail_unless, template_with_regex, read_if_exists, read_content_from_file


class Out(Base):
    ''' Out resource'''

    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)
        self.metadata = []
        self.path = kwargs.get("path", False)
        self.reply = read_if_exists(self.working_dir, kwargs.get("reply", False))
        self.reply_thread = kwargs.get("reply_thread", True)

        # Get context from original message
        context_json_path = '{}/{}/bender.json'.format(self.working_dir, self.path)
        try:
            context_content = read_content_from_file(context_json_path)
            context_content = json.loads(context_content)
        except ValueError as value_error:
            fail_unless(False, "JSON Input error: {}".format(value_error))

        self.version = context_content["version"]
        self.metadata = context_content["metadata"]
        self.original_msg = context_content["original_msg"]

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

        regex = self._msg_grammar(self.original_msg)
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
