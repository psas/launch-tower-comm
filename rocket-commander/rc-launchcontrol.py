#!/usr/bin/env python

"""Rocket Commander - Launch Control Side
Sends commands to Rocket Commander on the LTC (rc-LTC).

It waits for an acknowledgement from rc-LTC and displays it. It connects to
the user-side of the Phidget WebService Dictionary.

Uses code from the Phidget example `Dictionary-simple.py` version 2.1.8,
by Adam Stelmack.
"""

__author__ = 'John Boyle'
__date__ = 'Jun 2013'


import random
import sys
from ctypes import *
from time import sleep

#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, \
                                ErrorEventArgs, InputChangeEventArgs, \
                                OutputChangeEventArgs, SensorChangeEventArgs
from Phidgets.Dictionary import Dictionary, DictionaryKeyChangeReason


#Kivy specific imports
import kivy
kivy.require('1.0.5')
from kivy.app import App
from kivy.clock import Clock
from kivy.config import ConfigParser
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label  import Label
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty

LTCIP = 'localhost'
ORDERS = ['fc_on', 'fc_off', 'rr_on', 'rr_off']


##### Phidgets Event Handler Callback Functions #####
def DictionaryError(e):
    print("Dictionary Error %i: %s" % (e.eCode, e.description))
    return 0

def DictionaryServerConnected(e):
    print("Dictionary connected to server %s" % (e.device.getServerAddress()))
    try:
        #keyListener.start()
        pass
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
    return 0

def DictionaryServerDisconnected(e):
    print("Dictionary disconnected from server")
    try:
        #keyListener.stop()
        pass
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
    return 0

def setup_ph_dict():
    #Create a Dictionary object and a key listener object
    try:
        dictionary = Dictionary()

    except RuntimeError as e:
        print("Runtime Exception: %s" % e.details)
        print("Exiting....")
        exit(1)

    try:
        dictionary.setErrorHandler(DictionaryError)
        dictionary.setServerConnectHandler(DictionaryServerConnected)
        dictionary.setServerDisconnectHandler(DictionaryServerDisconnected)

    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

    print("Opening phidget object....")

    try:
        dictionary.openRemoteIP(LTCIP, port=5001)
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
    return dictionary


########### KIVY Setup ############

class RC(FloatLayout):
    ''' Loaded from the kv lang file
    '''

class Commander(BoxLayout):
    def __init__(**kwargs):
        self.name = kwargs['name'].pop()
        super(Commander, self).__init__(**kwargs)
        self.


class OutDevice(BoxLayout):
    ''' Loaded from the kv lang file.
    '''
    def set_properties(self, name):
        self.device_label.text = name # an attribute from kv file
        self.ioindex = name.lower()
        # Check connection status every half second.
        Clock.schedule_interval(self.check_status, 0.5)

    def check_status(self, instance):
        self.status_ind.text = dictionary.getKey(self.ioindex)
        self.conn_ind.text = dictionary.getKey('dev_state')

class RCApp(App):

    def build(self):
        rc = RC()

        #This LED setup may seem repetitive in this simple example.
        # It would be useful in more complex situations
        fc_on = Commander(name='fc_on')
        fc_off = Commander()
        rc_on = Commander()

        ai1.setup(name='AI1')
        ai2.setup(name='AI2')
        ai3.setup(name='AI3')

        controlpanel.add_widget(ai1)
        controlpanel.add_widget(ai2)
        controlpanel.add_widget(ai3)

        dictlisten.content.add_widget(controlpanel) # 'content' is a reference to a
                                                  # layout placeholder in the
                                                  # kv lang file
        return dictlisten


if __name__ == '__main__':
    dictionary = setup_ph_dict()
    RCApp().run()
