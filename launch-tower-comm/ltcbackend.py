'''
Created on May 22, 2013

@author: theo
'''

from ctypes import *
from datetime import datetime
import sys
import random
import time
from kivy.logger import Logger
# import logging
# log = Logger.getLogger(__name__)

log = Logger

# Phidgets specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, \
    ErrorEventArgs, InputChangeEventArgs, OutputChangeEventArgs, \
    SensorChangeEventArgs
from Phidgets.Devices.InterfaceKit import InterfaceKit


# # Kivy specific imports
import kivy
kivy.require('1.0.5')
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config, ConfigParser
from kivy.core.window import Window
from kivy.lang import Builder
# from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.properties import *
from kivy.extras.highlight import KivyLexer
from kivy.graphics import *

########### Phidgets Setup ########

class LTCPhidget(object):
    # TODO: logging
    # TODO: can the remote specific events find a disconnected usb cable?
    # TODO: thread
    devserial = 0
    IP = "0.0.0.0"
    port = 0

    def __init__(self, **kwargs):
        self.attach = kwargs.pop('attach', None)
        self.detach = kwargs.pop('detach', None)
        self.error = kwargs.pop('error', None)
        self.output = kwargs.pop('output', None)
        self.input = kwargs.pop('input', None)
        self.sense = kwargs.pop('sensor', None)
        log.debug("Acquiring InterfaceKit")
        self.ik = InterfaceKit()
        log.debug("Registering Handlers")
        if self.attach is not None:
            self.ik.setOnAttachHandler(self._onAttach)
        if self.detach is not None:
            self.ik.setOnDetachHandler(self._onDetach)
        if self.error is not None:
            self.ik.setOnErrorhandler(self._onError)
        if self.output is not None:
            self.ik.setOnOutputChangeHandler(self._onOutput)
        if self.input is not None:
            self.ik.setOnInputChangeHandler(self._onInput)
        if self.sense is not None:
            self.ik.setOnSensorChangeHandler(self._onSensor)
        log.debug("Opening remote IP")
        self.ik.openRemoteIP(self.IP, self.port, self.devserial)

    def _onAttach(self, event):
        self.attach(event)

    def _onDetach(self, event):
        self.detach(event)

    def _onError(self, event):
        if self.ik.isAttached():
            self.error(event)

    def _onOutput(self, event):
        self.output(event)

    def _onInput(self, event):
        self.input(event)

    def _onSensor(self, event):
        self.sense(event)

    def close(self):
        self.ik.closePhidget()

class Sensor(object):
    isRatiometric = None
    unit = ""
    def __init__(self, name):
        self.name = name

    def convert(self, sample):
        return sample

class VoltageSensor(Sensor):
    isRatiometric = False
    unit = "V"

    def convert(self, sample):
        return (sample / 200.0 - 2.5) / 0.0681

class TemperatureSensor(Sensor):
    isRatiometric = True
    unit = "C"

    def convert(self, sample):
        return (sample * 2.0 / 9.0) - 61.111

class CorePhidget(LTCPhidget):
    # Interface Kit 8/8/8 with sensors attached
    devserial = 178346
    IP = "192.168.128.251"
    port = 5001

    output24v = 1
    inputWindspeed = 7  # make a sensor?

    def __init__(self, **kwargs):
        self.sensor = dict()
        self.sensor[1] = VoltageSensor("vBatt")
        self.sensor[0] = TemperatureSensor("Internal Temperature")
        self.sensor[2] = Sensor("Humidity")
        self.sensor[3] = TemperatureSensor("External Temperature")
        self.sensor[4] = Sensor("Unused")
        self.sensor[5] = VoltageSensor("vChargeBatt")
        self.sensor[6] = VoltageSensor("5v")
        self.sensor[7] = VoltageSensor("24v")

        super(CorePhidget, self).__init__(**kwargs)

    def _onAttach(self, event):
        self.ik.setRatiometric(False)
        self.attach(event)

    def _onSensor(self, event):
        module = self.sensor[event.index]
        if module.isRatiometric:
            self.ik.setRatiometric(True)
            event.value = self.ik.getSensorValue(event.index)
            self.ik.setRatiometric(False)
        event.sensor = self.sensor[event.index]
        self.sense(event)

    def set24vState(self, state):
        self.ik.setOutputState(self.output24v, state)

class IgnitionRelay(LTCPhidget):
    # Interface Kit 0/0/4 with relays
    devserial = 259173
    IP = "192.168.128.251"
    port = 5001
    relay_index = 1

    def _onOutput(self, event):
        if event.index == self.relay_index:
            self.output(event)

    def toggleIgnitionRelayState(self, event):
        if self.ik.isAttached():
            state = self.ik.getOutputState(self.relay_index)
            self.setIgnitionRelayState(not state)

    def setIgnitionRelayState(self, state):
        self.ik.setOutputState(self.relay_index, state)

class LTCbackend(object):

    def __init__(self, central_dict):
        log.info("Starting Backend")
        self.central_dict = central_dict
        self.relay = IgnitionRelay(attach=self.attach,
                                   detach=self.detach,
                                   error=self.error,
                                   output=self.output)
        self.core = CorePhidget(attach=self.attach,
                                detach=self.detach,
                                error=self.error,
                                output=self.output,
                                input=self.input,
                                sensor=self.sensor)
    def attach(self, event):
        attached = event.device
        ik = "{} InterfaceKit Attached".format(attached.getSerialNum())
        log.info(ik)
        self.central_dict[ik] = "True"

    def detach(self, event):
        attached = event.device
        ik = "{} InterfaceKit Detached".format(attached.getSerialNum())
        log.info(ik)
        self.central_dict[ik] = "False"

    def error(self, event):
        try:
            source = event.device
            log.info("InterfaceKit %i: Phidget Error %i: %s"
                  % (source.getSerialNum(), event.eCode, event.description))
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (event.code, event.details))

    def output(self, event):
        source = event.device
        output = "{} Output {}".format(source.getSerialNum(), event.index)
        log.info(output)
        self.central_dict[output] = str(event.state)

    def input(self, event):
        source = event.device
        input = "{} Input {}".format(source.getSerialNum(), event.index)
        log.info(input)
        self.central_dict[input] = str(event.state)

    def sensor(self, event):
        source = event.device
        sensor = "{} Sensor {}".format(source.getSerialNum(), event.index)
        log.info(sensor)
        self.central_dict[sensor] = str(event.value)

    def close(self, event):
        log.debug("Closing LTCBackend")
        self.relay.close()
        self.core.close()

    def ignite(self, state):
        # TODO: cross check with shorepower
        self.relay.setIgnitionRelayState(state)

    def shorepower(self, state):
        self.core.set24vState(state)

class RelayLabel(Label):
    # TODO: ref Error, on click pop up detailed description
    background_color = ListProperty([1, 1, 1, 1])
    states = {"Detached": [1, 1, 1, 1],
            "Thinking": [0, 1, 1, 1],
            "Open": [0, 1, .5, 1],
            "Closed": [1, 0, 0, 1],
            "Error": [1, 1, 0, 1]}
    def __init__(self, **kwargs):
        super(RelayLabel, self).__init__(**kwargs)
        self.set_state("Detached")

    def set_state(self, state):
        self.background_color = self.states[state]
        if state == "Thinking":
            self.text = ""
        else:
            self.text = state

    def on_attach(self, event):
        self.set_state("Thinking")

    def on_detach(self, event):
        self.set_state("Detached")

    def on_output_changed(self, event):
        if event.state:
            self.set_state("Open")
        else:
            self.set_state("Closed")

    def on_error(self, event):
        self.set_state("Error")

    def on_button(self, event):
        self.set_state("Thinking")

class ltcbackendApp(App):
    def build(self):
        box = BoxLayout()
        rl = RelayLabel()
        button = Button(text="Toggle Relay")
        ir = IgnitionRelay(attach=rl.on_attach,
                           detach=rl.on_detach,
                           output=rl.on_output_changed,
                           error=rl.on_error)
        button.bind(on_press=ir.toggleIgnitionRelayState)
        box.add_widget(rl)
        box.add_widget(button)

        def on_stop_event(event):
            ir.close()
        self.bind(on_stop=on_stop_event)

        return box

if __name__ == '__main__':

    ltcbackendApp().run()
#     print "starting"
#     a = CorePhidget()
#     while not a.ik.isAttached():
#         pass
#     a.ik.setRatiometric(True)
#     for i in range(2):
#         print (a.ik.getSensorValue(0) * 2 / 9) - 61.111
# #         print (a.ik.getSensorValue(0) / 200 - 2.5) / 0.0681
#         time.sleep(1)
#
#     a.close()
#
#     a = Relays()
#     while not a.isAttached():
#         pass
#
#     time.sleep(100)
#     a.closePhidget()
#     time.sleep(1)
#     try:
#         pass
# #         a.print_info()
# #         a.test_outstate()
#     finally:
#         a.close_ltc()

