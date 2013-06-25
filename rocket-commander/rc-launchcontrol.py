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
ORDERS = ['v360_on', 'v360_off', 'atv_on', 'atv_off', 'fc_on', 'fc_off',
          'rr_on', 'rr_off', 'wifi_on', 'wifi_off']

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

class HSeparator(Widget):
    ''' Loaded from the kv lang file
    '''

class Commander(BoxLayout):
    def __init__(self, **kwargs):
        self.name = kwargs.pop('name', None)
        super(Commander, self).__init__(**kwargs)
        self.c_name.text = self.name
        self.command = self.name

        if (self.name in ORDERS) or self.name == 'LATCH':
            self.c_btn.bind(on_press=self.send_command)
        else:
            self.remove_widget(self.c_btn)
            self.add_widget(Label(text='-'))

        if self.name == 'LATCH':
            self.message = 'SET'
        else:
            self.message = 'PLEASE'

        dictionary.addKey(self.command, 'ready')

        Clock.schedule_interval(self.check_status, 1)

    def send_command(self, instance):
        dictionary.addKey(self.command, self.message)

    def check_status(self, instance):
        self.c_ind.text = dictionary.getKey(self.name)


class RCLaunchControlApp(App):

    def build(self):
        rc = RC()

        v360_on = Commander(name='v360_on')
        v360_off = Commander(name='v360_off')

        atv_on = Commander(name='atv_on')
        atv_off = Commander(name='atv_off')

        fc_on = Commander(name='fc_on')
        fc_off = Commander(name='fc_off')

        rr_on = Commander(name='rr_on')
        rr_off = Commander(name='rr_off')

        wifi_on = Commander(name='wifi_on')
        wifi_off = Commander(name='wifi_off')

        STATUS = Commander(name='STATUS')
        LATCH = Commander(name='LATCH')

        rc.content.add_widget(STATUS)
        rc.content.add_widget(LATCH)

        rc.content.add_widget(HSeparator())

        rc.content.add_widget(v360_on)
        rc.content.add_widget(v360_off)

        rc.content.add_widget(atv_on)
        rc.content.add_widget(atv_off)

        rc.content.add_widget(fc_on)
        rc.content.add_widget(fc_off)

        rc.content.add_widget(rr_on)
        rc.content.add_widget(rr_off)

        rc.content.add_widget(wifi_on)
        rc.content.add_widget(wifi_off)

        return rc


if __name__ == '__main__':
    dictionary = setup_ph_dict()
    RCLaunchControlApp().run()
