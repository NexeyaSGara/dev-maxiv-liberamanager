#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the LiberaManager project
#
# Test Copyright
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the Libera Manager Class."""

# Path
import sys
import os
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
from time import sleep
from mock import MagicMock
from PyTango import DevFailed, DevState
from devicetest import DeviceTestCase, main
from LiberaManager import LiberaManager

# Note:
#
# Since the device uses an inner thread, it is necessary to
# wait during the tests in order the let the device update itself.
# Hence, the sleep calls have to be secured enough not to produce
# any inconsistent behavior. However, the unittests need to run fast.
# Here, we use a factor 3 between the read period and the sleep calls.
#
# Look at devicetest examples for more advanced testing


# Device test case
class LiberaManagerDeviceTestCase(DeviceTestCase):
    import PyTango
    """Test case for packet generation."""
    device = LiberaManager
    properties = {'EventGeneratorDevice': 'r3-a101911cab03/tim/evg-01','IncludedLiberas': '','ExcludedLiberas': '','Timeout': '30',
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = LiberaManager.numpy = MagicMock()
        # PROTECTED REGION ID(LiberaManager.mocking) ENABLED START #
        cls.PyTango.DeviceProxy = LiberaManager.DeviceProxy = MagicMock()
        # PROTECTED REGION END #    //  LiberaManager.mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(LiberaManager.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  LiberaManager.test_properties
        pass

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(LiberaManager.test_State) ENABLED START #
        print self.device.State()
        sleep(3)
        print self.device.State()
        # PROTECTED REGION END #    //  LiberaManager.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(LiberaManager.test_Status) ENABLED START #
        print self.device.Status()
        sleep(3)
        print self.device.Status()
        # PROTECTED REGION END #    //  LiberaManager.test_Status

    def test_Synchronized(self):
        """Test for Synchronized"""
        # PROTECTED REGION ID(LiberaManager.test_Synchronized) ENABLED START #
        self.device.Synchronized = False
        print self.device.Synchronized
        self.device.Synchronized = True
        print self.device.Synchronized
        # PROTECTED REGION END #    //  LiberaManager.test_Synchronized


# Main execution
if __name__ == "__main__":
    main()
