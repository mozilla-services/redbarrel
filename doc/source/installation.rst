Installing RedBarrel
====================

First, make sure you have Pip, Distribute and Virtualenv installed.

You can quickly set things up with::

    $ curl -O http://python-distribute.org/distribute_setup.py
    $ python distribute_setup.py
    $ easy_install pip virtualenv

Installing the latest stable RedBarrel release is then done with::

    $ pip install redbarrel

If you want to try the cutting-edge version, grab the repository and
create a local virtualenv::

    $ hg clone https://bitbucket.org/tarek/redbarrel
    $ cd redbarrel
    $ virtualenv --distribute .
    $ bin/python setup.py develop

In this setup, all RedBarrel scripts will be located in the **bin**
directory.

You can also setup bash completion::

    $ sudo cp bash_completion.d/redbarrel /etc/bash_completion.d/
