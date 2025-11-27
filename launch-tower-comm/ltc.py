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

from types import MappingProxyType

import kivy
import ltclogger as log
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from ltcbackend import LTCbackend
from ltcctrl import LTCctrl
from Phidget22.PhidgetException import PhidgetException

VERSION = '0.2'

kivy.require('1.0.5')
Config.set('kivy', 'log_enable', '0')
# This unhelpfully also turns off unhandled exception reporting.
# You would hope an exception would be a critical thing but nope.
# Config.set('kivy', 'log_level', 'critical')
Config.set('kivy', 'desktop', '1')
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '800')
# Config.set('graphics', 'fullscreen', 'auto')


class LTC(Widget):
    # Loaded from the kv lang file. Other objects added here.
    app = ObjectProperty(None)
    box_layout = ObjectProperty(None)
    version = StringProperty(VERSION)


class RelayLabel(Label):
    '''A display widget for the Phidget Relays in the launch tower computer.

    Loads from the kv lang file. Used by ltcbackend sensors.
    '''

    # TODO: ref Error, on click pop up detailed description
    background_color = ListProperty([1, 1, 1, 1])
    states = MappingProxyType(
        {
            "Detached": [0.1, 0.1, 0.1, 1],
            "Thinking": [0, 1, 1, 1],
            "Open": [1, 0, 0, 1],
            "Closed": [0, 1, 0.5, 1],
            "Error": [1, 1, 0, 1],
            "Unknown": [0.1, 0.1, 0.1, 1],
        }
    )

    def __init__(self, **kwargs):
        # load from kv lang file first
        super().__init__(**kwargs)
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
            self.color = [1, 1, 1, 0.1]
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
    '''Displays the overall state of the LTC Phidget sensors, and a message.

    Loaded from kv lang file first.
    '''

    # TODO: scrollable log
    states = MappingProxyType(
        {
            "Nominal": ("Disable Shore power to arm", [0.5, 0.5, 0.5, 1]),
            "ARMED": ("You could abort", [1, 0, 0, 1]),
            "Disarmed": ("The igniter is now off and safe", [0.5, 0.5, 0.5, 1]),
            "IGNITED!": ("Click Ignite again to disable Ignition power", [0, 1, 0.5, 1]),
            "Phidget Call Failed": (
                "Phidgets didn't get the message, \nplease try again",
                [1, 0, 0, 1],
            ),
            "Disconnected": ("Please leave a message or call again.", [1, 1, 0, 1]),
            "Abort Failed": ("The attempt to shut off the igniter failed.", [1, 0, 0, 1]),
        }
    )

    def __init__(self, **kwargs):
        # load from the kv lang file
        super().__init__(**kwargs)
        self.set_state("Disconnected")

    def on_attach(self):
        self.set_state("Nominal")

    def on_detach(self, event):
        self.set_state("Disconnected")

    def on_error(self, event):
        self.set_state("Phidget Call Failed")

    def on_ignite(self, event):
        if event.state:
            self.set_state('IGNITED!')
        else:
            self.set_state("Nominal")

    def on_value(self, event):
        self.set_state("Nominal")

    def set_state(self, state):
        log.info(f"State changed:{state}")
        self.state_info.text = state
        self.state_info.color = self.states[state][1]
        self.state_message.text = self.states[state][0]


class InterfaceKitPanel(BoxLayout):
    '''Container for IOIndicators. Loaded from kv lang file.'''


class IOIndicator(BoxLayout):
    def __init__(self, sensor, **kwargs):
        '''Indicator widget. Includes a name label, and status label.'''
        super().__init__(**kwargs)

        self.nominal_value = sensor.nominal_value
        self.name = sensor.name
        self.unit = sensor.unit
        self.get_reading = sensor.get_reading
        self.device_label.text = sensor.name
        self.status_ind.set_state('Unknown')

        sensor.add_callback(self.on_attach, 'attach')
        sensor.add_callback(self.on_detach, 'detach')
        sensor.add_callback(self.on_value, 'value')

    def on_attach(self):
        self.status_ind.set_state('Closed')

    def on_detach(self, event):
        self.status_ind.set_state('Detached')

    def on_value(self):
        try:
            sensor_reading = self.get_reading()
            print(f"{self.name}: {sensor_reading} type: {type(sensor_reading)}")
            if isinstance(sensor_reading, str):
                self.status_ind.text = f'{sensor_reading} {self.unit}'
            else:
                self.status_ind.text = f'{sensor_reading:.1f} {self.unit}'

            self.status_ind.background_color = self.nominal_value(sensor_reading)
        except PhidgetException as e:
            log.error(f"{self.name}: {e}")


class LTCApp(App):
    def build(self):
        # The 'build' method is called when the app is run.
        Builder.load_file("ltcctrl.kv")

        status = StatusDisplay()
        backend = LTCbackend(status.set_state)
        self.bind(on_stop=backend.close)
        self.bind(on_start=backend.start)

        sens0 = IOIndicator(backend.sensors[0])
        sens1 = IOIndicator(backend.sensors[3])
        sens5 = IOIndicator(backend.sensors[2])
        sens6 = IOIndicator(backend.sensors[1])
        sens7 = IOIndicator(backend.sensors[5])
        sens8 = IOIndicator(backend.sensors[6])
        sens9 = IOIndicator(backend.sensors[7])
        sens4 = IOIndicator(backend.sensors[4])

        relay1 = IOIndicator(backend.shore)
        relay2 = IOIndicator(backend.ignition)

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

        for sensor in backend.sensors:
            sensor.add_callback(status.on_attach, 'attach')
            sensor.add_callback(status.on_detach, 'detach')
            sensor.add_callback(status.on_error, 'error')

        backend.ignition.add_callback(status.on_attach, 'attach')
        backend.ignition.add_callback(status.on_detach, 'detach')
        backend.ignition.add_callback(status.on_error, 'error')

        backend.shore.add_callback(status.on_attach, 'attach')
        backend.shore.add_callback(status.on_detach, 'detach')
        backend.shore.add_callback(status.on_error, 'error')

        ctrl = LTCctrl(backend.ignite, backend.shorepower, status.set_state)
        # backend.shore.add_callback(ctrl.on_shorepower, "value")
        # backend.ignition.add_callback(ctrl.on_ignite, "value")

        ltc = LTC()
        ltc.toplayout.add_widget(ctrl)
        ltc.toplayout.add_widget(status)
        ltc.indicators.add_widget(relay_panel)
        ltc.indicators.add_widget(input_panel)
        return ltc


if __name__ == '__main__':
    log.info("Starting LTCCOM")
    LTCApp().run()
