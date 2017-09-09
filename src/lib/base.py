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
        self.users = self._call_api("users.list", presence=0)
        self.mention = kwargs.get("mention")
        if self.mention:
            self.bot_id = self._filter(self.users['members'], "id", "name", self.bot)
            fail_unless(self.bot_id, "Unable to find bot name '{}'".format(self.bot))
        if not self.grammar and not self.mention:
            fail_unless(False, "At least one parameter is required 'grammar', 'mention'.")

        self.channel_id, self.channel_type = self._get_channel_group_info()
        fail_unless(self.channel_id, "Unable to find channel/group '{}'".format(self.channel))

    def _call_api(self, method, **kwargs):
        """Interface to Slack API"""
        api_response = self.slack_client.api_call(method, **kwargs)
        response_status = api_response.get("ok", False)
        fail_unless(response_status, "Slack API Call failed. method={} response={}".format(method, api_response))
        return api_response

    @staticmethod
    def _remove_bot_id(msg, bot_id):
        '''Return a text after removing <@BOT_NAME> from message.'''
        regex = re.compile(r"^(\s+)?<@{}>(.*)".format(bot_id))
        regex = regex.match(msg)
        if not regex:
            return None
        return regex.groups()[1].strip()

    def _msg_grammar(self, msg):
        ''' Return only message if grammar is not defined. Return regex if grammar is defined. And None if no match'''
        if self.mention:
            msg = self._remove_bot_id(msg, self.bot_id)
            if not self.grammar or not msg:
                # No grammar rule or or no mention of the bot, Just return msg
                return msg
        try:
            regex = re.compile(r"{}".format(self.grammar))
        except re.error as regex_error:
            fail_unless(False, "The grammar expression '{}' has an error : {}".format(self.grammar, regex_error))

        return regex.match(msg)

    @staticmethod
    def _filter(items, return_field, filter_field, filter_value):
        '''Return 'return_field' if filter_value in items filter_field else return none'''
        for item in items:
            if filter_value == item.get(filter_field, None):
                return item.get(return_field, None)
        return None

    def _get_channel_group_id(self, channel_type):
        items = self._call_api("{}.list".format(channel_type), exclude_members=1)
        return self._filter(items[channel_type], "id", "name", self.channel)

    def _get_channel_group_info(self):
        '''Return ID and type of channel (channel|groups)'''
        channel_id = self._get_channel_group_id("groups")
        if channel_id:
            return channel_id, "groups"
        channel_id = self._get_channel_group_id("channels")
        return channel_id, "channels"
