# -*- coding: utf-8 -*-
#
# This file is part of the LiberaManager project
#
# Test Copyright
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" Libera Manager Class

This class aims to manage liberas.
"""

__all__ = ["LiberaManager", "main"]

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango.server import class_property, device_property
from PyTango import AttrQuality, AttrWriteType, DispLevel, DevState
# Additional import
# PROTECTED REGION ID(LiberaManager.additionnal_import) ENABLED START #
import threading
import time
# PROTECTED REGION END #    //  LiberaManager.additionnal_import


class LiberaManager(Device):
    """
    This class aims to manage liberas.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(LiberaManager.class_variable) ENABLED START #
    TICK = 1
    thread_stop = False
    l_sync = False
    start_t = 0
    is_timeout = False
    
    # Wait for all liberas to be synchronized and then startSynchronization
    def wait_sync_and_start(self):
        liberas_sync = self.liberas
        for device in self.liberas:
            try:
                device.AnnounceSynchronization()
            except:
                self.error_stream("Can't Announce synchronization on device {0}".format(device))
        try:
            self.proxy_evt.SyncLBP()
            # self.proxy_evt.State()
        except:
            self.error_stream("Can't send SyncLBP to the EventGeneratorDevice")
            return
        while not self.thread_stop:
            if len(liberas_sync) == 0:
                self.thread_stop = True
                self.info_stream("All liberas are synchronized.")
            for device in liberas_sync:
                try:
                    if device.SynchronizationStatus == 2:
                        self.debug_stream("Device {0} is now synchronized".format(device))
                        liberas_sync.remove(device)
                    else:
                        self.debug_stream("Device {0} still not synchronized".format(device))
                except:
                    self.debug_stream("Device {0} is not accessible".format(device))
            if (time.time() - self.start_t > self.Timeout):
                self.thread_stop = True
                self.is_timeout = True
            time.sleep(self.TICK)
        if (self.is_timeout):
            self.set_state(DevState.ALARM)
            msg = "Timeout reached for waiting liberas to be synchronized : "
            for dev in liberas_sync:
                msg +="\n" + dev.name() + "not yet synchronized"
            self.set_status(msg)
        else:
            for device in self.liberas:
                try:
                    device.StartSynchronization()
                except:
                    self.debug_stream("Device {0} is not accessible".format(device))
            self.set_state(DevState.ON)
            msg = "The manager is connected to liberas :"
            for dev in self.liberas:
                msg +="\n" + dev.name()
            if len(self.liberas_failed) > 0:
                msg+="\n" + "Failed to connect to liberas :"
                for dev in self.liberas_failed:
                    msg +="\n" + dev
            self.set_status(msg)

    def init_thread(self):
        all_devices = self.IncludedLiberas
        self.debug_stream("All device found {0}".format(all_devices))
        all_devices_wanted = []
        # remove unwanted liberas
        if self.ExcludedLiberas is not None:
            if len(self.ExcludedLiberas) > 0:
                for device in all_devices:
                    if device not in self.ExcludedLiberas:
                        all_devices_wanted.append(device)
        else:
            all_devices_wanted = all_devices
        
        self.liberas=[]
        self.liberas_failed=[]
        for device in all_devices_wanted:
            proxy = PyTango.DeviceProxy(device)
            try:
                state = proxy.State()
                if state == DevState.ON or state == DevState.ALARM:
                    self.liberas.append(proxy)
                else:
                    self.error_stream("Can't synchronize the device {0}, state is {1}".format(device, state))
            except:
                self.error_stream("Can't access the device {0}".format(device))
                self.liberas_failed.append(device)

        if self.EventGeneratorDevice == "":
            self.set_state(DevState.FAULT)
            self.set_status("The EventGeneratorDevice property isn't filled!!!")
            return
        
        try:
            self.proxy_evt = PyTango.DeviceProxy(self.EventGeneratorDevice)
        except:
            self.set_state(DevState.FAULT)
            self.set_status("The EventGeneratorDevice doesn't exists in the Database")
            return
        try:
            state = self.proxy_evt.State()
        except:
            self.set_state(DevState.FAULT)
            self.set_status("The EventGeneratorDevice isn't accessible")
            return
        
        if len(self.liberas) > 0:
            self.set_state(DevState.ON)
            msg = "The manager is connected to liberas :"
            for dev in self.liberas:
                msg +="\n" + dev.name()
            if len(self.liberas_failed) > 0:
                msg+="\n" + "Failed to connect to liberas :"
                for dev in self.liberas_failed:
                    msg +="\n" + dev
            self.set_status(msg)
        else:
            self.set_state(DevState.FAULT)
            self.set_status("There is no libera connected or accessible.")
        self.sur_thread = None
    # PROTECTED REGION END #    //  LiberaManager.class_variable
    # ----------------
    # Class Properties
    # ----------------

    # -----------------
    # Device Properties
    # -----------------

    EventGeneratorDevice = device_property(
        dtype='str', default_value="r3-a101911cab03/tim/evg-01"
    )

    IncludedLiberas = device_property(
        dtype=('str',),
    )

    ExcludedLiberas = device_property(
        dtype=('str',),
    )

    Timeout = device_property(
        dtype='uint16', default_value=30
    )

    # ----------
    # Attributes
    # ----------

    Synchronized = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
        label="Synchronized",
        doc="Indicates if the liberas are synchronized",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        # PROTECTED REGION ID(LiberaManager.init_device) ENABLED START #
        if self.IncludedLiberas == None:
            self.set_state(DevState.FAULT)
            self.set_status("The IncludedLiberas property isn't filled")
            return
        self.init_thread = threading.Thread(target=self.init_thread)
        self.init_thread.start()
        self.set_state(DevState.INIT)
        self.set_status("LiberaManager initialization started....")
        # PROTECTED REGION END #    //  LiberaManager.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(LiberaManager.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  LiberaManager.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(LiberaManager.delete_device) ENABLED START #
        try:
            self.thread_stop = True
            if self.sur_thread.isAlive():
                self.sur_thread.join()
        except Exception:
            pass
        try:
            self.init_thread.join()
        except Exception:
            pass
        del self.init_thread
        # PROTECTED REGION END #    //  LiberaManager.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_Synchronized(self):
        # PROTECTED REGION ID(LiberaManager.Synchronized_read) ENABLED START #
        synchro = False
        all_ok = False
        for device in self.liberas:
            try:
                if device.SynchronizationStatus != 2:
                    # self.debug_stream("Device {0} is not synchronized".format(device))
                    all_ok = False
                else:
                    all_ok = True
            except:
                self.debug_stream("Device {0} is not accessible".format(device))
        if all_ok is True:
            synchro = True
        self.l_sync = synchro
        return synchro
        # PROTECTED REGION END #    //  LiberaManager.Synchronized_read

    def write_Synchronized(self, value):
        # PROTECTED REGION ID(LiberaManager.Synchronized_write) ENABLED START #
        if value is True:            
            # Launch the surveillance thread
            if self.sur_thread is None:
                self.sur_thread = threading.Thread(target = self.wait_sync_and_start)
                self.sur_thread.start()
                self.set_state(DevState.RUNNING)
                self.set_status("Waiting for liberas to be synchronized....")
                self.start_t = time.time()
                self.is_timeout = False
                self.thread_stop = False
            elif self.sur_thread.isAlive() is True:
                pass
        # PROTECTED REGION END #    //  LiberaManager.Synchronized_write

    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    from PyTango.server import run
    return run((LiberaManager,), args=args, **kwargs)

if __name__ == '__main__':
    main()
