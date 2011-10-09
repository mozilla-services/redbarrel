.. _rbr:

=================
RBR specification
=================

**Version 0.9**

The RBR (RedBaRell) Language is a syntax used to describe web services.

It's organized into:

- a meta section containing common definitions
- globs - values that can be used everywhere
- path definition sections for every web service


General syntax
==============

RBR is organized into definitions containing variables or operations,
and global definitions.

The general syntax is::

    global name "value";

    type binary python:Binary;

    meta (
        title "this",
        version 1.0,
        description "That"
    );

    path somepath (
        method   GET,
        url /,
        use python:somecode,
    );

Every section or global ends with a semi-colon, and every definitin is
separated by a comma.

There's a special unique **meta** section that's used to define a few metadata::

    meta (
        title "this",
        version 1.0,
        description "That"
    );


In sections, for some variables, you can define multiple elements::

    path Foo (
        variable1 (
            field1 value1,
            operation,
            field2 value2
        )
    );


Here's a full example of a valid RBR file that defines an API to shorten
URLs::

    meta (
        description """An URL Shortener""",
        version 1.0
    );

    path shorten (
        description "Shortens an URL",
        method POST,
        url /shorten,

        request-body (
            description "Contains the URL to shorten"
        ),
        response-body (
            description "The shortened URL"
        ),
        response-headers (
            set Content-Type "text/plain"
        ),
        response-status (
            describe 200 "Success",
            describe 400 "I don't like the URL provided"
        ),

        use python:shortme.shorten.shorten
    );

Types
=====

RBR recognizes these types:

- "string" -- characters wrapped into *"*.
- """text""" -- a string that may contain end of lines and *"*.
- status code -- an integer representing a status code, like 401
- verb -- an HTTP verb. Possible values: GET, HEAD, POST, PUT, DELETE,
  TRACE, CONNECT, OPTIONS. You can provide several verbs, separated
  by "|". Example:  GET|POST.
- path -- a path on the server, starting with /
- code location -- a fully qualified name that points to some callable.
- file location -- a path on the system

More on paths
:::::::::::::

Paths are described using the Routes syntax (see XXX), and always start with
*/*.

XXX more on paths.


More on locations
:::::::::::::::::

Every location is suffixed with a type. Right now RBR recognizes:

- **python:fqn** -- some python callable. The callable is expressed as a
  fully qualified name.
- **location:path** -- a path to a static file.
- **proxy:url** --  an http or https uri on which the call will be proxied.
  note that this will only work for the **use** option of paths.

Examples:

- location:/var/www/index.html
- python:package.module.func
- proxy:http://localhost:5000


List of variables
=================

Every path definition can contain these variables:

- **description** -- description of the section, can be a string or a text [1]_
- **method** -- the HTTP verb(s) used for the service [1]_ [3]_
- **url** --  the path matching the service [1]_ [3]_
- **use** --  the code or file location [1]_ [3]_
- **response-body** --  the response body [2]_
- **response-headers** -- the response headers [2]_
- **response-status** -- the response status [2]_
- **request-body** -- the request body [2]_
- **request-headers** -- the request headers [2]_
- **request-status** -- the request status [2]_

The meta section can contain:

- **version** -- the version of the API [1]_
- **description** -- a global description [1]_
- **title** -- a title for the application [1]_


.. [1] Single value
.. [2] Multiple values in a subsection. Subsections can contain a description,
   some variables and some operations.
.. [3] Mandatory


Every section can contain extra custom fields, as long as they are
suffixed by *x-* so they don't conflict with a future version of the RBR DSL.
Examples: **x-author**, **x-request-max-size**, etc. The reference
implementation is not interpreting those fields, but they are loaded in the
AST.


Operations
==========

Each section can contain one or several operations. Operations can be used to:

- check the type of a value, like the request body or one of its header.
- convert a value
- set a header
- describe response status codes
- document the web services


Check a type
::::::::::::

You can check a request or response header or body, using one of these
expressions:

1. unless type is [not] *name type* return code
2. unless *field name* type is [not] *name type* return code
3. unless *field name* validates with *prefixed name* return code

The first form can be used to validate a body. For example, to check that the
request body is json and return 400 if not, you can write::

    request-body (
        unless type is json return 400
    )

The second form is to be used for headers::

    request-headers (
        unless X-Back-Off is int return 400
    )


RBR provides a very few pre-defined types for these operations:

- **json**
- **int**
- **float**

But you can define your own types. See :ref:`custom-types`.

The last form can be used to call some custom function.
Basic authentication example::

    request-headers (
        unless Authorization validates with python:auth return 401
    )


Will return a 401 unless :func:`auth` returns True.


Convert a value
:::::::::::::::

You can alter the value of a header or body using *alter with code*, where
:func:`code` is a callable that will get the value to alter, and return the result.

For example, if you want to return a compressed version of a response that
contains a CSS stylesheet, you can write::

    response-body (
        alter with python:somemodule.compress_css
    )

Where :func:`compress_css` is a function that returns a compressed version
of the body.

Set a header
::::::::::::

You can directly set a header, using *set header value*. For instance, if you
want to set the Content-Type of a response to "text/css"::

    response-headers (
        set content-type "text/css"
    )


Describe a status code
::::::::::::::::::::::

*describe code text* will let you describe every status code for the response.

Example::

    response-status (
        describe 200 "Success",
        describe 400 "The request is probably malformed",
        describe 401 "Authentication failure"
    )

Descriptions
::::::::::::

As explained earlier, every section and subsection in the DSL file can
contain a description. Descriptions are useful to document the web services::

    path capitalize (
        description "A web service with several post/pre processing",
        ...

        request-body (
            description "Send a string in json and the server returns it Capitalized.",
        ),

        response-body (
            description "The string, Capitalized !",
        )
    );


.. _custom-types:

Defining custom types
=====================

RBR provides a very few pre-defined types for check operations:

- **json**
- **int**
- **float**

To define a new type, you can use a **type name value** definition, where name
is the **name** of the type and **value** a code location.

The code location is instanciated, then invoked everytime a type needs to
be chacked. It receives the value and must return True or False.

Example::

    type blob python:Blob;

Corresponding code::

    class Blob:
        def __call__(self, value):
            return value.startswith('blob:')



The meta section
================

The meta section allows you to define a title, a description and a
version for your application.


Example::

    meta (
        title "RedBarrel Application",
        version 1.1,
        description """
        This is a RedBarrel App !
        """
    );


Proxying
========

Requests to a given url can be proxied to another server.

Example::

    path shorten (
        description "Shortens an URL",
        method POST,
        url /shorten,

        request-body (
            description "Contains the URL to shorten"
        ),
        response-body (
            description "The shortened URL"
        ),
        response-headers (
            set Content-Type "text/plain"
        ),
        response-status (
            describe 200 "Success",
            describe 400 "I don't like the URL provided"
        ),

        use proxy:http://localhost:5000
    );


The request and response can be checked as usual, and the request is eventually
proxied to **http://localhost:5000** then the response returned.

This is useful if you want to use another server to build the response for a 
given service.
