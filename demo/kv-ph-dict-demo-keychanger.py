#!/usr/bin/env python

"""Kivy-Phidgets-Demo Dictionary Changer
Accesses a Phidgets Webservice Dictionary and periodically modifies 
values in order to simulate incoming data from various sensors.

Copyright 2013 John Boyle.


Most of the Phidgets code comes from Dictionary-simple.py, written by 
Adam Stelmack of Phidgets Inc, Copyright 2010. 
That code was under the Creative Commons Attribution 2.5 Canada License. 
To view a copy of this license, visit http://creativecommons.org/licenses/by/2.5/ca/

"""

__author__ = 'John Boyle'
__version__ = '0.0.1'
__date__ = 'March 20 2013'

#Basic imports
from ctypes import *
import sys
from time import sleep
#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, 
                                      PhidgetException
from Phidgets.Events.Events import ErrorEventArgs, KeyChangeEventArgs,
                                ServerConnectArgs, ServerDisconnectArgs
from Phidgets.Dictionary import Dictionary, DictionaryKeyChangeReason, 
                                KeyListener

#Create a Dictionary object and a key listener object
try:
    dictionary = Dictionary()
    keyListener = KeyListener(dictionary, ".*")
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
    
    print("%s -- Key: %s -- Value: %s" % (reason, e.key, e.value))
    return 0

#Main Program Code
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
    dictionary.openRemoteIP("localhost", 5001)
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
# Set revolving values
try:
    print("Now we'll add some keys...")
    sleep(1)
    
    ###  each valn needs to change at a different frequency
    ###  val4 will be the complete device connection state
    while True:
        val1 = random.randint(-10,15)
        val2 = random.randint(30, 50)
        val3 = rand
    
    dictionary.addKey("test1", "ok", True)
    dictionary.addKey("test2", "ok", False)
    dictionary.addKey("test3", "ok", True)
    sleep(2)
    
    print("Now we will test for key 'test2' being in the dictionary.")
    sleep(1)
    
    value = dictionary.getKey("test2")
    print("Key: test2  Value: %s" % (value))
    
    print("Now we will remove one of the keys...")
    sleep(1)
    
    dictionary.removeKey("test4")
    
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
