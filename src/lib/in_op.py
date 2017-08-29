#!/usr/bin/env python
''' The IN operation for bender resource'''
from __future__ import print_function

import json
import os

from payload import PayLoad
from base import Base, fail_unless, template_with_regex, write_to_file


class In(Base):
    ''' In resource class'''

    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)
        self.metadata = []
        self.template = kwargs.get("template")
        self.template_filename = os.path.basename(kwargs.get("template_filename", ""))
        self.templated_string = None
        self.original_msg = ""

    def _get_single_msg(self, timestamp):
        return self._call_api(self.channel_type + ".history",
                              channel=self.channel_id,
                              inclusive=True,
                              count=1,
                              latest=timestamp)


    def in_logic(self):
        """Concourse resource `in` logic """
        response = self._get_single_msg(self.version["id_ts"])
        self.original_msg = response["messages"][0].get("text")
        text = self._remove_botname(self.original_msg, self.bot_id)
        regex = self._msg_grammar(self.original_msg)
        user = response["messages"][0].get("user")

        user = self._filter(self.users['members'], "name", "id", user)
        if self.template:
            self.templated_string = template_with_regex(self.template, regex)

        self.metadata = [{"name": "User", "value": user},
                         {"name": "Message", "value": text}]

    def in_output(self):
        """Concourse resource `in` main """

        output = {"version": self.version, "metadata": self.metadata, "original_msg": self.original_msg}
        # Write response as bender.json for further use
        write_to_file(json.dumps(output), '{}/bender.json'.format(self.working_dir))
        # Write template if specified
        if self.templated_string:
            write_to_file(self.templated_string, '{}/{}'.format(self.working_dir, self.template_filename))

        # Print concourse output string
        print(json.dumps(output, indent=4, sort_keys=True))

def main():
    ''' Main'''
    payload = PayLoad()
    fail_unless(payload.args["version"], "version is required")

    slack_client = In(**payload.args)
    slack_client.in_logic()
    slack_client.in_output()

if __name__ == '__main__':
    main()
