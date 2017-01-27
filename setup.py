#!/usr/bin/env python
from distutils.core import setup
setup(name='TAP',
      version='1.0',

      description='A sample Python project',
      long_description='long_description',

      # Author details
      author='Matt Epperson',
      author_email='m.p.epperson@gmail.com',

      # Choose your license
      license='MIT',

      # add unit tests
      test_suite='tests',

      py_modules=['TAPP.Camera', 'utils.gdal_utils', 'utils.ply_utils'],
      scripts=['tapp.py']
      )
