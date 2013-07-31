#!/usr/bin/env python

"""Rocket Commander, key changer testing

The code up until the testing block may be pasted into ipython to allow
for interactive key/value changes.

Uses code from the Phidgets example `Dictionary-simple.py` version 2.1.8,
by Adam Stelmack.
"""

__author__ = 'John Boyle'
__version__ = '0.0.314'
__date__ = 'June 2013'

## COPY FROM HERE TO NEXT LINE OF #s for iPython usage
######################################################

#Basic imports
from ctypes import *
import sys, subprocess
from time import sleep

#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import ErrorEventArgs, KeyChangeEventArgs, ServerConnectArgs, ServerDisconnectArgs
from Phidgets.Dictionary import Dictionary, DictionaryKeyChangeReason, KeyListener

IP = "localhost"

##################
# Phidgets setup #
##################

#Create a Dictionary object and a key listener object
try:
    dictionary = Dictionary()
    keyListener = KeyListener(dictionary, "\/*")
except RuntimeError as e:
    print("Runtime Exception: %s" % e.details)
    print("Exiting....")
    exit(1)

#Event Handler Callback Functions
def DictionaryError(e):
    print("Dictionary Error %i: %s" % (e.eCode, e.description))
    return 0

def DictionaryServerConnected(e):
    print("Dictionary connected to server %s" % (e.device.getServerAddress()))
    try:
        keyListener.start()
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
    return 0

def DictionaryServerDisconnected(e):
    print("Dictionary disconnected from server")
    try:
        keyListener.stop()
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
    return 0

def KeyChanged(e):
    if e.reason == DictionaryKeyChangeReason.PHIDGET_DICTIONARY_VALUE_CHANGED:
        reason = "Value Changed"
    elif e.reason == DictionaryKeyChangeReason.PHIDGET_DICTIONARY_ENTRY_ADDED:
        reason = "Entry Added"
    elif e.reason == DictionaryKeyChangeReason.PHIDGET_DICTIONARY_ENTRY_REMOVING:
        reason = "Entry Removed"
    elif e.reason == DictionaryKeyChangeReason.PHIDGET_DICTIONARY_CURRENT_VALUE:
        reason = "Current Value"

    if 'Heartbeat' not in e.key:
        print("%s -- Key: %s -- Value: %s" % (reason, e.key, e.value))
    return 0

def KeyRemoved(e):
    if e.reason == DictionaryKeyChangeReason.PHIDGET_DICTIONARY_VALUE_CHANGED:
        reason = "Value Changed"
    elif e.reason == DictionaryKeyChangeReason.PHIDGET_DICTIONARY_ENTRY_ADDED:
        reason = "Entry Added"
    elif e.reason == DictionaryKeyChangeReason.PHIDGET_DICTIONARY_ENTRY_REMOVING:
        reason = "Entry Removed"
    elif e.reason == DictionaryKeyChangeReason.PHIDGET_DICTIONARY_CURRENT_VALUE:
        reason = "Current Value"

    if 'Heartbeat' not in e.key:
        print("%s -- Key: %s -- Value: %s" % (reason, e.key, e.value))
    return 0


#   Main Program   #

try:
    dictionary.setErrorHandler(DictionaryError)
    dictionary.setServerConnectHandler(DictionaryServerConnected)
    dictionary.setServerDisconnectHandler(DictionaryServerDisconnected)

    keyListener.setKeyChangeHandler(KeyChanged)
    keyListener.setKeyRemovalListener(KeyRemoved)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

print("Opening Dictionary object....")

try:
    dictionary.openRemoteIP(IP, 5001)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

try:
    while dictionary.isAttachedToServer() == False:
        pass
    else:
        print("Connected: %s" % (dictionary.isAttachedToServer()))
        print("Server: %s:%s" % (dictionary.getServerAddress(), dictionary.getServerPort()))
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

##################################################################


### TESTING KEYS
try:
    print("Now we'll add some keys...")
    sleep(1)

    dictionary.addKey("LTC_ON", "None")
    dictionary.addKey("Command Check", "None")
    dictionary.addKey("Command", "None")
    sleep(2)
    dictionary.addKey("Command", "Nope")

    print("Now we will test the LTC_ON Command.")
    sleep(1)
    dictionary.addKey("LTC_ON", "ff")
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

print("Press Enter to quit....")

chr = sys.stdin.read(1)

print("Closing...")

try:
    keyListener.stop()
    dictionary.closeDictionary()
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

print("Done.")
exit(0)
