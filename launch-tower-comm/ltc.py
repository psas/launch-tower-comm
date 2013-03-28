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
    def __init__(self, devserial, IP, port, **kwargs):
        self.devserial = devserial
        
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
            #interfaceKit.setOnSensorChangeHandler(interfaceKitSensorChanged)
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")
            exit(1)
            
        try:
            interfaceKit.openRemoteIP(IP, port=port, serial=devserial)
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
        self.num_sensors = self.interfaceKit.getSensorCount()
        
        Clock.schedule_interval(self.check_status, 0.5)
    
    def check_status(self, instance):
        for index in self.num_sensors:
            sensor = "{} Sensor {}".format(self.devserial, index)
            inputs_dict[sensor] = self.interfaceKit.getSensorRawValue(index)
        

class Sensor(BoxLayout):
    
    def __init__(self, name, devserial, sensor_index, **kwargs):
    
        super(Sensor, self).__init__(**kwargs)
        self.devserial = devserial
        self.device_label.text = name + ' ' + str(sensor_index)
        self.iotype = iotype
        self.ioindex = sensor_index

        Clock.schedule_interval(self.check_status, 1)

    def check_status(self, instance):
        sensor = "{} Sensor {}".format(self.devserial, index)
        self.conn_ind.text = input_dict[sensor]



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

        inputs = Inputs(devserial=INTERFACEKIT888, IP=WEBSERVICEIP, port=WEBSERVICEPORT)
        sens0 = Sensor(name='Temperature', INTERFACEKIT888, 0)
        sens1 = Sensor(name='Voltage30', INTERFACEKIT888, 1)
        sens5 = Sensor(name='Voltage30', INTERFACEKIT888, 5)
        sens6 = Sensor(name='Voltage30', INTERFACEKIT888, 6)
        
        inputs.addwidget(sens0)
        inputs.addwidget(sens1)
        inputs.addwidget(sens5)
        inputs.addwidget(sens6)
            
        ltc = LTC()
        ltc.content.add_widget(inputs) 
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
