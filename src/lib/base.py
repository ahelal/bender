''' Base class and some helper functions'''
from __future__ import print_function

import os
import re
import sys

from jinja2 import StrictUndefined, Template, TemplateSyntaxError, UndefinedError
from slackclient import SlackClient


def template_str(text, variables):
    ''' Return a templated text '''
    # Merge ENV with variables passed
    os_env = {"ENV": os.environ}
    variables.update(os_env)

    try:
        return Template(text, undefined=StrictUndefined).render(variables)
    except TemplateSyntaxError as syntax_error:
        fail_unless(False, "Template syntax error. Template string: '{}'\n.{}".format(text, syntax_error))
    except UndefinedError as undefined_error:
        fail_unless(False, "Undefined variable. Template string: '{}'\n.{}".format(text, undefined_error))
    except TypeError as type_error:
        fail_unless(False, "Type error. Template string: '{}'\n.{}".format(text, type_error))

def template_with_regex(text, regex):
    ''' Add regex groupdict or groups to our environment'''
    extra_env = {}
    if regex and regex.groupdict():
        extra_env = {"regex": regex.groupdict()}
    elif regex and regex.groups():
        extra_env = {"regex": regex.groups()}
    return template_str(text, extra_env)

def write_to_file(content, output_file):
    ''' write content to output_file'''
    output_file_fd = open(output_file, 'w')
    print(content, file=output_file_fd)


def fail_unless(condition, msg):
    """If condition is not True print msg and exit with status code 1"""
    if not condition:
        print("{}".format(msg), file=sys.stderr)
        exit(1)


class Base(object): # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Slack Concourse resource implementation"""

    def __init__(self, **kwargs):
        self.slack_client = SlackClient(kwargs.get("slack_token"))
        self.bot = kwargs.get("bot", "bender")
        self.channel = kwargs.get("channel", "")
        self.grammar = kwargs.get("grammar", False)
        self.version = kwargs.get("version", False)
        self.working_dir = kwargs.get("working_dir", False)
        self.slack_unread = kwargs.get("slack_unread", False)
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
        regex = regex.match(direct_msg)

        return regex


    @staticmethod
    def _filter(items, return_field, filter_field, filter_value):
        for item in items:
            if filter_value == item.get(filter_field, None):
                return item.get(return_field, None)
        return None

    def _get_channel_group_id(self, channel_type):
        items = self._call_api("{}.list".format(
            channel_type), exclude_members=1)
        return self._filter(items[channel_type], "id", "name", self.channel)

    def _get_channel_group_info(self):
        # Try to get it from groups
        channel_id = self._get_channel_group_id("groups")
        if channel_id:
            return channel_id, "groups"

        # not a group try a channel
        channel_id = self._get_channel_group_id("channels")
        return channel_id, "channels"
