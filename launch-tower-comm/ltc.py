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
from kivy.config import Config, ConfigParser
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label  import Label
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.extras.highlight import KivyLexer


#~ global INTERFACEKIT888 
#~ global INTERFACEKIT004 
#~ global WEBSERVICEIP
#~ global WEBSERVICEPORT
#~ global inputs_dict

INTERFACEKIT888 = 178346
INTERFACEKIT004 = 259173
WEBSERVICEIP = "192.168.128.250"
WEBSERVICEPORT = 5001
inputs_dict = dict()

########### Phidgets Setup ########
#Event Handler Callback Functions
def inferfaceKitAttached(e):
    attached = e.device
    ik = "InterfaceKit {} Attached".format(attached.getSerialNum())
    inputs_dict[ik] = "True"
    print("InterfaceKit %i Attached!" % (attached.getSerialNum()))

def interfaceKitDetached(e):
    detached = e.device
    ik = "InterfaceKit {} Attached".format(attached.getSerialNum())
    inputs_dict[ik] = "False"
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
        print(self.num_sensors)
        Clock.schedule_interval(self.check_status, 0.5)
    
    def check_status(self, instance):
        for index in range(self.num_sensors):
            sensor = "{} Sensor {}".format(self.devserial, index)
            inputs_dict[sensor] = self.interfaceKit.getSensorRawValue(index)
        

class Sensor(BoxLayout):
    
    def __init__(self, name, devserial, sensor_index, **kwargs):
    
        super(Sensor, self).__init__(**kwargs)
        self.devserial = devserial
        self.name = name
        self.device_label.text = name + ' ' + str(sensor_index)
        self.sensor_index = sensor_index

        Clock.schedule_interval(self.check_status, 1)

    def check_status(self, instance):
        '''Retrieves sensor values from internal dict, converts to proper units
        and updates the sensor widget value display
        '''
        
        sensor = "{} Sensor {}".format(self.devserial, self.sensor_index)
        val = inputs_dict[sensor]
        
        if 'voltage30' in self.name.lower():
            newval = ((val / 200.0) - 2.5) / 0.0681
            newval = '{:.0f} V'.format(newval)
        if 'temp' in self.name.lower():
            newval = ((val / 4.095) * 0.22222) - 61.111
            newval = '{:.0f} Celsius'.format(newval)
        self.status_ind.text = newval


class LTCApp(App):

    def build(self):
        # The 'build' method is called when the object is run.

        inputs = Inputs(devserial=INTERFACEKIT888, IP=WEBSERVICEIP, port=WEBSERVICEPORT)
        sens0 = Sensor('Temperature', INTERFACEKIT888, 0)
        sens1 = Sensor('Voltage30', INTERFACEKIT888, 1)
        sens5 = Sensor('Voltage30', INTERFACEKIT888, 5)
        sens6 = Sensor('Voltage30', INTERFACEKIT888, 6)
        sens7 = Sensor('Voltage30', INTERFACEKIT888, 7)
        
        inputs.add_widget(sens0)
        inputs.add_widget(sens1)
        inputs.add_widget(sens5)
        inputs.add_widget(sens6)
        inputs.add_widget(sens7)
            
        ltc = LTC()
        ltc.content.add_widget(inputs) 
        return ltc
    
    def build_config(self, config):
        config.add_section('rocket')
        config.set('rocket', 'index', '0')
        config.add_section('launch')
        config.set('launch', 'type', 'success')

    def build_settings(self, settings):
        settings.add_json_panel('Testing', self.config, data='''[
            { "type": "title", "title": "Rocket" },
            { "type": "numeric", "title": "Size",
              "desc": "Rocket size, from 0 to X",
              "section": "rocket", "key": "index" },
            { "type": "title", "title": "Launch" },
            { "type": "options", "title": "Launch",
              "desc": "The kind of launch you would like to have",
              "section": "launch", "key": "type",
              "options": ["success", "boom", "crunch"]}
        ]''')


if __name__ == '__main__':
    Config.set('graphics', 'width', '600')
    Config.set('graphics', 'height', '600')
    Config.set('graphics', 'fullscreen', '1')
    
    LTCApp().run()
