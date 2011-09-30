# -*- coding: utf-8 -*-
"""
    Storage APIs

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from collections import defaultdict


_events = defaultdict(list)


def subscribe(event, func):
    if func not in _events[event]:
        _events[event].append(func)


def notify(event, *args, **kw):
    for func in _events[event]:
        func(*args, **kw)


def unsubscribe(event, func):
    if func in _events[event]:
        _events[event].remove(func)
