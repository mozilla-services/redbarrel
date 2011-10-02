""" App editor.

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import os
import sys

from mako.template import Template
from webob import Response
from webob.exc import HTTPFound

from redbarrel.util import reST2HTML
from redbarrel.application import RedBarrelApplication


_MEDIA = os.path.join(os.path.dirname(__file__), 'media')
_PREFIXES = ['python', 'file', 'proxy', 'directory']
_META = ('global', 'type', 'worker', 'arbiter')

_PATH = """\
path %(name)s (
    use %(use)s,
    url %(url)s,
    method %(methods)s,
    description \"\"\"%(description)s\"\"\",
    response-headers (
        set Content-Type "%(content_type)s"
    )
);

"""

class AppView(object):
    def __init__(self, wsgiapp, location=None, rbr=None, code=None,
                 name='undefined'):
        self.wsgiapp = wsgiapp
        self.app = RedBarrelApplication(location=location,
                                        rbr_content=rbr,
                                        app_content=code,
                                        name=name,
                                        context=self.wsgiapp)   # XXX ugly

    def get_root(self):
        return self.app.get_root()

    def generate(self):
        self.app.generate()

    def _apis(self):
        return Response(self.app.rbr_content,
                        content_type='text/plain')

    def which_lib(self, callable):
        lib, callable = callable.split('.', 1)
        url = '%s/__editor__/editapp?lib=%s' % (self.app.get_root(),
                                                callable)
        return url   #'/__lib__/%s' % lib

    def _edit(self, path):
        here = os.path.dirname(__file__)
        tmpl = os.path.join(here, 'templates', 'edit.mako')
        with open(tmpl) as f:
            tmpl = Template(f.read())

        options = self.app.get_options()

        if 'title' in options:
            title = options['title']
            if 'version' in options:
                title += ' v%s' % options['version']
        else:
            title = 'Redbarrel Services'


        return tmpl.render(path=path,
                           name=path[1],
                           defs=self.app.get_hooks(),
                           options=options,
                           rst2HTML=reST2HTML,
                           which_lib=self.which_lib,
                           app=self.app,
                           approot=self.app.get_root(),
                           libs=self.wsgiapp.libraries,
                           title=title)

    def _editapp(self, request):
        here = os.path.dirname(__file__)
        tmpl = os.path.join(here, 'templates', 'appcode.mako')
        with open(tmpl) as f:
            tmpl = Template(f.read())

        if request.POST:
            data  = request.POST['data']
            data = data.replace('\r\n', '\n')   # XXX
            self.app.update_code(data)
            self.app.sync()

        options = self.app.get_options()

        if 'title' in options:
            title = options['title']
            if 'version' in options:
                title += ' v%s' % options['version']
        else:
            title = 'Redbarrel Services'

        return tmpl.render(app=self.app,
                           options=options,
                           rst2HTML=reST2HTML,
                           which_lib=self.which_lib,
                           libs=self.wsgiapp.libraries,
                           title=title)

    def _doc(self):
        here = os.path.dirname(__file__)
        tmpl = os.path.join(here, 'templates', 'doc.mako')
        with open(tmpl) as f:
            tmpl = Template(f.read())

        options = self.app.get_options()

        if 'title' in options:
            title = options['title']
            if 'version' in options:
                title += ' v%s' % options['version']
        else:
            title = 'Redbarrel Services'

        return tmpl.render(defs=self.app.get_hooks(),
                           options=options,
                           rst2HTML=reST2HTML,
                           which_lib=self.which_lib,
                           approot=self.app.get_root(),
                           app=self.app,
                           libs=self.wsgiapp.libraries,
                           title=title)

    def _rooted(self, path):
        return '%s/%s' % (self.get_root(), path.lstrip('/'))

    def editing(self, request):
        if request.path == self._rooted('/__editor__'):
            return self._doc()

        editor_path = request.path.split('__editor__/')[-1]
        parts = editor_path.split('/')

        if parts == ['editapp'] and request.method in ('GET', 'POST'):
            return self._editapp(request)

        if parts == ['newpath'] and request.method == 'POST':
            # adding a new path

            data = {}
            description = request.POST['description']
            data['description'] = description.replace('\r', '')
            data['url'] = request.POST['url']
            methods = request.POST['method']
            if isinstance(methods, unicode):
                methods = [methods]
            data['methods'] = '|'.join(methods)
            data['name'] = request.POST['name']
            data['use'] = request.POST['use']
            content_type = request.POST['content-type']
            if content_type == 'other':
                content_type = request.POST['content-type-value']
            data['content_type'] = content_type
            definition = _PATH % data
            try:
                self.app.add_content(definition)
                return HTTPFound(location=self.app.get_root() + '/__editor__')
            except Exception, e:
                return 'Definition: %r\nError: %s' % (definition, str(e))

        if len(parts) == 2 and parts[0] == 'delete':
            path_id = parts[-1]
            self.app.del_def(path_id)
            raise HTTPFound(location=self.app.get_root() + '/__editor__')

        if len(parts) == 2 and parts[0] == 'edit':
            path_id = parts[-1]
            path_def = None
            for definition in self.app.ast:
                if definition[0] == 'def' and definition[1] == path_id:
                    path_def = definition
                    break

            if path_def is not None:
                return self._edit(path_def)

        raise NotImplementedError()

    def _edit_path(self, path):
        raise NotImplementedError()

    def __call__(self, request):
        # the __api__ page returns the rbr file
        if request.path == self._rooted('/__api__'):
            return self._apis()

        # to deprecate
        if request.path == self._rooted('/__doc__'):
            return self._doc()

        # anything that starts with /__editor__ is sent
        # to the app editor
        if request.path.startswith(self._rooted('/__editor__')):
            return self.editing(request)

        # anything else is the app itself
        return self.app(request)
