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
    defines the RedBarrel DSL.

"""
import ply.yacc as yacc

# importing this builds the lexer
from redbarrel.dsl.lexer import *   # NOQA


#
# classes that represent AST nodes
#

class BaseToken(object):
    def _typ(self, attr):
        if isinstance(attr, str):
            return '"%s"' % attr
        return attr

    def _col(self, attr, no_typing=False):
        if not hasattr(attr, 'collapse'):
            if no_typing:
                return attr
            else:
                return self._typ(attr)
        return attr.collapse()


class Value(BaseToken):
    def __init__(self, value):
        self.type = 'val'
        self.value = value

    def collapse(self):
        return self._col(self.value)


class Statement(BaseToken):

    pattern = '%s %s'
    type = 'assign'
    description = '%s %s'

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def collapse(self):
        return self.pattern % (self._col(self.left, True),
                               self._col(self.right))

    def __str__(self):
        return self.description % (self._col(self.left),
                                   self._col(self.right))


class Global(Statement):
    pattern = 'global %s %s;'
    type = 'global'


class Type(Statement):
    pattern = 'type %s %s;'
    type = 'type'


class Worker(Statement):
    pattern = 'worker %s %s;'
    type = 'worker'


class Arbiter(Statement):
    pattern = 'arbiter %s %s;'
    type = 'arbiter'


class Variable(object):
    type = 'var'
    pattern = '%s'
    description = '%s'

    def __init__(self, value):
        self.value = value

    def _col(self, value):
        if hasattr(value, 'collapse'):
            return self.value.collapse()
        return str(self.value)

    def collapse(self):
        return self.pattern % self._col(self.value)

    def __str__(self):
        return self.description % self._col(self.value)


class Socket(Variable):
    type = 'socket'
    pattern = 'socket %s;'


class Meta(Variable):
    type = 'meta'
    pattern = 'meta (\n%s\n);'


class Root(Variable):
    type = 'root'
    pattern = 'root %s;'


class Definition(Statement):
    type = 'def'
    pattern = 'path %s (\n%s\n);'


class TypeChecker(Statement):
    type = 'check_type'


class Alter(Variable):
    type = 'alter'
    pattern = 'alter with %s'
    description = 'The result is altered by %r'


class Describe(Statement):
    type = 'describe'
    pattern = 'describe %s %s'
    description = '%s %s'


class Set(Statement):
    type = 'set'
    pattern = 'set %s %s'
    description = '%r is %r'


class OnError(Variable):
    type = 'onerror'
    pattern = 'on error return %s'


class CheckNotType(object):
    type = 'check_not_type'
    pattern = 'unless %s type is not %s return %s'
    description = '%s should not be of type %s. A %s is returned otherwise'

    def __init__(self, name, type, code):
        self.name = name
        self.type = type
        self.code = code

    def _col(self, attr):
        if not hasattr(attr, 'collapse'):
            return str(attr)
        return attr.collapse()

    def collapse(self):
        return self.pattern % (self._col(self.name),
                               self._col(self.type),
                               self._col(self.code))

    def __str__(self):
        return self.description % (self._col(self.name),
                                   self._col(self.type),
                                   self._col(self.code))


class CheckIsType(CheckNotType):
    type = 'check_is_type'
    pattern = 'unless %s type is %s return %s'
    description = '%s should be of type %s. A %s is returned otherwise'


class ValidatesWith(CheckNotType):
    type = 'validates_with'
    pattern = 'unless %s validates with %s return %s'
    description = '%r is validated with %r. A %s is returned if it does not.'


class CheckType(Statement):
    type = 'statement'
    pattern = 'unless type is %s return %s'
    description = 'The type is %r. A %s is returned otherwise'


class Description(Variable):
    type = 'description'
    pattern = 'description %s'


class Verb(object):
    def __init__(self, verb):
        self.type = 'verb'
        self.verb = verb

    def collapse(self):
        return self.verb

    def __str__(self):
        return self.verb


class Verbs(list):
    def collapse(self):
        return '|'.join([verb.collapse() for verb in self])



#
# The actual parser
#

def p_program(p):
    """program : definitions
    """
    p[0] = p[1]


def p_path_definitions(p):
    """definitions :
                   | definitions definition
    """
    if len(p) == 1:
        p[0] = list()
    else:
        p[1].append(p[2])
        p[0] = p[1]


def p_path_definition(p):
    """definition : PATH NAME LP statements RP SEMI
                  | META LP statements RP SEMI
                  | GLOBAL NAME value SEMI
                  | TYPE NAME PREFIXED_NAME SEMI
                  | WORKER NAME PREFIXED_NAME SEMI
                  | ARBITER NAME PREFIXED_NAME SEMI
                  | ROOT URLVALUE SEMI
    """
    if p[1] == 'meta':
        p[0] = Meta(p[3])
    elif p[1] == 'global':
        p[0] = Global(p[2], p[3])
    elif p[1] == 'type':
        p[0] = Type(p[2], p[3])
    elif p[1] == 'worker':
        p[0] = Worker(p[2], p[3])
    elif p[1] == 'arbiter':
        p[0] = Arbiter(p[2], p[3])
    elif p[1] == 'socket':
        p[0] = Socket(p[2])
    elif p[1] == 'root':
        p[0] = Root(p[2])
    else:
        p[0] = Definition(p[2], p[4])


def p_statements(p):
    """statements : statements COMMA statement
                  | statements COMMA
                  | statement
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = p[1]
    else:
        p[0] = p[1] + [p[3]]


def p_values(p):
    """values : value
              | values COMMA value
              | values COMMA
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = p[1]
    else:
        p[0] = p[1] + [p[3]]


def p_command(p):
    """command : UNLESS         TYPE  IS        NAME RETURN         CODE
        | UNLESS         TYPE  IS        NOT  NAME           RETURN CODE
        | UNLESS         NAME  TYPE      IS   NAME           RETURN CODE
        | UNLESS         NAME  TYPE      IS   NOT            NAME   RETURN CODE
        | UNLESS         NAME  VALIDATES WITH NAME           RETURN CODE
        | UNLESS         NAME  VALIDATES WITH PREFIXED_NAME  RETURN CODE
        | ON             ERROR RETURN    CODE
        | SET            NAME  value
        | DESCRIBE       CODE TEXT
        | DESCRIPTION    TEXT
        | ALTER          WITH PREFIXED_NAME
    """
    if len(p) == 7:
        p[0] = CheckType(p[4], p[6])
    elif len(p) == 8 and p[2] != 'type':
        if p[3] == 'type':
            klass = CheckIsType
        else:
            klass = ValidatesWith
        p[0] = klass(p[2], p[5], p[7])
    elif len(p) == 5:
        p[0] = OnError(p[4])
    elif len(p) == 9:
        p[0] = CheckNotType(p[2], p[6], p[8])
    elif len(p) == 4:
        if p[1] == 'describe':
            p[0] = Describe(p[2], p[3])
        elif p[1] == 'alter':
            p[0] = Alter(p[3])
        elif p[1] == 'set':
            p[0] = Set(p[2], p[3])
        else:
            raise NotImplementedError(p[1:])
    elif len(p) == 3:
        if p[1] == 'description':
            p[0] = Description(p[2])
        else:
            raise NotImplementedError(p[1:])


def p_verbs(p):
    """verbs : VERB
             | verbs PIPE VERB
    """
    if len(p) == 4:
        p[0] = Verbs(p[1]) + Verbs([Verb(p[3])])
    else:
        p[0] = Verbs([Verb(p[1])])


def p_value(p):
    """value : command
             | INT
             | FLOAT
             | verbs
             | URLVALUE
             | TEXT
             | FILE
             | DIRECTORY
             | PROXY
             | DOTTED_NAME
             | PREFIXED_NAME
    """
    p[0] = Value(p[1])


def p_variable(p):
    """variable : METHOD
                | URL
                | NAME
    """
    p[0] = Variable(p[1])


def p_statement(p):
    """statement : variable LP values RP
                 | variable value
                 | DESCRIPTION TEXT
    """
    if p[2] == '(':
        p[0] = Statement(p[1], p[3])
    else:
        p[0] = Statement(p[1], p[2])


def p_error(t):
    if t is None:
        # eof
        raise SyntaxError('Could not read the file.')
    else:
        raise SyntaxError("%r, line %d" % (t.value, t.lineno))


# generates the parser
yacc.yacc()
