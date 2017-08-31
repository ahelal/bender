''' Base class and some helper functions'''
from __future__ import print_function

import re

from slackclient import SlackClient
from functions import fail_unless

class Base(object): # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Slack Concourse resource implementation"""

    def __init__(self, **kwargs):
        self.slack_client = SlackClient(kwargs.get("slack_token"))
        self.bot = kwargs.get("bot_name")
        self.channel = kwargs.get("channel")
        self.grammar = kwargs.get("grammar")
        self.version = kwargs.get("version")
        self.working_dir = kwargs.get("working_dir")
        self.slack_unread = kwargs.get("slack_unread")
        # Get all user list
        self.users = self._call_api("users.list", presence=0)
        # find my id `the bot`
        self.bot_id = self._filter(self.users['members'], "id", "name", self.bot)
        fail_unless(self.bot_id, "Unable to find bot name '{}'".format(self.bot))
        # Get channel/group ID
        self.channel_id, self.channel_type = self._get_channel_group_info()
        fail_unless(self.channel_id, "Unable to find channel '{}'".format(self.channel))

    def _call_api(self, method, **kwargs):
        """Interface to slack API"""
        api_response = self.slack_client.api_call(method, **kwargs)
        response_ok = api_response.get("ok", False)
        fail_unless(response_ok, "Failed to do API request to Slack. method={} response={}".format(method, api_response))
        return api_response

    @staticmethod
    def _remove_botname(msg, bot_id):
        regex = re.compile(r"^(\s+)?<@{}>(.*)".format(bot_id))
        regex = regex.match(msg)
        if not regex:
            return None
        return regex.groups()[1].strip()

    def _msg_grammar(self, msg):
        direct_msg = self._remove_botname(msg, self.bot_id)
        if not self.grammar or not direct_msg:
            # We don't have grammar rules or if our not a direct msg to the bot.
            # Just return direct_msg
            return direct_msg
        try:
            regex = re.compile(r"{}".format(self.grammar))
        except re.error as regex_error:
            fail_unless(False, "The grammar expression '{}' has an error : {}".format(self.grammar, regex_error))
        return  regex.match(direct_msg)


    @staticmethod
    def _filter(items, return_field, filter_field, filter_value):
        for item in items:
            if filter_value == item.get(filter_field, None):
                return item.get(return_field, None)
        return None

    def _get_channel_group_id(self, channel_type):
        items = self._call_api("{}.list".format(channel_type), exclude_members=1)
        return self._filter(items[channel_type], "id", "name", self.channel)

    def _get_channel_group_info(self):
        # Try to get it from groups
        channel_id = self._get_channel_group_id("groups")
        if channel_id:
            return channel_id, "groups"
        # not a group try a channel
        channel_id = self._get_channel_group_id("channels")
        return channel_id, "channels"
