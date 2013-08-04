from ctypes import *
from datetime import datetime
import sys
import time
# kivy logger because kivy breaks with normal python logger
from kivy.logger import Logger
# import logging
# log = Logger.getLogger(__name__)

log = Logger

# Phidgets specific imports
from Phidgets.PhidgetException import PhidgetException
from Phidgets.Devices.InterfaceKit import InterfaceKit

########### Phidgets Setup ########

LTCIP = '192.168.128.2'

class LTCPhidget(object):
    # TODO: logging
    # TODO: can the remote specific events find a disconnected usb cable?
    # TODO: thread
    devserial = 0
    IP = "0.0.0.0"
    port = 0

    attach = []
    detach = []
    error = []
    input = {}
    output = {}
    sensor = {}

    callback = {"attach": attach,
                'detach': detach,
                'error': error}


    def __init__(self, **kwargs):
        log.debug("Acquiring InterfaceKit")
        self.ik = InterfaceKit()
        log.debug("Registering Handlers")
        self.ik.setOnAttachHandler(self._onAttach)
        self.ik.setOnDetachHandler(self._onDetach)
        self.ik.setOnErrorhandler(self._onError)
        self.ik.setOnOutputChangeHandler(self._onOutput)
        self.ik.setOnInputChangeHandler(self._onInput)
        self.ik.setOnSensorChangeHandler(self._onSensor)

    def start(self):
        log.debug("Opening remote IP")
        self.ik.openRemoteIP(self.IP, self.port, self.devserial)

    def close(self):
        self.ik.closePhidget()

    def add_callback(self, cb, type):
        self.callback[type].append(cb)

    def _onAttach(self, event):
        for cb in callback['attach']:
            cb(event)
        for dev in input:
            dev.callback['attach'](event)
        for dev in output:
            dev.callback['attach'](event)
        for dev in sensor:
            dev.callback['attach'](event)

    def _onDetach(self, event):
        for cb in callback['detach']:
            cb(event)
        for dev in input:
            dev.callback['detach'](event)
        for dev in output:
            dev.callback['detach'](event)
        for dev in sensor:
            dev.callback['detach'](event)

    def _onError(self, event):
        if self.ik.isAttached():
            for cb in callback['error']:
                cb(event)
            for dev in input:
                dev.callback['error'](event)
            for dev in output:
                dev.callback['error'](event)
            for dev in sensor:
                dev.callback['error'](event)

    def _onOutput(self, event):
        self.output(event)
        for cb in output[event.index]['value']:
            cb(event)

    def _onInput(self, event):
        self.input(event)
        for cb in output[event.index]['value']:
            cb(event)

    def _onSensor(self, event):
        self.sense(event)
        for cb in output[event.index]['value']:
            cb(event)


    # TODO: __str__ returns devserial?

class Sensor(object):
    isRatiometric = None
    unit = ""
    callback = {"attach": [],
                 'detach': [],
                 'value': []}

    def __init__(self, name, index):
        self.name = name
        self.index = index

    def convert(self, sample):
        return sample

    def add_callback(self, cb, type):
        self.callback[type].append(cb)

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

class Relay(Sensor):
    def convert(self, sample):
        return "Open" if sample else "Closed"

class CorePhidget(LTCPhidget):
    # Interface Kit 8/8/8 with sensors attached
    devserial = 178346
    IP = LTCIP
    port = 5001

    shorepower = Relay('Shore Power Relay', 7)

    inputWindspeed = 7  # make a sensor?
    output = {}
    output[7] = shorepower
    sensor = {}
    sensor[0] = TemperatureSensor("Internal Temperature", 0)
    sensor[1] = VoltageSensor("Ignition Battery", 1)
    sensor[2] = Sensor("Humidity", 3)
    sensor[3] = TemperatureSensor("External Temperature", 4)
    sensor[4] = VoltageSensor("Rocket Ready", 2)
    sensor[5] = VoltageSensor("System Battery", 5)
    sensor[6] = VoltageSensor("Solar Voltage", 6)
    sensor[7] = VoltageSensor("Shore Power", 7)

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
        self.ik.setOutputState(self.shorepower.index, state)

class IgnitionRelay(LTCPhidget):
    # Interface Kit 0/0/4 with relays
    devserial = 259173
    IP = LTCIP
    port = 5001
    relay = Relay('Ignition Relay', 0)

    def _onOutput(self, event):
        if event.index == self.relay.index:
            self.output(event)

    def toggleIgnitionRelayState(self, event):
        if self.ik.isAttached():
            state = self.ik.getOutputState(self.relay.index)
            self.setIgnitionRelayState(not state)

    def setIgnitionRelayState(self, state):
        self.ik.setOutputState(self.relay.index, state)

class LTCbackend(object):

    def __init__(self):
        log.info("Starting Backend")
        self.relay = IgnitionRelay()
        self.relay.add_callback(self.attach, "attach")

        self.core = CorePhidget()
        self.core.add_callback(self.attach, "attach")
        self.core.shorepower.add_callback(self.output, 'value')

    def start(self, event):
        self.relay.start()
        self.core.start()

    def attach(self, event):
        self.ignite(False)

    def output(self, event):
        if event.index == self.core.shorepower.index:
            self.shorepower_state = event.state


    def close(self, event):
        log.debug("Closing LTCBackend")
        try:
            self.ignite(False)
        except PhidgetException:
            log.info("Unable to turn off ignite on quit")
        self.relay.close()
        self.core.close()

    def ignite(self, state):
        if state is False:
            self.relay.setIgnitionRelayState(False)
        elif self.shorepower_state is False and state is True:
            self.relay.setIgnitionRelayState(True)
        else:
            raise PhidgetException(1)  # TODO: more descriptive errno?

    def shorepower(self, state):
        self.core.set24vState(state)
