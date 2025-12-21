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

import kivy
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.widget import Widget

import ltclogger as log
from ltcbackend import LTCbackend
from ltcctrl import LTCctrl
from ltcui import (
    InterfaceKitPanel,
    RelayIndicator,
    RocketReadyIndicator,
    StatusDisplay,
    VoltageSensorIndicator,
)

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


class LTCApp(App):
    def build(self):
        # The 'build' method is called when the app is run.
        Builder.load_file("ltcctrl.kv")

        status = StatusDisplay()
        backend = LTCbackend()
        # callbacks receive self arg, backend does not need
        self.bind(on_stop=lambda _: backend.close)
        self.bind(on_start=lambda _: backend.start)

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
