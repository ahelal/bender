''' Helper functions'''
from __future__ import print_function

import os
import sys

from jinja2 import (StrictUndefined, Template, TemplateSyntaxError, UndefinedError)


def fail_unless(condition, msg):
    """If condition is not True print msg and exit with status code 1"""
    if not condition:
        print("{}".format(msg), file=sys.stderr)
        exit(1)

def template_str(text, variables):
    ''' Return a templated text '''

    # Merge ENV with variables passed
    variables.update({"ENV": os.environ})
    try:
        return Template(text, undefined=StrictUndefined).render(variables)
    except TemplateSyntaxError as syntax_error:
        fail_unless(False, "Template syntax error. Template string: '{}'\n.{}".format(text, syntax_error))
    except UndefinedError as undefined_error:
        fail_unless(False, "Undefined variable. Template string: '{}'\n.{}".format(text, undefined_error))
    except TypeError as type_error:
        fail_unless(False, "Type error. Template string: '{}'\n.{}".format(text, type_error))

def template_with_regex(text, regex, **template_vars):
    ''' Add regex groupdict or groups to our environment'''
    if regex and regex.groupdict():
        template_vars.update({"regex": regex.groupdict()})
    elif regex and regex.groups():
        template_vars.update({"regex": regex.groups()})
    return template_str(text, template_vars)

def write_to_file(content, output_file):
    ''' write content to output_file'''
    output_file_fd = open(output_file, 'w')
    print(content, file=output_file_fd)

def read_if_exists(base_path, content):
    ''' Return content of file, if file exists else return content.'''
    path = os.path.abspath(os.path.join(base_path, str(content)))
    is_file = os.path.isfile(path)
    if is_file:
        return read_content_from_file(path)
    return content

def read_content_from_file(path):
    ''' Return content of file.'''
    try:
        with open(path) as file_desc:
            return file_desc.read()
    except IOError as file_error:
        fail_unless(False, "Failed to read file '{}'. IOError: '{}".format(path, file_error))

def list_get(a_list, idx, default=None):
    ''' Return index of a list if exists'''
    try:
        return a_list[idx]
    except IndexError:
        return default
