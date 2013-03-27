#!/usr/bin/env python

"""Nearly all of the Phidgets code comes from
InterfaceKit-simple.py, written by Adam Stelmack of Phidgets Inc,
Copyright 2010.  It is under the Creative Commons
Attribution 2.5 Canada License.

Known Issues:
    Does not check/update output state indicators after a re-connect.
    **** Therefore, after re-connect, buttons and indicators may be opposite actual state!


General Issues:
    The phidget main loop is separate from the Kivy main loop. Many hacks ensue.
"""

__author__ = 'John Boyle'
__date__ = '22 Jan 2012'

# Basic imports
from ctypes import *
import sys
import random

# Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, 
                                    ErrorEventArgs, InputChangeEventArgs,
                                    OutputChangeEventArgs, SensorChangeEventArgs
from Phidgets.Devices.InterfaceKit import InterfaceKit

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


##### Phidgets Event Handler Callback Functions #####
ik_attached = False

def inferfaceKitAttached(e):
    attached = e.device
    print("InterfaceKit %i Attached!" % (attached.getSerialNum()))

    # Used for checking connection status within the Kivy app
    global ik_attached
    ik_attached = True

def interfaceKitDetached(e):
    detached = e.device
    print("InterfaceKit %i Detached!" % (detached.getSerialNum()))

    # Used for checking connection status within the Kivy app
    global ik_attached
    ik_attached = False

def interfaceKitError(self, e):
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

def setup_interfaceKit():
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

    print("Opening phidget object....")

    try:
        #interfaceKit.openPhidget()
        interfaceKit.openRemoteIP('192.168.1.100', port=5001)
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
    return interfaceKit


########### KIVY Setup ############

class KvPhDemo(FloatLayout):
    ''' Loaded from the kv lang file
    '''

class ControlPanel(BoxLayout):
    '''Loaded from the kv lang file.
    '''

class OutDevice(BoxLayout):
    ''' Loaded from the kv lang file.
    '''
    # 'self.__init__' didn't work to do what 'set_properties' does
    # b/c I found I can't call object attributes defined within the
    # kv lang file until apparently AFTER the object has been initialized.
    # That isn't to say that there is a more natural way of doing this
    # that is provided by Kivy.

    def set_properties(self, name, iotype, ioindex):
        self.device_label.text = name + ' ' + str(ioindex)# an attribute from kv file
        self.iotype = iotype
        self.ioindex = ioindex

        # Explicitly set outputs to OFF (good habit in control situations)
        # Just as easily could read the current status instead.
        self.status_ind.text = 'OFF'
        interfaceKit.setOutputState(self.ioindex, False)

        # Check connection status every half second.
        Clock.schedule_interval(self.check_connection, 0.5)

    def check_connection(self, instance):
        # 'ik_attached' is set by the phidgets 'interfaceKitDetached' and
        # 'interfaceKitAttached' event handlers
        self.conn_ind.text = 'Connected' if bool(ik_attached) else 'disconnected'

    def toggle_state(self, state):
        ledstate = interfaceKit.getOutputState(self.ioindex)
        ledstate = not ledstate
        interfaceKit.setOutputState(self.ioindex, ledstate)
        self.status_ind.text = 'OFF' if state=='normal' else 'ON'


class KvPhDemoApp(App):

    def build(self):
        # The 'build' method is called when the object is run.

        kvphdemo = KvPhDemo()
        controlpanel = ControlPanel()

        #This LED setup may seem repetitive in this simple example.
        # It would be useful in more complex situations
        led1 = OutDevice()
        led4 = OutDevice()
        led6 = OutDevice()

        led1.set_properties(name='LED', iotype='output', ioindex=1)
        led4.set_properties(name='LED', iotype='output', ioindex=4)
        led6.set_properties(name='LED', iotype='output', ioindex=6)

        controlpanel.add_widget(led1)
        controlpanel.add_widget(led4)
        controlpanel.add_widget(led6)

        kvphdemo.content.add_widget(controlpanel) # 'content' is a reference to a
                                                  # layout placeholder in the
                                                  # kv lang file
        return kvphdemo


if __name__ == '__main__':
    interfaceKit = setup_interfaceKit()
    KvPhDemoApp().run()
