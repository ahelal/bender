#!/usr/bin/env python
''' The Check operation for bender resource'''
from __future__ import print_function

import json

from payload import PayLoad
from functions import list_get
from base import Base


class Check(Base):
    ''' Check resource'''
    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)
        self.checked_msg = []

    def _mark_read(self, timestamp):
        self._call_api(self.channel_type + ".mark",
                       channel=self.channel_id,
                       ts=timestamp)

    def _filter_msgs(self, messages, index):
        ''' Filter messages by type 'message' and regex match grammar'''
        for message in messages[:index]:
            if message.get("type") == "message" and self._msg_grammar(message.get("text")):
                self.checked_msg.append({"id_ts": message["ts"]})

    def check_logic_unread(self, max_api_count=1000, limit=5):
        """Concourse resource `check` logic using unread mark by slack"""
        unread_counter = True
        latest_ts = 0
        while unread_counter or limit >= 0:
            messages = self._call_api(self.channel_type + ".history",
                                      channel=self.channel_id,
                                      unreads=True,
                                      count=max_api_count,
                                      latest=latest_ts)
            limit -= 1
            if latest_ts == 0:
                unread_counter = messages.get("unread_count_display")
                mark_ts = list_get(messages["messages"], 0, {}).get("ts", False)
            latest_ts = list_get(messages["messages"], -1, {}).get("ts", 0)
            if messages["messages"] and 0 < unread_counter < max_api_count:
                self._filter_msgs(messages["messages"], unread_counter)
                unread_counter = 0
            elif messages["messages"] and unread_counter >= max_api_count:
                self._filter_msgs(messages["messages"], unread_counter)
                unread_counter -= max_api_count

        if mark_ts:
            # Mark that we read all unread msgs
            self._mark_read(mark_ts)

        if not self.checked_msg:
            # Sort messages by 'ts' chronologically
            self.checked_msg = sorted(self.checked_msg, key=lambda k: k['id_ts'])

    def check_logic_concourse(self, max_api_count=1000, limit=5):
        """Concourse resource `check` logic using version passed by concourse."""
        oldest = self.version.get("id_ts", 0)
        has_more = True
        while has_more and limit >= 0:
            messages = self._call_api(self.channel_type + ".history",
                                      channel=self.channel_id,
                                      count=max_api_count,
                                      oldest=oldest)
            limit -= 1
            has_more = messages.get("has_more")
            if messages["messages"]:
                oldest = messages["messages"][-1]["ts"]
                self._filter_msgs(messages["messages"], len(messages["messages"]))

        if not self.checked_msg:
            # Sort messages by 'ts' chronologically
            self.checked_msg = sorted(self.checked_msg, key=lambda k: k['id_ts'])
            if not self.version.get("id_ts"):
                # if we don't have version passed. So report latest only
                try:
                    self.checked_msg = [self.checked_msg[0]]
                except IndexError:
                    self.checked_msg = []

    def check_output(self):
        """Concourse resource `check` output """
        print(json.dumps(self.checked_msg, indent=4, sort_keys=True))

def main():
    """Concourse resource `check` main """
    payload = PayLoad()
    slack_client = Check(**payload.args)
    if slack_client.slack_unread:
        slack_client.check_logic_unread()
    else:
        slack_client.check_logic_concourse()
    slack_client.check_output()

if __name__ == '__main__':
    main()
