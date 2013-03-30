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
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.extras.highlight import KivyLexer


INTERFACEKIT888 = 178346
INTERFACEKIT004 = 259173
WEBSERVICEIP = "192.168.128.250"
WEBSERVICEPORT = 5001
app_dict = dict()

########### Phidgets Setup ########


#Event Handler Callback Functions
def inferfaceKitAttached(e):
    attached = e.device
    ik = "InterfaceKit {} Attached".format(attached.getSerialNum())
    app_dict[ik] = "True"
    print("InterfaceKit %i Attached!" % (attached.getSerialNum()))


def interfaceKitDetached(e):
    detached = e.device
    ik = "InterfaceKit {} Attached".format(attached.getSerialNum())
    app_dict[ik] = "False"
    print("InterfaceKit %i Detached!" % (detached.getSerialNum()))


def interfaceKitError(e):
    try:
        source = e.device
        print("InterfaceKit %i: Phidget Error %i: %s"
              % (source.getSerialNum(), e.eCode, e.description))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))


def interfaceKitSensorChanged(e):
    source = e.device
    sensor = "{} Sensor {}".format(source.getSerialNum(), e.index)
    app_dict[sensor] = str(e.value)
    print("InterfaceKit %i: Sensor %i: %i"
          % (source.getSerialNum(), e.index, e.value))


########### KIVY Setup ############

class LTC(FloatLayout):
    # Loaded from the kv lang file
    pass


class InterfaceKitPanel(BoxLayout):

    def __init__(self, devserial, IP, port, **kwargs):
        self.devserial = devserial
        self.IP = IP
        self.port = port
        super(InterfaceKitPanel, self).__init__(**kwargs)

        # Add extra column for a control indicator
        if '259173' in str(self.devserial):
            # These widgets are from kv language templates.
            # This instantiates them.
            vsep = Builder.template('VSeparator')
            lbl = Builder.template('MyLabel', text='Toggle it', font_size=20)
            self.labels.add_widget(vsep)
            self.labels.add_widget(lbl)

        # Create an interfacekit object
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
            interfaceKit.openRemoteIP(self.IP, self.port, self.devserial)
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
        self.device_name = interfaceKit.getDeviceName()
        self.num_sensors = self.interfaceKit.getSensorCount()
        self.num_outputs = self.interfaceKit.getOutputCount()

        Clock.schedule_interval(self.check_status, 0.5)
        return

    def check_status(self, instance):
        if '8/8/8' in self.device_name:
            for index in xrange(self.num_sensors):
                io = "{} SENSOR {}".format(self.devserial, index)
                app_dict[io] = self.interfaceKit.getSensorRawValue(index)

        if '0/0/4' in self.device_name:
            for index in xrange(self.num_outputs):
                io = "{} OUTPUT {}".format(self.devserial, index)
                app_dict[io] = self.interfaceKit.getOutputState(index)
        return


class IOIndicator(BoxLayout):

    def __init__(self, name, iotype, devserial, ioindex, **kwargs):
        '''Indicator widget. Includes a name label, and status label.

        name<str>:      Real IO thing name. ex: "Wind Speed", "Battery Voltage"
        iotype<str>:    Phidget name for channel. ex: "output" "sensor" "input"
        ioindex<int>:   Channel index.
        devserial<str>: Serial of InterfaceKit on which this channel is found.
        '''
        self.name = name
        self.iotype = iotype.upper()
        self.ioindex = ioindex
        self.devserial = devserial
        super(IOIndicator, self).__init__(**kwargs)

        self.device_label.text = name + ' ' + str(ioindex)
        Clock.schedule_interval(self.check_status, 1)
        return

    def check_status(self, instance):
        '''Retrieves values from internal dict, converts to proper units
        and updates the sensor widget value display
        '''
        io = "{} {} {}".format(self.devserial, self.iotype, self.ioindex)
        val = app_dict[io]

        if 'volt' in self.name.lower():
            newval = ((val / 200.0) - 2.5) / 0.0681
            newval = '{:.0f} V'.format(newval)
        if 'temp' in self.name.lower():
            newval = ((val / 4.095) * 0.22222) - 61.111
            newval = '{:.0f} Celsius'.format(newval)
        if 'relay' in self.name.lower():
            newval = 'OPEN' if val else 'CLOSED'

        self.status_ind.text = newval
        return


class Relay(IOIndicator):

    def __init__(self, *args, **kwargs):
        super(Relay, self).__init__(*args, **kwargs)

        btn = ToggleButton(text='Toggle Relay')
        btn.bind(state=self.check_relay_state)
        self.label_slot.add_widget(btn)
        return

    def check_relay_state(self, instance, value):
        print 'My button <%s> state is <%s>' % (instance, value)
        return


class LTCApp(App):

    def build(self):
        # The 'build' method is called when the object is run.

        input_panel = InterfaceKitPanel(INTERFACEKIT888, WEBSERVICEIP,
                                        WEBSERVICEPORT)
        # name, iotype, ioindex, devserial,
        sens0 = IOIndicator('Temperature', 'sensor', INTERFACEKIT888, 0)
        sens1 = IOIndicator('Voltage30', 'sensor', INTERFACEKIT888, 1)
        sens5 = IOIndicator('Voltage30', 'sensor', INTERFACEKIT888, 5)
        sens6 = IOIndicator('Voltage30', 'sensor', INTERFACEKIT888, 6)
        sens7 = IOIndicator('Voltage30', 'sensor', INTERFACEKIT888, 7)

        input_panel.add_widget(sens0)
        input_panel.add_widget(sens1)
        input_panel.add_widget(sens5)
        input_panel.add_widget(sens6)
        input_panel.add_widget(sens7)

        relay_panel = InterfaceKitPanel(INTERFACEKIT004, WEBSERVICEIP,
                                        WEBSERVICEPORT)
        relay1 = Relay('Okay Relay', 'output', INTERFACEKIT004, 1)
        relay2 = Relay('Fancy Relay', 'output', INTERFACEKIT004, 2)
        relay3 = Relay('Nice Relay', 'output', INTERFACEKIT004, 3)

        relay_panel.add_widget(relay1)
        relay_panel.add_widget(relay2)
        relay_panel.add_widget(relay3)

        ltc = LTC()
        ltc.content.add_widget(input_panel)
        ltc.content.add_widget(relay_panel)
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
    LTCApp().run()
