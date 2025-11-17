#!/usr/bin/env python

from Phidget22.Devices.DigitalOutput import DigitalOutput

ignition = DigitalOutput()
ignition.setDeviceSerialNumber(259173)
ignition.setChannel(0)
ignition.openWaitForAttachment(5000)
ignition.setDeviceLabel("Ignition Relay")
print("Done")
