#!/usr/bin/env python

"""ignition-relay-watchdog
Ignition relay timeout.

Most of this code comes from the InterfaceKit-simple.py example by Adam 
Stelmack of Phidgets, Inc. That code was under the following license:

Copyright 2010 Phidgets Inc.
This work is licensed under the Creative Commons Attribution 2.5 Canada 
License. To view a copy of this license, visit 
http://creativecommons.org/licenses/by/2.5/ca/
"""


#Basic imports
from ctypes import *
import sys
import random
import signal
from time import sleep

#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, OutputChangeEventArgs, SensorChangeEventArgs
from Phidgets.Devices.InterfaceKit import InterfaceKit


SERIAL_NUM = 259173   # Relay board 0/0/4 serial number
RELAY = 0             # The iginition relay
TIMEOUT = 10          # Wait this long to shut it off

# Signal handler
def handler(signum, frame):
    print "Ignition Relay timeout: Opening Ignition Relay"
    interfaceKit.setOutputState(RELAY, False)

#Event Handler Callback Functions
def inferfaceKitAttached(e):
    attached = e.device
    print("InterfaceKit %i Attached!" % (attached.getSerialNum()))

def interfaceKitDetached(e):
    detached = e.device
    print("InterfaceKit %i Detached!" % (detached.getSerialNum()))

def interfaceKitError(e):
    try:
        source = e.device
        print("InterfaceKit %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))

def interfaceKitInputChanged(e):
    source = e.device
    print("InterfaceKit %i: Input %i: %s" % (source.getSerialNum(), e.index, e.state))

def interfaceKitSensorChanged(e):
    source = e.device
    print("InterfaceKit %i: Sensor %i: %i" % (source.getSerialNum(), e.index, e.value))

def interfaceKitOutputChanged(e):
    source = e.device
    print("InterfaceKit %i: Output %i: %s" % (source.getSerialNum(), e.index, e.state))
    if (source.getSerialNum() == SERIAL_NUM) and (e.index == RELAY):
            if e.state == True:
                # Set an alarm
                signal.alarm(TIMEOUT) 
                print "Alarm set"

        
if __name__ == "__main__":
    # Set the timeout alarm signal handler
    signal.signal(signal.SIGALRM, handler)

    #Create an interfacekit object
    try:
        interfaceKit = InterfaceKit()
    except RuntimeError as e:
        print("Runtime Exception: %s" % e.details)
        print("Exiting....")
        exit(1)

    try:
        interfaceKit.setOnAttachHandler(inferfaceKitAttached)
        interfaceKit.setOnDetachHandler(interfaceKitDetached)
        interfaceKit.setOnErrorhandler(interfaceKitError)
        interfaceKit.setOnInputChangeHandler(interfaceKitInputChanged)
        interfaceKit.setOnOutputChangeHandler(interfaceKitOutputChanged)
        interfaceKit.setOnSensorChangeHandler(interfaceKitSensorChanged)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

    print("Opening phidget relay board....")

    try:
        interfaceKit.openRemoteIP("192.168.128.2", port=5001, serial=SERIAL_NUM)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

    print("Waiting for attach....")

    try:
        interfaceKit.waitForAttach(10000)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        try:
            interfaceKit.closePhidget()
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")
            exit(1)
        print("Exiting....")
        exit(1)

    while True:
        sleep(1)

    try:
        interfaceKit.closePhidget()
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

    print("Done.")
    exit(0)
