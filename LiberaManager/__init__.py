# -*- coding: utf-8 -*-
#
# This file is part of the LiberaManager project
#
# Test Copyright
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""Libera Manager Class

This class aims to manage liberas.
"""

from . import release
from .LiberaManager import LiberaManager, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
