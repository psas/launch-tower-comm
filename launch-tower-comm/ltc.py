#!/usr/bin/env python

'''ltc.py

Copyright (C) 2013 John K. Boyle

This file is part of launch-tower-comm.

launch-tower-comm is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

launch-tower-comm is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with launch-tower-comm.  If not, see <http://www.gnu.org/licenses/>.

Much of the Phidgets code comes from InterfaceKit-simple.py, written by Adam
Stelmack of Phidgets Inc, Copyright 2010.  It is under the Creative Commons
Attribution 2.5 Canada License.

Some of the kv language code in ltc.kv is copied from IcarusTouch,
written by Cyril Stoller, (C) 2011, under GPLv3.

'''

USE_PHIDGETS = False


from ctypes import *
from datetime import datetime
import sys
import random


# Phidgets specific imports
if USE_PHIDGETS:
    from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
    from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, \
        ErrorEventArgs, InputChangeEventArgs, OutputChangeEventArgs, \
        SensorChangeEventArgs
    from Phidgets.Devices.InterfaceKit import InterfaceKit

# Kivy specific imports
import kivy
kivy.require('1.0.5')
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config, ConfigParser
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.extras.highlight import KivyLexer

VERSION = '0.2'

INTERFACEKIT888 = 178346
INTERFACEKIT004 = 259173
WEBSERVICEIP = "192.168.128.251"
WEBSERVICEPORT = 5001
central_dict = dict()

########### Phidgets Setup ########

class LTCbackend(object):

    def __init__(self, devserial, IP, port):
        self.devserial = devserial
        self.IP = IP
        self.port = port
        if USE_PHIDGETS:
            # Create an interfacekit object
            try:
                self.ik = InterfaceKit()
            except RuntimeError as e:
                print("Runtime Exception: %s" % e.details)
                print("Exiting....")
                exit(1)

        # Set Event Handlers
            try:
                self.ik.setOnAttachHandler(self.inferfaceKitAttached)
                self.ik.setOnDetachHandler(self.interfaceKitDetached)
                self.ik.setOnErrorhandler(self.interfaceKitError)

                self.ik.openRemoteIP(self.IP, self.port, self.devserial)
            except PhidgetException as e:
                print("Phidget Exception %i: %s" % (e.code, e.details))
                print("Exiting....")
                exit(1)

            print("Waiting for attach....")


    def close_ltc(self):  # TODO: this should probably be called somewhere
        try:
            self.ik.closePhidget()
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")
            exit(1)

    def check_status(self, instance):
        if '8/8/8' in self.device_name:
            for index in xrange(self.num_sensors):
                io = "{} SENSOR {}".format(self.devserial, index)
                central_dict[io] = self.ik.getSensorValue(index)

        if '0/0/4' in self.device_name:
            for index in xrange(self.num_outputs):
                io = "{} OUTPUT {}".format(self.devserial, index)
                central_dict[io] = self.ik.getOutputState(index)

    def log_sensor_values(self, instance):
        for key, value in central_dict.iteritems():
            Logger.info('{}: {}, {}'.format(key, value, datetime.now()))

    # Event Handler Callback Functions
    def inferfaceKitAttached(self, e):
        attached = e.device
        ik = "{} InterfaceKit Attached".format(attached.getSerialNum())
        central_dict[ik] = "True"
        print("InterfaceKit %i Attached!" % (attached.getSerialNum()))

        self.device_name = self.ik.getDeviceName()
        self.num_sensors = self.ik.getSensorCount()
        self.num_outputs = self.ik.getOutputCount()

        # Voltage sensors are not ratiometric
        if '8/8/8' in self.device_name:
            self.ik.setRatiometric(False)

        # Schedule sensor polling
        Clock.schedule_interval(self.check_status, 0.5)
        Clock.schedule_interval(self.log_sensor_values, 1)


    def interfaceKitDetached(self, e):
        detached = e.device
        ik = "{} InterfaceKit Attached".format(detached.getSerialNum())
        central_dict[ik] = "False"
        print("InterfaceKit %i Detached!" % (detached.getSerialNum()))


    def interfaceKitError(self, e):
        try:
            source = e.device
            print("InterfaceKit %i: Phidget Error %i: %s"
                  % (source.getSerialNum(), e.eCode, e.description))
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))

    # Maybe use this rather than polling?
    def interfaceKitSensorChanged(self, e):
        source = e.device
        sensor = "{} Sensor {}".format(source.getSerialNum(), e.index)
        central_dict[sensor] = str(e.value)
        print("InterfaceKit %i: SENSOR %i: %i"
              % (source.getSerialNum(), e.index, e.value))

########### KIVY Setup ############

class LTC(Widget):
    # Loaded from the kv lang file and here.
    app = ObjectProperty(None)
    box_layout = ObjectProperty(None)
    version = StringProperty(VERSION)



class InterfaceKitPanel(BoxLayout):

    def __init__(self, devserial, **kwargs):
        super(InterfaceKitPanel, self).__init__(**kwargs)

        # Add extra column for a control indicator
        if '259173' in str(devserial):
            # These widgets are from kv language templates.
            # This instantiates them.
            vsep = Builder.template('VSeparator')
            lbl = Builder.template('MyLabel', text='Toggle it', font_size=20)
            self.labels.add_widget(vsep)
            self.labels.add_widget(lbl)


class IOIndicator(BoxLayout):

    def __init__(self, name, iotype, devserial, ioindex, **kwargs):
        '''Indicator widget. Includes a name label, and status label.

        name<str>:      Real IO thing name. ex: "Wind Speed", "Battery Voltage"
        iotype<str>:    Phidget name for channel: "output" "sensor" "input"
        ioindex<int>:   Channel index.
        devserial<str>: Serial # of InterfaceKit where this channel is found.
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
        try:
            val = central_dict[io]
        except KeyError:
            val = 0  # default value if sensor doesn't exist

        if 'volt' in self.name.lower():
            newval = val / 13.62 - 36.7107
            newval = '{:.0f} V'.format(newval)

        if 'temp' in self.name.lower():
            newval = ((val / 4.095) * 0.22222) - 61.111
            newval = '{:.0f} Celsius'.format(newval)

        if 'relay' in self.name.lower():
            newval = 'CLOSED' if val else 'OPEN'

        self.status_ind.text = newval
        return


class Relay(IOIndicator):

    def __init__(self, ltcbackend, *args, **kwargs):
        self.ltcbackend = ltcbackend
        super(Relay, self).__init__(*args, **kwargs)

        btn = ToggleButton(text='Toggle Relay')
        btn.bind(state=self.set_relay_state)
        self.label_slot.add_widget(btn)
        return

    def set_relay_state(self, instance, value):
        if value == 'down':
            self.ltcbackend.ik.setOutputState(self.ioindex, True)
        elif value == 'normal':
            self.ltcbackend.ik.setOutputState(self.ioindex, False)
        return


class LTCApp(App):

    def build(self):
        # The 'build' method is called when the app is run.

        input_panel = InterfaceKitPanel(INTERFACEKIT888)
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

        #relay_ik = LTCbackend(INTERFACEKIT004, WEBSERVICEIP, WEBSERVICEPORT)
        if USE_PHIDGETS:
            relay_ik = LTCbackend(INTERFACEKIT004, WEBSERVICEIP, WEBSERVICEPORT)
        else:
            relay_ik = Widget()

        relay1 = Relay(relay_ik, 'Relay Foo', 'output', INTERFACEKIT004, 1)
        relay2 = Relay(relay_ik, 'Relay Bar', 'output', INTERFACEKIT004, 2)
        relay3 = Relay(relay_ik, 'Relay Baz', 'output', INTERFACEKIT004, 3)

        relay_panel = InterfaceKitPanel(INTERFACEKIT004)
        relay_panel.add_widget(relay1)
        relay_panel.add_widget(relay2)
        relay_panel.add_widget(relay3)


        ltc = LTC()
        ltc.box_layout.add_widget(input_panel)
        ltc.box_layout.add_widget(relay_panel)

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
    #USE_PHIDGETS = False

    LTCApp().run()
