# -*- coding: utf-8 -*-
"""
    Setup file.

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from setuptools import setup, find_packages


setup(name='RedBarrel',
      version='0.1',
      packages=find_packages(),
      install_requires=['ply', 'Routes', 'WebOb', 'Mako', 'docutils',
                        'cssmin', 'argparse', 'WSGIProxy', 'gevent',
                        'gevent-socketio', 'pistil', 'gunicorn',
                        'pysandbox'],
      license='MPL',
      classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Operating System :: OS Independent',
      ],
      include_package_data=True,
      # XXX use distutils' script
      entry_points="""
      [console_scripts]
      rbr-check = redbarrel.util:check_syntax
      rbr-run = redbarrel.util:run_server
      rbr-quickstart = redbarrel.wizard:quickstart
      """)
