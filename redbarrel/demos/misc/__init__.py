# -*- coding: utf-8 -*-
"""
    Demos

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import json
import cssmin


#
# simplest app
#
def hello(globs, request):
    return 'Hello, World'


#
# a controller with a state (not thread-safe)
#
class CountController(object):
    def __init__(self):
        self.counter = 0

    def __call__(self, globs, request):
        try:
            return '%d' % self.counter
        finally:
            self.counter += 1


counter = CountController()


# a web page
def html(globs, req):
    return """
    <html>
      <body>
        <div>Hello</div>
      </body>
    </html>
    """


# a web service
def capitalize(globs, req):
    return json.dumps(json.loads(req.body).capitalize())


def auth(header):
    """Authorization check"""
    if header is None:
        raise Exception('Unauthorized')
    # whatever works...


def compress_css(globs, request, css):
    """Compress the css using cssmin"""
    return cssmin.cssmin(css)


#
# a counter using a global + a config file
#
class MyApp(object):
    def __init__(self, globs):
        self.counter = 0  # int(globs['config'])


def app(globs):
    return MyApp(globs)


def counter2(globs, request):
    app = globs['app']
    try:
        return '%d' % app.counter
    finally:
        app.counter += 1


def blobish(globs, request):
    return 'OK'


# check and return the new value
# # XXX not clear yet about converting here
# and the full rol of this function
class blob(object):
    def __call__(self, value):
        return True
