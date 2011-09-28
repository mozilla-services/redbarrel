# -*- coding: utf-8 -*-
# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is Sync Server
#
# The Initial Developer of the Original Code is the Mozilla Foundation.
# Portions created by the Initial Developer are Copyright (C) 2010
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   See AUTHORS.txt
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK *****

"""
    defines the RedBarrel Lexer
"""
import ply.lex as lex


reserved = {
    'path': 'PATH',
    'meta': 'META',
    'worker': 'WORKER',
    'arbiter': 'ARBITER',
    'unless': 'UNLESS',
    'validates': 'VALIDATES',
    'with': 'WITH',
    'not': 'NOT',
    'is': 'IS',
    'on': 'ON',
    'error': 'ERROR',
    'return': 'RETURN',
    'type': 'TYPE',
    'set': 'SET',
    'alter': 'ALTER',
    'describe': 'DESCRIBE',
    'description': 'DESCRIPTION',
    'global': 'GLOBAL',
    'root': 'ROOT'}


tokens = ['DOTTED_NAME', 'PREFIXED_NAME', 'NAME', 'LP', 'RP', 'COMMA', 'CODE',
          'INT', 'FILE', 'DIRECTORY', 'FLOAT', 'METHOD', 'VERB', 'URL',
          'URLVALUE', 'TEXT', 'SEMI', 'PROXY', 'PIPE'] + reserved.values()

literals = ''


def t_FILE(t):
    r'file:[a-zA-Z0-9_\./\\]*'
    return t


def t_DIRECTORY(t):
    r'directory:[a-zA-Z0-9_\./\\]*'
    return t


def t_DOTTED_NAME(t):
    r'([a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)+)+'
    return t


def t_PREFIXED_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*:([a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)+)+'  # NOQA
    return t


# will do better later -- more chars allowed
def t_PROXY(t):
    r'proxy:(http|https):\/\/[a-zA-Z0-9_:~\-]*'  # NOQA
    return t


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_\-]*'
    if t.value in VERBS:
        t.type = 'VERB'
    else:
        t.type = reserved.get(t.value, 'NAME')
    return t


def t_CODE(t):
    r'\d\d\d'
    t.value = int(t.value)
    return t


def t_TEXT(t):
    r'(?ms)("""(.*?)""")|(\"([^\\\n]|(\\.))*?\")'
    if t.value.startswith('"""'):
        t.value = t.value[3:-3]
    else:
        t.value = t.value[1:-1]
    return t


t_PIPE = r'\|'
t_SEMI = r';'
t_URL = r'url'
t_URLVALUE = r'/[a-zA-Z0-9\.~\{\}:\[\]+\-_/\*\$\(\)\?\<\>]*'  # incomplete
t_METHOD = r'method'
t_COMMA = r','
t_LP = r'\('
t_RP = r'\)'
t_INT = r'\d+'
t_FLOAT = r'\d+\.\d+'
t_ignore = " \t"
t_ignore_COMMENT = r'\#.*?$'


VERBS = ('POST', 'GET', 'DELETE', 'PUT', 'HEAD', 'TRACE',
         'OPTIONS', 'CONNECT')


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    raise SyntaxError("%r, line %d" % (t.value[0], t.lineno))
    #t.lexer.skip(1)


lex.lex()
