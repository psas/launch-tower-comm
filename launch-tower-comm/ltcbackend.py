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
    def __init__(self, name, index):
        self.name = name
        self.index = index

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

class Relay(Sensor):
    def convert(self, sample):
        return "Open" if sample else "Closed"

class CorePhidget(LTCPhidget):
    # Interface Kit 8/8/8 with sensors attached
    devserial = 178346
    IP = "192.168.128.250"
    port = 5001

    shorepower = Relay('Shore Power Relay', 1)
    inputWindspeed = 7  # make a sensor?

    sensor = dict()
    sensor[0] = TemperatureSensor("Internal Temperature", 0)
    sensor[1] = VoltageSensor("Ignition Battery", 1)
    sensor[2] = Sensor("Humidity", 2)
    sensor[3] = TemperatureSensor("External Temperature", 3)
    sensor[4] = Sensor("Unused", 4)
    sensor[5] = VoltageSensor("System Battery", 5)
    sensor[6] = VoltageSensor("Internal 5v", 6)
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
    IP = "192.168.128.250"
    port = 5001
    relay = Relay('Ignition Relay', 1)

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
        self.central_dict[str(self.relay.devserial) + " InterfaceKit"] = False
        self.central_dict[str(self.core.devserial) + " InterfaceKit"] = False

    def attach(self, event):
        self.ignite(False)
        attached = event.device
        ik = "{} InterfaceKit".format(attached.getSerialNum())
        log.info(ik + " Attached")
        self.central_dict[ik] = "True"

    def detach(self, event):
        attached = event.device
        ik = "{} InterfaceKit".format(attached.getSerialNum())
        log.info(ik + " Detached")
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
        self.ignite(False)
        self.relay.close()
        self.core.close()

    def ignite(self, state):
        # TODO: cross check with shorepower
        self.relay.setIgnitionRelayState(state)

    def shorepower(self, state):
        self.core.set24vState(state)
