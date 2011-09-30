""" Dynamic web app generated with a RBR file

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import os
import sys
import mimetypes

from webob.dec import wsgify
from webob.exc import HTTPNotFound, HTTPFound
from webob import Response

from redbarrel.appview import AppView
from redbarrel.libraries import Library

from mako.template import Template
from webob import Response


_MEDIA = os.path.join(os.path.dirname(__file__), 'media')
_PREFIXES = ['python', 'file', 'proxy', 'directory']

_DEFAULT_APP = """\
root %(root)s;

meta (
    description \"\"\"%(description)s\"\"\",
    title "%(name)s",
    version 1.0
);


"""

# XXX can be configured
_LIBS = os.path.join(os.path.dirname(__file__), 'libs')
_APPS = os.path.join(os.path.dirname(__file__), 'apps')


def by_len(path1, path2):
    return cmp(len(path1), len(path2))


class WebApp(object):
    """
    Top application. Display built-in views and delegate calls to WebMapper
    """
    def __init__(self, rbrs, worker=None):
        self.rbrs = rbrs
        self.worker = worker
        self.libdir = _LIBS
        self.libraries = self._load_libs()
        self.appdir = _APPS
        self.appviews = self._load_apps()

    def _load_apps(self):
        appviews = []
        # provided RBRs
        for rbr in self.rbrs:
            appview = AppView(self, rbr)
            appview.generate()
            appviews.append((appview.get_root(), appview))

        # disk-based RBRs
        for path in os.listdir(self.appdir):
            full = os.path.join(self.appdir, path)
            if not os.path.isdir(full):
                continue
            rbr = os.path.join(full, 'definitions.rbr')
            appview = AppView(self, rbr)
            appview.generate()
            appviews.append((appview.get_root(), appview))

        appviews.sort(by_len)
        return appviews

    def _load_libs(self):
        libs = []
        for element in os.listdir(self.libdir):
            path = os.path.join(self.libdir, element)
            libs.append(Library(path))
        return libs

    def _media(self, request):
        path = request.path_info[len('/__media__/'):]
        # make sure the path does not start with a dot
        if path.startswith('.') or path.strip() == '.':
            raise HTTPNotFound()
        fullpath = os.path.join(_MEDIA, path)
        if not os.path.exists(fullpath) or not os.path.isfile(fullpath):
            raise HTTPNotFound()

        mimetype = mimetypes.guess_type(fullpath)[0]
        with open(fullpath) as f:
            return Response(f.read(), content_type=mimetype)

    def _lib(self, request):
        name = request.path.split('/')[-1]
        slib = None
        for lib in self.libraries:    # XXX use a dict
            if lib.name == name:
                slib = lib
                break

        if request.POST:
            data  = request.POST['data']
            data = data.replace('\r\n', '\n')   # XXX
            slib.update(data)

        here = os.path.dirname(__file__)
        tmpl = os.path.join(here, 'templates', 'lib.mako')
        with open(tmpl) as f:
            tmpl = Template(f.read())
        return tmpl.render(lib=slib)

    def _main(self, request):
        if request.path == '/__main__':
            here = os.path.dirname(__file__)
            tmpl = os.path.join(here, 'templates', 'main.mako')
            with open(tmpl) as f:
                tmpl = Template(f.read())

            return tmpl.render(appviews=self.appviews,
                               libraries=self.libraries)

        if request.path == '/__main__/add' and request.method == 'POST':
            def _name2path(name):
                # MORE CHARS
                path = name.lower()
                path = path.replace(' ', '')
                return '/' + path

            data = {}
            data['name'] = request.POST['name']
            data['root'] = _name2path(data['name'])
            data['description'] = request.POST['description']
            rbr = _DEFAULT_APP % data
            appview = AppView(self, rbr)
            appview.generate()
            self.appviews.append((appview.get_root(), appview))
            self.appviews.sort(by_len)
            # XXX
            url = 'http://%s%s/__editor__' % (request.environ['HTTP_HOST'],
                                        appview.get_root())
            return HTTPFound(location=url)

        if request.path == '/__main__/addlib' and request.method == 'POST':
            # loading a new lib
            name = request.POST['name']
            file_ = request.POST['file']
            if hasattr(file_, 'file'):
                code = file_.file.read()
            else:
                code = ''
            self.libraries.append(Library(code, name))
            # XXX
            url = 'http://%s/__lib__/%s' % (request.environ['HTTP_HOST'], name)
            return HTTPFound(location=url)


        raise HTTPNotFound()

    @wsgify
    def __call__(self, request):
        path = request.path
        if path.startswith('/__media__'):
            return self._media(request)

        if path.startswith('/__main__'):
            return self._main(request)

        if path.startswith('/__lib__'):
            return self._lib(request)

        # pre-matching
        for root, app in self.appviews:
            if path.startswith(root):
                return app(request)

        raise HTTPNotFound(request)


if __name__ == '__main__':
    from socketio import SocketIOServer
    app = WebApp([sys.argv[1]])
    server = SocketIOServer(('', 8000), app, resource='socket.io')
    print("Serving on port 8000...")
    server.serve_forever()
