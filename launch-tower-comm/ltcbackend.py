from ctypes import *
from datetime import datetime
import sys
import time
import ltclogger as log

# Phidgets specific imports
from Phidgets.PhidgetException import PhidgetException
from Phidgets.Devices.InterfaceKit import InterfaceKit

########### Phidgets Setup ########

LTCIP = '192.168.128.2'

class Sensor(object):
    isRatiometric = None
    unit = ""

    def __init__(self, name, index):
        self.callback = {"attach": [],
                         'detach': [],
                         'value': []}
        self.name = name
        self.index = index

    def convert(self, sample):
        return sample

    def add_callback(self, cb, type):
        log.debug("Adding callback to {} sensor".format(self.name))
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
        return "Closed" if sample else "Open"

class LTCPhidget(object):
    # TODO: logging
    # TODO: can the remote specific events find a disconnected usb cable?
    # TODO: thread
    devserial = 0
    IP = "0.0.0.0"
    port = 0

    input = {}
    output = {}
    sensor = {}

    callback = {'attach': [],
                'detach': [],
                'error': [],
                'output': [],
                'input': [],
                'sensor': []}

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
        log.verbose("Opening remote IP")
        self.ik.openRemoteIP(self.IP, self.port, self.devserial)
        log.debug("Remote IP opened")

    def close(self):
        log.verbose("Closing InterfaceKit")
        self.ik.closePhidget()
        log.debug("Interfac kit closed")

    def add_callback(self, cb, type):
        log.debug("Adding a {} type callback".format(type))
        self.callback[type].append(cb)

    def _genericCB(self, event, type):
        log.verbose("{} event received".format(type))
        for cb in self.callback[type]:
            cb(event)
        for dev in self.input.itervalues():
            for cb in dev.callback[type]:
                cb(event)
        for dev in self.output.itervalues():
            for cb in dev.callback[type]:
                cb(event)
        for dev in self.sensor.itervalues():
            for cb in dev.callback[type]:
                cb(event)

    def _onAttach(self, event):
        self._genericCB(event, 'attach')


    def _onDetach(self, event):
        self._genericCB(event, 'detach')

    def _onError(self, event):
        if self.ik.isAttached():
            self._genericCB(event, 'error')
        else:
            log.verbose("Error while detached, likely telling us it's detached")

    def _onOutput(self, event):
        log.verbose("Output event received")
        for cb in self.callback['output']:
            cb(event)
        try:
            for cb in self.output[event.index].callback['value']:
                cb(event)
        except KeyError:
            pass

    def _onInput(self, event):
        log.verbose("Input event received")
        for cb in self.callback['input']:
            cb(event)
        try:
            for cb in self.input[event.index].callback['value']:
                cb(event)
        except KeyError:
            pass

    def _onSensor(self, event):
        log.verbose("Sensor event received")
        for cb in self.callback['sensor']:
            cb(event)
        try:
            for cb in self.sensor[event.index].callback['value']:
                cb(event)
        except KeyError:
            pass

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
        super(CorePhidget, self)._onAttach(event)

    def _onSensor(self, event):
        module = self.sensor[event.index]
        if module.isRatiometric:
            self.ik.setRatiometric(True)
            event.value = self.ik.getSensorValue(event.index)
            self.ik.setRatiometric(False)
        super(CorePhidget, self)._onSensor(event)

    def set24vState(self, state):
        log.info("Setting shorepower state to {}".format(state))
        self.ik.setOutputState(self.shorepower.index, state)

class IgnitionRelay(LTCPhidget):
    # Interface Kit 0/0/4 with relays
    devserial = 259173
    IP = LTCIP
    port = 5001
    relay = Relay('Ignition Relay', 0)
    output = {}
    output[0] = relay

    def _onOutput(self, event):
        if event.index == self.relay.index:
            super(IgnitionRelay, self)._onOutput(event)

    def toggleIgnitionRelayState(self, event):
        if self.ik.isAttached():
            state = self.ik.getOutputState(self.relay.index)
            self.setIgnitionRelayState(not state)

    def setIgnitionRelayState(self, state):
        log.info("Setting ignition relay state to {}".format(state))
        self.ik.setOutputState(self.relay.index, state)

class LTCbackend(object):

    def __init__(self, set_status):
        log.info("Starting Backend")
        self.relay = IgnitionRelay()
        self.relay.add_callback(self.attach, "attach")

        self.core = CorePhidget()
        self.core.add_callback(self.attach, "attach")
        self.core.shorepower.add_callback(self.output, 'value')

        self.set_status = set_status

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
        try:
            if state is False:
                self.relay.setIgnitionRelayState(False)
            elif state is True:
                if self.shorepower_state is False:
                    self.relay.setIgnitionRelayState(True)
                else:
                    raise PhidgetException(1)  # TODO: more descriptive errno?
            else:
                raise TypeError
        except PhidgetException:
            self.set_status("Phidget Call Failed")
            raise


    def shorepower(self, state):
        try:
            self.core.set24vState(state)
            self.set_status("Nominal")
        except PhidgetException:
            self.set_status("Phidget Call Failed")
            raise
