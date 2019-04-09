#  Copyright 2019 Jacques Supcik
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

""" Constants and functions to handle LaTeX in Jinja2 templates """

import os
import re

import jinja2

LATEX_SUBS = (
    (re.compile(r'\\'), r'\\textbackslash'),
    (re.compile(r'([{}_#%&$])'), r'\\\1'),
    (re.compile(r'~'), r'\~{}'),
    (re.compile(r'\^'), r'\^{}'),
    (re.compile(r'"(.*?)"'), r"``\1''"),
    (re.compile(r'\.\.\.+'), r'\\ldots'),
    (re.compile(r'\x92'), r"'"),
    (re.compile(r'\x85'), r'\\ldots{} '),
    (re.compile(r'\x96'), r'--'),
    # (re.compile(r'/'), r'\/'),
)


def latex_env(loader=jinja2.FileSystemLoader(os.path.abspath('.'))):
    """ Returns a Jinja2 environment for latex """
    env = jinja2.Environment(
        block_start_string=r'\BLOCK{',
        block_end_string=r'}',
        variable_start_string=r'\VAR{',
        variable_end_string=r'}',
        comment_start_string=r'\#{',
        comment_end_string=r'}',
        line_statement_prefix=r'%%',
        line_comment_prefix=r'%#',
        trim_blocks=True,
        autoescape=False,
        loader=loader,
    )

    def escape_tex(value):
        newval = value
        for pattern, replacement in LATEX_SUBS:
            newval = pattern.sub(replacement, newval)
        return newval

    def cell_break(value):
        value = re.sub(r'\r?\n', r'\\newline{}', value)
        return value

    def line_break(value):
        value = re.sub(r'\r?\n', r'\\\\\n', value)
        return value

    env.filters['escape_tex'] = escape_tex
    env.filters['cell_break'] = cell_break
    env.filters['line_break'] = line_break

    return env
