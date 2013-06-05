#!/usr/bin/env python


# TODO: start phidgets service on startup
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

from ctypes import *
from datetime import datetime
import sys
import random
# import logging
from kivy.logger import Logger
# logging.root = Logger  # Make kivy play nice with python logging module

from ltcbackend import LTCbackend
# Kivy specific imports
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
from kivy.uix.image import AsyncImage
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.extras.highlight import KivyLexer



VERSION = '0.2'

INTERFACEKIT888 = 178346
INTERFACEKIT004 = 259173
WEBSERVICEIP = "192.168.128.251"
WEBSERVICEPORT = 5001
central_dict = dict()

########### Phidgets Setup ########



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

    def __init__(self, action, *args, **kwargs):
        self.action = action
        super(Relay, self).__init__(*args, **kwargs)

        btn = ToggleButton(text='Toggle Relay')
        btn.bind(state=self.set_relay_state)
        self.label_slot.add_widget(btn)
        return

    def set_relay_state(self, instance, value):
        try:
            if value == 'down':
                self.action(True)
            elif value == 'normal':
                self.action(False)
        except PhidgetException:
            pass

class LTCApp(App):

    def build(self):
        # The 'build' method is called when the app is run.
        backend = LTCbackend(central_dict)
        self.bind(on_stop=backend.close)
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

        action = backend.relay.setIgnitionRelayState
        relay1 = Relay(action, 'Relay Foo', 'output', INTERFACEKIT004, 1)
        relay2 = Relay(action, 'Relay Bar', 'output', INTERFACEKIT004, 2)
        relay3 = Relay(action, 'Relay Baz', 'output', INTERFACEKIT004, 3)

        relay_panel = InterfaceKitPanel(INTERFACEKIT004)
        relay_panel.add_widget(relay1)
        relay_panel.add_widget(relay2)
        relay_panel.add_widget(relay3)

        ltc = LTC()
        ltc.indicators.add_widget(input_panel)
        ltc.indicators.add_widget(relay_panel)
        
        for i in range(10):
            src = "http://placehold.it/480x270.png&text=StateInfo-%d&.png" % i
            image = AsyncImage(source=src, allow_stretch=True)
            ltc.status_info.add_widget(image)

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
#     for a in dir(Logger):
#         print a

#     logging.basicConfig(level=logging.INFO)
    LTCApp().run()
