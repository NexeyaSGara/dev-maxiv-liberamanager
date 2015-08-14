#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the LiberaManager project
#
# Test Copyright
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

import os
import sys
from setuptools import setup

setup_dir = os.path.dirname(os.path.abspath(__file__))

# make sure we use latest info from local code
sys.path.insert(0, setup_dir)

with open('README.rst') as file:
    long_description = file.read()

exec(open('LiberaManager/release.py').read())
pack = ['LiberaManager']

setup(name=name,
      version=version,
      description=description,
      packages=pack,
      scripts=['scripts/LiberaManager'],
      include_package_data=True,
      test_suite="test",
      author=author,
      author_email=author_email,
      license=license,
      long_description=long_description,
      url=url,
      platforms="All Platforms"
      )
