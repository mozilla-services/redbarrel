# -*- coding: utf-8 -*-
"""
    Contains the pistil server + workervarious helpers.

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from gevent import monkey

monkey.noisy = False
monkey.patch_all()
