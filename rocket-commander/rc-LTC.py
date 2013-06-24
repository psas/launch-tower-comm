#!/usr/bin/env python

"""Rocket Commander
Sends power commands to the rocket.

Starts a Phidgets Dictionary that receives KeyChange events from the
Phidgets Webservice and reacts by sending tty commands to the rocket.

It then changes the command keys back to their nuetral state as a
acknowledgement signal.


Uses code from the Phidgets example `Dictionary-simple.py` version 2.1.8,
by Adam Stelmack.
"""

__author__ = 'John Boyle'
__version__ = '0.0.314'
__date__ = 'June 2013'


#Basic imports
from ctypes import *
import sys, subprocess
from time import sleep

#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import ErrorEventArgs, KeyChangeEventArgs, ServerConnectArgs, ServerDisconnectArgs
from Phidgets.Dictionary import Dictionary, DictionaryKeyChangeReason, KeyListener

IP = "localhost"
COMMANDS = dict()

###################
# commander setup #
###################

def capture_commands(e):
    key = e.key
    if 'LTC_ON' == key or 'COMMAND_CHECK' == key:
        COMMANDS[e.key] = e.value


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

    capture_commands(e)
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

    capture_commands(e)
    return 0

####################
#   Main Program   #
####################

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


#############
# Main Loop #
#############
COMMANDS['LTC_ON'] = 'HI'
COMMANDS['COMMAND_CHECK'] = 'HI'

while(True):
    sleep(1)
    print COMMANDS.keys()
    print '--------'
    print COMMANDS.values()

    if COMMANDS['LTC_ON'] == 'YES PLEASE':
        if COMMANDS['COMMAND_CHECK'] == 'AFFIRMATIVE':
            try:
                shell_command = "/home/john/code/ltcscripts/fc_on"
                results = subprocess.Popen(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                results = results.communicate()
                if results[1]:
                    print "Error: {}".format(results[1])
                    dictionary.addKey('COMMAND_CHECK', 'NEGATORY')
                    dictionary.addKey('LTC_ON', 'ERROR')
                else:
                    print "Message Sent"
                    dictionary.addKey('COMMAND_CHECK', 'NEGATORY')
                    dictionary.addKey('LTC_ON', 'EXECUTED')

            except PhidgetException as e:
                print("Phidget Exception %i: %s" % (e.code, e.details))
                #~ print("Exiting....")
                #~ exit(1)
        else:
            print "Incorrect command sequence"


# Graceful exit
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
