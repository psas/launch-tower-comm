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

from ctypes import *
from datetime import datetime
import sys
import random
# import logging
from kivy.logger import Logger
# logging.root = Logger  # Make kivy play nice with python logging module

from ltcbackend import LTCbackend
from ltcctrl import LTCctrl
# Kivy specific imports
import kivy
kivy.require('1.0.5')
from kivy.config import Config, ConfigParser
# Config.set('graphics', 'fullscreen', 'auto')
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, ListProperty
from kivy.extras.highlight import KivyLexer

from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import ErrorEventArgs, KeyChangeEventArgs, ServerConnectArgs, ServerDisconnectArgs
from Phidgets.Dictionary import Dictionary, DictionaryKeyChangeReason, KeyListener

VERSION = '0.2'

class LTC(Widget):
    # Loaded from the kv lang file and here.
    app = ObjectProperty(None)
    box_layout = ObjectProperty(None)
    version = StringProperty(VERSION)


class RelayLabel(Label):
    # TODO: ref Error, on click pop up detailed description
    background_color = ListProperty([1, 1, 1, 1])
    states = {"Detached": [.1, .1, .1, 1],
            "Thinking": [0, 1, 1, 1],
            "Open": [1, 0, 0, 1],
            "Closed": [0, 1, .5, 1],
            "Error": [1, 1, 0, 1],
            "Unknown":[.1, .1, .1, 1]}
    def __init__(self, **kwargs):
        super(RelayLabel, self).__init__(**kwargs)
        self.set_state("Detached")

    def set_state(self, state, text=''):
        self.background_color = self.states[state]
        if state == "Thinking":
            self.text = ""
        elif text:
            self.text = text
        else:
            self.text = state

        if state == 'Unknown':
            self.color = [1, 1, 1, .1]
        else:
            self.color = [1, 1, 1, 1]

    def on_attach(self, event):
        self.set_state("Thinking")

    def on_detach(self, event):
        self.set_state("Detached")

    def on_output_changed(self, event):
        if event.state:
            self.set_state("Closed")
        else:
            self.set_state("Open")

    def on_error(self, event):
        self.set_state("Error")

    def on_button(self, event):
        self.set_state("Thinking")

class StatusDisplay(BoxLayout):
    # TODO: scrollable log
    states = {
            "Nominal": ("Disable Shore power to arm", [.5, .5, .5, 1]),
            "ARMED": ("You could abort", [1, 0, 0, 1]),
            "IGNITED!": ("Click Ignite again to disable Ignition power", [0, 1, .5, 1]),
            "Phidget Call Failed": ("Phidgets had a problem and didn't \nget the message, please try again", [1, 0, 0, 1]),
            "Disconnected": ("Phidgets can't be reached right now. \nPlease leave a message or call again.", [1, 1, 0, 1]),
            "CRITICAL: Abort Failed": ("No response was received from the ignition relay while attempting to disarm it. \nUse extreme caution.", [1, 0, 0, 1])
            }
    def __init__(self, **kwargs):
        '''Displays the state and a (hopefully) helpful message.'''

        super(StatusDisplay, self).__init__(**kwargs)
        self.set_state("Disconnected")

    def on_attach(self, event):
        self.set_state("Nominal")

    def on_detach(self, event):
        self.set_state("Disconnected")

    def on_error(self, event):
        self.set_state("Phidget Call Failed")

    def on_ignite(self, event):
        if event.state is True:
            self.set_state('IGNITED!')
        else:
            self.set_state("Nominal")

    def on_value(self, event):
        self.set_state("Nominal")

    def set_state(self, state):
        self.state_info.text = state
        self.state_info.color = self.states[state][1]
        self.status_message.text = self.states[state][0]


class InterfaceKitPanel(BoxLayout):
    pass


class IOIndicator(BoxLayout):
    def __init__(self, sensor, **kwargs):
        '''Indicator widget. Includes a name label, and status label.
        '''
        super(IOIndicator, self).__init__(**kwargs)
        self.name = sensor.name
        self.unit = sensor.unit
        self.conversion = sensor.convert
        self.device_label.text = sensor.name
        self.status_ind.set_state('Unknown')
        sensor.add_callback(self.on_attach, 'attach')
        sensor.add_callback(self.on_detach, 'detach')
        sensor.add_callback(self.on_value, 'value')

    def on_attach(self, event):
        self.status_ind.set_state('Closed')

    def on_detach(self, event):
        self.status_ind.set_state('Detached')

    def on_value(self, event):
        try:
            val = event.value
        except AttributeError:
            val = event.state

        if val is 0:  # The sensors seem to return 0 when absent.
            self.status_ind.set_state('Open', 'Not Found')
            return

        newval = self.conversion(val)
        if isinstance(newval, str):
            self.status_ind.text = '{} {}'.format(newval, self.unit)
        else:
            self.status_ind.text = '{:.1f} {}'.format(newval, self.unit)


class LTCApp(App):

    def build(self):
        # The 'build' method is called when the app is run.
        Builder.load_file("ltcctrl.kv")
        backend = LTCbackend()
        self.bind(on_stop=backend.close)
        self.bind(on_start=backend.start)

        sens0 = IOIndicator(backend.core.sensor[0])
        sens1 = IOIndicator(backend.core.sensor[3])
        sens5 = IOIndicator(backend.core.sensor[2])
        sens6 = IOIndicator(backend.core.sensor[1])
        sens7 = IOIndicator(backend.core.sensor[5])
        sens8 = IOIndicator(backend.core.sensor[6])
        sens9 = IOIndicator(backend.core.sensor[7])
        sens4 = IOIndicator(backend.core.sensor[4])
        relay1 = IOIndicator(backend.core.shorepower)
        relay2 = IOIndicator(backend.relay.relay)

        input_panel = InterfaceKitPanel()
        relay_panel = InterfaceKitPanel()

        input_panel.add_widget(sens8)
        input_panel.add_widget(sens7)
        input_panel.add_widget(sens0)
        input_panel.add_widget(sens1)
        input_panel.add_widget(sens5)

        relay_panel.add_widget(sens4)
        relay_panel.add_widget(relay2)
        relay_panel.add_widget(sens6)
        relay_panel.add_widget(relay1)
        relay_panel.add_widget(sens9)

        status = StatusDisplay()
        backend.core.add_callback(status.on_attach, 'attach')
        backend.core.add_callback(status.on_detach, 'detach')
        backend.core.add_callback(status.on_error, 'error')
        backend.relay.add_callback(status.on_attach, 'attach')
        backend.relay.add_callback(status.on_detach, 'detach')
        backend.relay.add_callback(status.on_error, 'error')
        backend.relay.relay.add_callback(status.on_ignite, 'value')

        ctrl = LTCctrl(backend.ignite, backend.shorepower, status.set_state)
        backend.core.shorepower.add_callback(ctrl.on_shorepower, "value")
        backend.relay.relay.add_callback(ctrl.on_ignite, "value")
        ltc = LTC()
        ltc.indicators.add_widget(relay_panel)
        ltc.indicators.add_widget(input_panel)
        ltc.toplayout.add_widget(ctrl)
        ltc.toplayout.add_widget(status)
        return ltc

if __name__ == '__main__':
    LTCApp().run()
