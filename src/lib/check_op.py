#!/usr/bin/env python
''' The Check operation for bender resource'''
from __future__ import print_function

import json

from payload import PayLoad
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

    def _parse_msgs(self, messages, index):
        for message in messages[:index]:
            # Ignore non message types and grammar must match
            if message.get("type", "") == "message" and self._msg_grammar(message.get("text", False)):
                self.checked_msg.append({"id_ts": message["ts"]})

    def check_logic(self, max_api_count=100):
        """Concourse resource `check` logic """
        # TODO: (A) Simplify that logic and (B) Add concourse logic of checking from last version (will be damn slow)
        latest_ts = 0
        msgs_2_return = max_api_count
        unread_counter = 1
        mark_ts = False
        while unread_counter:
            messages = self._call_api(self.channel_type + ".history",
                                      channel=self.channel_id,
                                      unreads=True,
                                      count=msgs_2_return,
                                      latest=latest_ts)

            if not mark_ts:
                # first time in the loop. Check if we have no new unread msg
                unread_counter = messages["unread_count_display"]
                if unread_counter == 0:
                    break
                mark_ts = messages["messages"][0]["ts"]

            if msgs_2_return >= unread_counter:
                self._parse_msgs(messages["messages"], unread_counter)
                break
            elif unread_counter <= 0:
                break
            elif unread_counter >= max_api_count:
                # special case if we have a huge backlog we can only get max_api_count msg at a time
                self._parse_msgs(messages["messages"], max_api_count)
                msgs_2_return = max_api_count
                unread_counter -= msgs_2_return
            else:
                self._parse_msgs(messages["messages"], unread_counter)
                msgs_2_return = unread_counter - msgs_2_return
                unread_counter -= msgs_2_return
            # Get ts for our next read message.
            latest_ts = messages["messages"][-1]["ts"]

        if not self.checked_msg:
            # Sort messages by ts chronological
            self.checked_msg = sorted(self.checked_msg, key=lambda k: k['id_ts'])

        if mark_ts:
            # Mark last point (if needed) to make next lookup faster
            self._mark_read(mark_ts)
        return mark_ts

    def check_output(self):
        """Concourse resource `check` output """
        print(json.dumps(self.checked_msg, indent=4, sort_keys=True))

def main():
    payload = PayLoad()
    slack_client = Check(**payload.args)

    slack_client.check_logic()
    slack_client.check_output()

if __name__ == '__main__':
    main()
