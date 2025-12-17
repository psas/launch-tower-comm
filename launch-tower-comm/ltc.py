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

from enum import Enum

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


class LTCLabel(Label):
    '''A display widget for the Phidget Relays in the launch tower computer.

    Loads from the kv lang file. Used by ltcbackend sensors.
    '''

    class State(Enum):
        DETACHED = [0.1, 0.1, 0.1, 1]
        THINKING = [0, 1, 1, 1]
        ON = [1, 0, 0, 1]
        OFF = [0, 1, 0.5, 1]
        ERROR = [1, 1, 0, 1]
        UNKNOWN = [0.1, 0.1, 0.1, 1]

    # TODO: ref Error, on click pop up detailed description
    background_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        # load from kv lang file first
        super().__init__(**kwargs)
        self.color = [1, 1, 1, 1]  # Set font color to white
        self.set_state(self.State.DETACHED)

    def set_state(self, state: State, text=''):
        match state:
            case self.State.THINKING:
                self.text = ""
            case _:
                if len(text) > 0:
                    self.text = text
                else:
                    self.text = state.name

    def on_attach(self, *args, **kwargs):
        self.set_state(self.State.THINKING)

    def on_detach(self, *args, **kwargs):
        self.set_state(self.State.DETACHED)

    def on_output_changed(self, event):
        if event.state:
            self.set_state(self.State.OFF)
        else:
            self.set_state(self.State.ON)

    def on_error(self, *args, **kwargs):
        self.set_state(self.State.ERROR)

    def on_button(self, *args, **kwargs):
        self.set_state(self.State.THINKING)


class StatusDisplay(BoxLayout):
    '''Displays the overall state of the LTC Phidget sensors, and a message.

    Loaded from kv lang file first.
    '''

    class State(Enum):
        NOMINAL = ("Shore power must be off to arm", [0.5, 0.5, 0.5, 1])
        ARMED = (
            "Press abort to disarm and return to unarmed tab",
            [1, 0, 0, 1],
        )
        DISARMED = ("The igniter is now off and safe", [0.5, 0.5, 0.5, 1])
        IGNITED = (
            "Click Ignite again to disable Ignition power",
            [0, 1, 0.5, 1],
        )
        ERROR = (
            "An error occurred, \nPlease try again",
            [1, 0, 0, 1],
        )
        DISCONNECTED = ("Please leave a message or call again.", [1, 1, 0, 1])
        ABORT_FAILED = (
            "The attempt to shut off the igniter failed.",
            [1, 0, 0, 1],
        )

        @property
        def message(self):
            return self.value[0]

        @property
        def color(self):
            return self.value[1]

    # TODO: scrollable log

    def __init__(self, **kwargs):
        # load from the kv lang file
        super().__init__(**kwargs)
        self.set_state(self.State.DISCONNECTED)

    def on_attach(self, *args, **kwargs):
        self.set_state(self.State.NOMINAL)

    def on_detach(self, *args, **kwargs):
        self.set_state(self.State.DISCONNECTED)

    def on_error(self, errno, *args, **kwargs):
        match errno:
            case 4103:
                log.error("Sensor value out of range")
            case _:
                self.set_state(self.State.ERROR)

    def on_ignite(self, event):
        if event.state:
            self.set_state(self.State.IGNITED)
        else:
            self.set_state(self.State.NOMINAL)

    def on_value(self, *args, **kwargs):
        self.set_state(self.State.NOMINAL)

    def set_state(self, state: State, *args):
        log.info(f"Setting StatusDisplay state to {state}")
        self.state_info.text = state.name
        self.state_info.color = state.color
        if args:
            self.state_message.text = args[0].message
        else:
            self.state_message.text = state.message


class InterfaceKitPanel(BoxLayout):
    '''Container for IOIndicators. Loaded from kv lang file.'''


class IOIndicator(BoxLayout):
    def __init__(self, sensor, **kwargs):
        '''Indicator widget. Includes a name label, and status label.'''
        super().__init__(**kwargs)

        self.nominal_value = sensor.nominal_value
        self.name = sensor.name
        self.unit = sensor.unit
        self.device_label.text = sensor.name

        sensor.add_callback(self.on_attach, 'attach')
        sensor.add_callback(self.on_detach, 'detach')
        sensor.add_callback(self.on_value, 'value')

    def on_attach(self, *args, **kwargs):
        self.ltc_label.set_state(LTCLabel.State.UNKNOWN)

    def on_detach(self, *args, **kwargs):
        self.ltc_label.set_state(LTCLabel.State.DETACHED)


class VoltageSensorIndicator(IOIndicator):
    def __init__(self, sensor, **kwargs):
        super().__init__(sensor, **kwargs)

    def on_value(self, sensor_reading, *args, **kwargs):
        if isinstance(sensor_reading, float):
            self.ltc_label.text = f"{sensor_reading:.1f} {self.unit}"
            self.ltc_label.background_color = self.nominal_value(sensor_reading)
        else:
            log.error(
                f"Unsupported type passed to {self.name} value callback: {type(sensor_reading)}"
            )


class RelayIndicator(IOIndicator):
    def __init__(self, sensor, **kwargs):
        super().__init__(sensor, **kwargs)

    def on_value(self, sensor_reading, *args, **kwargs):
        if isinstance(sensor_reading, bool):
            self.ltc_label.text = "On" if sensor_reading else "Off"
            self.ltc_label.background_color = self.nominal_value(sensor_reading)
        else:
            log.error(
                f"Unsupported type passed to {self.name} value callback: {type(sensor_reading)}"
            )


class RocketReadyIndicator(IOIndicator):
    def __init__(self, sensor, **kwargs):
        super().__init__(sensor, **kwargs)

    def on_value(self, sensor_reading, *args, **kwargs):
        if isinstance(sensor_reading, float):
            self.ltc_label.text = "High" if sensor_reading >= 2.0 else "Low"
            self.ltc_label.background_color = self.nominal_value(sensor_reading)
        else:
            log.error(
                f"Unsupported type passed to {self.name} value callback: {type(sensor_reading)}"
            )


class LTCApp(App):
    def build(self):
        # The 'build' method is called when the app is run.
        Builder.load_file("ltcctrl.kv")

        status = StatusDisplay()
        backend = LTCbackend(status.set_state)
        self.bind(on_stop=backend.close)
        self.bind(on_start=backend.start)

        sens0 = VoltageSensorIndicator(backend.sensors[0])
        # sens1 = IOIndicator(backend.sensors[3])
        # sens5 = IOIndicator(backend.sensors[2])
        sens6 = VoltageSensorIndicator(backend.sensors[1])
        sens7 = VoltageSensorIndicator(backend.sensors[3])
        sens8 = VoltageSensorIndicator(backend.sensors[4])
        sens9 = VoltageSensorIndicator(backend.sensors[5])
        sens4 = RocketReadyIndicator(backend.sensors[2])

        relay1 = RelayIndicator(backend.shore)
        relay2 = RelayIndicator(backend.ignition)

        input_panel = InterfaceKitPanel()
        relay_panel = InterfaceKitPanel()

        input_panel.add_widget(sens4)
        input_panel.add_widget(sens8)
        input_panel.add_widget(sens7)
        input_panel.add_widget(sens0)
        # input_panel.add_widget(sens1)
        # input_panel.add_widget(sens5)

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
        backend.shore.add_callback(ctrl.on_shorepower, "value")
        backend.ignition.add_callback(ctrl.on_ignite, "value")

        ltc = LTC()
        ltc.toplayout.add_widget(ctrl)
        ltc.toplayout.add_widget(status)
        ltc.indicators.add_widget(relay_panel)
        ltc.indicators.add_widget(input_panel)
        return ltc


if __name__ == '__main__':
    log.info("Starting LTCCOM")
    LTCApp().run()
