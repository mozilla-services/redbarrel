.. _quickstart:

==========
Quickstart
==========

A RedBarrel-based application is composed of:

- a RBR file: a text file that contains a description of the application.
- a Python package containing the code that's going to be executed

Creating a project
==================

To create the initial structure, create an empty directory and
run the **rbr-quickstart** command. It will create for you an example 
sample RBR file and a Python package containing the code used by 
the example -- a simple hello world.

The script will ask you a few questions ::

    $ rbr-quickstart 
    Name of the project: Hello World !
    Description: A simple app
    Version [1.0]:
    Home page of the project: http://example.com
    Author: Tarek
    Author e-mail: tarek@ziade.org
    App generated. Run your app with "rbr-run shortme.rbr"


Once the files are generated, run your application using **rbr-run**::

    $ bin/rbr-run hello-wo.rbr
    Generating the Web App...
    => 'hello' hooked for '/'
    ...ready

    Serving on port 8000...

Then, visit *http://localhost:8000/__doc__*. You should see the documentation
page of your application.


Adding web services
===================

Adding a web service consists of describing it in the RBR file (see 
:ref:`rbr`), then adding the required code for every pre- or post- step, or 
for the service itself.

A possible convention is to add one Python module per service, and
eventually group all pre- and post- functions in an :file:`util.py` module.

Check out a full example at :ref:`demo` .
