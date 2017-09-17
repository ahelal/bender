#!/usr/bin/env python
''' The IN operation for bender resource'''
from __future__ import print_function

import json
import os

from payload import PayLoad
from base import Base
from functions import write_to_file, list_get, template_with_regex, fail_unless

class In(Base):
    ''' In resource class'''

    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)
        self.metadata = []
        self.template = kwargs.get("template")
        self.template_filename = os.path.basename(kwargs.get("template_filename"))
        self.templated_string = None
        self.original_msg = ""

    def _get_single_msg(self, timestamp):
        message = self._call_api(self.channel_type + ".history",
                                 channel=self.channel_id,
                                 inclusive=True,
                                 count=1,
                                 latest=timestamp)
        fail_unless(message["messages"], "Message '{}' is empty. Might have been removed".format(timestamp))
        return message

    def in_logic(self):
        """Concourse resource `in` logic """
        message = list_get(self._get_single_msg(self.version["id_ts"])["messages"], 0, {})
        self.original_msg = message.get("text")
        user = self._filter(self.users['members'], "name", "id", message.get("user"))
        if self.template:
            regex = self._msg_grammar(self.original_msg)
            self.templated_string = template_with_regex(self.template, regex, user=user)
        if self.mention:
            meta_data_msg = self._remove_bot_id(self.original_msg, self.bot_id)
        else:
            meta_data_msg = self.original_msg

        self.metadata = [{"name": "User", "value": user},
                         {"name": "Message", "value": meta_data_msg}]

    def in_output(self):
        """Concourse resource `in` main """

        output = {"version": self.version, "metadata": self.metadata,
                  "original_msg": self.original_msg}
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
