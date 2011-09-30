# -*- coding: utf-8 -*-
""" Dynamic web app generated with a rbr file

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import json
from pprint import pprint
from StringIO import StringIO

from webob.exc import HTTPError

from redbarrel.util import reST2HTML, translate
from redbarrel.dsl.runners import resolve_runner


class WebHook(dict):

    def __init__(self, data=None, types_=None):
        if data is None:
            data = {}
        self.types = {'float': float,
                      'json': json.loads,
                      'int': int}

        # adding custome types
        if types_ is not None:
            self.types.update(types_)

        super(WebHook, self).__init__(data)

    def _check_type(self, type_, value, code):
        # XXX we should keep the value converted, no ?
        if type_ in self.types:
            try:
                self.types[type_](value)
            except ValueError, e:
                err = HTTPError()
                err.status_int = code
                body = StringIO()
                pprint(str(e), body)
                body.seek(0)
                err.body = body.read()
                raise err
        else:
            raise NotImplementedError(type_)

    def _execute_resp_body(self, response, rule, request, globs):
        if rule.type == 'check_type':
            self._check_type(rule.value, response.body, rule[2])
        elif rule.type == 'alter':
            alterator = resolve_runner(rule.value)
            response.body = alterator(globs, request, response.body)
        else:
            raise NotImplementedError(str(rule))

    def _execute_resp_headers(self, response, rule, request, globs):
        if rule.type == 'set':
            response.headers[rule.left] = rule.right.value
        else:
            raise NotImplementedError(str(rule))

    def _execute_req_headers(self, request, rule, globs):
        if rule[0] == 'validates_with':
            header = rule[1]
            validator = resolve_runner(rule[2])
            code = rule[3]

            def _failed(e):
                err = HTTPError()
                err.status_int = code
                body = StringIO()
                pprint(str(e), body)
                body.seek(0)
                err.body = body.read()
                raise err

            value = request.headers.get(header)
            try:
                validator(globs, request, value)
            except Exception, e:
                _failed(e)
        else:
            raise NotImplementedError(str(rule))

    def _execute_req_body(self, request, rule, globs):
        if rule[0] == 'check_type':
            self._check_type(rule[1], request.body, rule[2])
        else:
            raise NotImplementedError(str(rule))

    def describe(self, field):
        rules = self.get(field, [])
        for rule in rules:
            if rule.value.type == 'description':
                return reST2HTML(rule.value.value)
        return ''

    def has_rules(self, field):
        rules = self.get(field, [])
        if (len(rules) == 0 or
            (len(rules) == 1 and rules[0].value.type == 'description')):
            return False
        return True

    def translate(self, field, part=''):
        return translate(self.get(field, []), part)

    def _cleanup_rules(self, rules):
        if isinstance(rules, tuple):
            rules = [rules]
        res = []
        for rule in rules:
            # might want to clean up the AST before
            if rule.type == 'val':
                rule = rule.value
            if rule.type == 'description':
                continue
            res.append(rule)
        return res

    def postconditions(self, response, request, globs):
        if 'response-headers' in self:
            for rule in self._cleanup_rules(self['response-headers']):
                self._execute_resp_headers(response, rule, request, globs)

        if 'response-body' in self:
            for rule in self._cleanup_rules(self['response-body']):
                self._execute_resp_body(response, rule, request, globs)

    def preconditions(self, request, globs):
        if 'request-headers' in self:
            for rule in self._cleanup_rules(self['request-headers']):
                self._execute_req_headers(request, rule, globs)

        if 'request-body' in self:
            for rule in self._cleanup_rules(self['request-body']):
                self._execute_req_body(request, rule, globs)
