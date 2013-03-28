#!/usr/bin/env python

'''ltc.py - the launch-tower-comm program.
Runs on Phidgets and Kivy.

'''

from ctypes import *
import sys
import random

#Phidgets specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, \ 
        ErrorEventArgs, InputChangeEventArgs, OutputChangeEventArgs, \
        SensorChangeEventArgs
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
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label  import Label
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.codeinput import CodeInput
from kivy.extras.highlight import KivyLexer
from kivy.config import ConfigParser
from kivy.uix.settings import Settings


global INTERFACEKIT888 = 178346
global INTERFACEKIT004 = 259173
global WEBSERVICEIP = "192.168.128.250"
global WEBSERVICEPORT = 5001
global inputs_dict = dict()

########### Phidgets Setup ########
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

def interfaceKitSensorChanged(e):
    source = e.device
    sensor = "{} Sensor {}".format(source.getSerialNum(), e.index)
    inputs_dict[sensor] = str(e.value)
    print("InterfaceKit %i: Sensor %i: %i" % (source.getSerialNum(), e.index, e.value))


########### KIVY Setup ############

class LTC(FloatLayout):
    # Loaded from the kv lang file
    pass

class Inputs(BoxLayout):
    def __init__(self, **kwargs):
        global INTERFACEKIT888
        global WEBSERVICEIP
        global WEBSERVICEPORT
        global inputs_dict
        
        super(Inputs, self).__init__(**kwargs)
        
        #Create an interfacekit object
        try:
            interfaceKit = InterfaceKit()
        except RuntimeError as e:
            print("Runtime Exception: %s" % e.details)
            print("Exiting....")
            exit(1)

        # Set Event Handlers
        try:
            interfaceKit.setOnAttachHandler(inferfaceKitAttached)
            interfaceKit.setOnDetachHandler(interfaceKitDetached)
            interfaceKit.setOnErrorhandler(interfaceKitError)
            interfaceKit.setOnSensorChangeHandler(interfaceKitSensorChanged)
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")
            exit(1)
            
        try:
            interfaceKit.openRemoteIP(WEBSERVICEIP, port=WEBSERVICEPORT, serial=INTERFACEKIT888)
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
        
        print("InterfaceKit Attached...")
        self.interfaceKit = interfaceKit

class InputDevice(BoxLayout):
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


    

#class StandardWidgets(FloatLayout):

    #value = NumericProperty(0)

    #def __init__(self, **kwargs):
        #super(StandardWidgets, self).__init__(**kwargs)
        #Clock.schedule_interval(self.increment_value, 1 / 30.)

    #def increment_value(self, dt):
        #self.value += dt

class LTCApp(App):

    def build(self):
        # The 'build' method is called when the object is run.

        inputs = Inputs()

        ltc = LTC()
        ltc.content.add_widget(root) 
        return ltc
    
    def build_config(self, config):
        config.add_section('kinect')
        config.set('kinect', 'index', '0')
        config.add_section('shader')
        config.set('shader', 'theme', 'rgb')

    def build_settings(self, settings):
        settings.add_json_panel('Testing', self.config, data='''[
            { "type": "title", "title": "Kinect" },
            { "type": "numeric", "title": "Index",
              "desc": "Kinect index, from 0 to X",
              "section": "kinect", "key": "index" },
            { "type": "title", "title": "Shaders" },
            { "type": "options", "title": "Theme",
              "desc": "Shader to use for a specific visualization",
              "section": "shader", "key": "theme",
              "options": ["rgb", "hsv", "points"]}
        ]''')


if __name__ == '__main__':
    LTCApp().run()
