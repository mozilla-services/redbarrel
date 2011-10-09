==================
What's RedBarrel ?
==================

tldr; **RedBarrel is a DSL and Micro-Framework to write Web Services**

RedBarrel allows you to describe your Web Services via a Domain Specific 
Language (DSL) and organize your code in a very simple way. The DSL 
replaces the code usually needed to route you request to the right
piece of code, and let you describe all the pre- and post- steps.

RedBarrel can be used to write any kind of web application, but is
specifically designed to write Web Services.


Anatomy of a Web Service
========================

A Web Service is basically doing these four steps:

1. **[pre-processing]** Check the request body and headers, and potentially 
   reject it. Rejection can be due to a Basic Authentication failure, 
   an unexpected value for the request body, etc. 

2. **[routing]** Find what code or application should be called to build 
   the response. This is usually computed with the path information and 
   sometimes some headers. 

3. **[execution]** Invoke some code to build the response

4. **[post-processing]** Return the response built and maybe do some 
   post-processing or post-assertions like converting the content-type 
   etc.


In Python, when you build web services using a WSGI framework like Pylons,
Pyramid, or simply Routes + WebOb, all of these steps happen in your code. You
define the routing using Routes descriptions, or using more clever dispatching
systems like what Pyramid offers, then delegate the execution to a controller
class or a simple function, after a potential pre-processing. Although the
pre-processing part is often merged with the execution part because they are
closely related.

For instance, if you have a web service that requires a JSON mapping in the
request body, you could write something that looks like::

    def my_webservice(request): 
        try: 
            data = json.loads(request.body) 
        except ValueError: 
            # this raises a 400 
            raise HTTPBadRequest("Unknown format -- we want JSON")

        ... do something ...

Of course you can always generalize this by using a decorator to clearly
separate the pre-processing part::

    @if_not_json(400) 
    def my_webservice(request): 
        ... do something ...

Same thing for the post-processing step::

    @if_not_json(400) 
    @convert_output('application/json') 
    def my_webservice(request): 
        ... do something ...

And in some frameworks, the routing itself is expressed as a decorator::

    @route('/here/is/my/webservice') 
    @if_not_json(400)
    @convert_output('application/json') 
    def my_webservice(request): 
        ... do something ...

It turns out that there are a lot of pre/post steps that can be pushed to a
**meta level**. 

With RedBarrel, Steps 1., 2. and 4. are described in a Domain Specific 
Language (DSL) instead of decorators or other meta-level code.

The RBR DSL
===========

RedBarrel pushes all the pre- and post- processing descriptions in a DSL
called **RBR**. The RBR file also describes in detail every web service,
like the path to invoke them, which HTTP method should be used, 
what possible status codes will be returned, etc.

The first benefit is a natural separation of the code that actually does
the job, from the code that checks or converts inputs and outputs. 
When you are developing a web service, you don't have to worry anymore 
about checking the request or setting the response content-type. 
You can just focus on the feature. This separation favors code reuse
and reduces the boiler-plate code of your application: all the post- and
pre- conditions can be grouped in a library that's reused accross all your
web services.

A DSL also allows a possible delegation of pre/post tasks to a higher
layer: if the RedBarrel DSL was to be implemented as an Nginx module
all the pre- and post- processing could happen at the web server level,
allowing an interesting leverage of resources. Rejecting bad request
in NGinx makes more sense than doing it in the Python backend.

Last, expressing web services in a DSL facilitates introspection:
the RedBarrel default implementation for instance, creates a HTML
view of all available webservices.


Writing an application with RedBarrel
=====================================

Writing a web application with RedBarrel consists of describing the logic of
every web service in a RBR file, then worry about the implementation of 
every piece. There is no MVC paradigm or anything similar that the developer
must follow. You can write your code in functions, classes or whatever, and
just hook them into the RBR file.

For example, the RBR for a simple Hello world app can look like this::

    path hello_world (
        description "Simplest application: Hello World!",
        method GET,
        url /,
        use python:somemodule.hello
    );


With a function `hello` located in `somemodule`::

    def hello(request):
        return 'Hello World'


Have a look at a full example: :ref:`demo`.

What do you get with RedBarrel ?
================================

The current version includes:

- a parser for the RBR DSL.
- a RBR syntax checker.
- a pure Python implementation of a WSGI Web Server that can be launched
  with a RBR file.
- a documentation generator.
- a wizard to quick-start a project

What I'd like to have in a future revision:

- a NGinx Module implementation
- an Apache implementation
- more backends than Python, so web services can execute JS, Erlang, etc
- contributors

How to contribute ?
===================

If you like the idea, you can contribute to the project, by:

- using RedBarrel in one of your project and providing feedback
- contributing code and/or documentation
- etc.

Contact me at tarek_at_ziade.org
