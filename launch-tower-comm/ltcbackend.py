from enum import Enum, unique
from typing import Callable

# Phidgets specific imports
from Phidget22.Devices.DigitalOutput import DigitalOutput
from Phidget22.Devices.VoltageInput import VoltageInput, VoltageSensorType
from Phidget22.Devices.VoltageRatioInput import (
    VoltageRatioInput,
    VoltageRatioSensorType,
)
from Phidget22.Net import Net
from Phidget22.Phidget import Phidget
from Phidget22.PhidgetException import PhidgetException

import ltclogger as log

########### Phidgets Setup ########


class LTCPhidget(Phidget):
    def __init__(self):
        super().__init__()
        # TODO: can the remote specific events find a disconnected usb cable?
        self._callback = {
            'attach': [],
            'detach': [],
            'error': [],
            'property': [],
        }

        self.setOnAttachHandler(self._on_attach)
        self.setOnDetachHandler(self._on_detach)
        self.setOnErrorHandler(self._on_error)
        self.setOnPropertyChangeHandler(self._on_property)

    def add_callback(self, cb: Callable, event_type: str):
        log.debug(f"Adding callback to {self.name}")
        self._callback[event_type].append(cb)

    def _on_attach(self, *args, **kwargs):
        log.verbose("attach event received")
        for cb in self._callback['attach']:
            cb()

    def _on_detach(self, *args, **kwargs):
        log.verbose("detach event received")
        for cb in self._callback['detach']:
            cb()

    def _on_error(self, _device: Phidget, code: int, description: str, *args, **kwargs):
        log.error(f"error code {code} received: {description}")
        for cb in self._callback['error']:
            cb(code)

    def _on_property(self, name: str, *args, **kwargs):
        log.verbose(f"property {name} changed")
        try:
            for cb in self._callback['value']:
                cb(name)
        except TypeError as e:
            log.error(f"Error executing callback for {self.name}: {e}")


class Relay(LTCPhidget, DigitalOutput):
    def __init__(self, name: str, devserial: int, channel: int, *, invert: bool = False):
        super().__init__()
        self._callback['value'] = []
        self.setDeviceSerialNumber(devserial)
        self.setChannel(channel)

        self._callback['value'] = self._callback['property']

        self.unit = ''
        self.name = name
        self.invert = invert  # invert == True ? Nominal closed : Nominal open
        self.channel = channel

    @unique
    class State(Enum):
        ON = True
        OFF = False

    def setState(self, state: State):  # noqa: N802
        log.info(f"Setting {self.name} to {state}")

        for cb in self._callback['value']:
            cb(state)

        super().setState(state.value)

    def nominal_value(self, val: bool):
        return val != self.invert


class TemperatureSensor(LTCPhidget, VoltageRatioInput):
    def __init__(self, name: str, devserial: int, channel: int, upper: float, lower: float):
        super().__init__()
        self._callback['value'] = []
        self.setOnSensorChangeHandler(self._on_voltage)
        self.setDeviceSerialNumber(devserial)
        self.setChannel(channel)

        self.unit = "C"
        self.name = name
        self.upper = upper
        self.lower = lower

        # Set the sensor type after attaching only
        self.add_callback(self.set_type, 'attach')

    def _on_voltage(self, _device: Phidget, ratio: float, *args, **kwargs):
        try:
            read = self.getSensorValue()
        except PhidgetException as e:
            log.error(f"Could not read {self.name}: {e}")

        for cb in self._callback['value']:
            cb(read)

    def nominal_value(self, val: float):
        return self.lower < val < self.upper

    def set_type(self):
        try:
            self.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1124)
        except PhidgetException as e:
            log.error(f"Error setting sensor type for {self.name}: {e}")


class VoltageSensor(LTCPhidget, VoltageInput):
    def __init__(self, name: str, devserial: int, channel: int, upper: float, lower: float):
        super().__init__()
        self.setDeviceSerialNumber(devserial)
        self.setChannel(channel)
        self._callback['value'] = []

        self.setOnSensorChangeHandler(self._on_voltage)

        self.unit = "V"
        self.name = name
        self.upper = upper
        self.lower = lower

        self.add_callback(self.set_type, 'attach')

    def _on_voltage(self, *args, **kwargs):
        read = self.getSensorValue()
        for cb in self._callback['value']:
            cb(read)

    def nominal_value(self, val: float):
        return self.lower < val < self.upper

    def set_type(self):
        self.setSensorType(VoltageSensorType.SENSOR_TYPE_1135)


class LTCError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class LTCbackend:
    def __init__(self):
        log.info("Starting Backend")
        # Interface Kit 0/0/4 with relays - 1014
        self.ignition = Relay('Ignition Relay', devserial=259173, channel=0)
        self.ignition.add_callback(self.attach, 'attach')
        self.shore = Relay('Shorepower Relay', devserial=259173, channel=3, invert=True)

        # Interface Kit 8/8/8 with sensors attached - 1018
        # Here, sensor[n] describes the nth sensor on the Interface Kit (IK),
        # following the Phidget convention. If sensor positions on the IK are
        # changed, the 'sensor' dictionary keys must be properly updated here.
        self.inputWindspeed = 7  # make a sensor?

        self.sensors = [
            TemperatureSensor("Internal Temperature", 178346, 0, 40.0, 10.0),
            VoltageSensor("Ignition Battery", 178346, 1, 4.1 * 4, 3.6 * 4),
            VoltageSensor("Rocket Ready", 178346, 2, 5.0, 1.5),
            VoltageSensor("System Battery", 178346, 5, 15.0, 11.0),
            VoltageSensor("Solar Voltage", 178346, 6, 25.0, 11.0),
            VoltageSensor("Shore Power", 178346, 7, 20.0, 18.0),
        ]

    def start(self, *args, **kwargs):
        # Net.addServer('ltc', 'ltc.psas.lan', 5001, '', 0)
        Net.addServer('ltc', '10.0.0.1', 5661, '', 0)
        self.ignition.open()
        self.shore.open()
        for sensor in self.sensors:
            sensor.open()

    def attach(self):
        # TODO: Handle Possible Error
        self.ignite(Relay.State.OFF)

    def close(self, *args, **kwargs):
        log.debug("Closing LTCBackend")
        try:
            self.ignite(Relay.State.OFF)
        except PhidgetException:
            log.info("Unable to turn off ignite on quit")
        self.ignition.close()
        self.shore.close()
        for sensor in self.sensors:
            sensor.close()

    def ignite(self, state: Relay.State):
        match state:
            case Relay.State.ON:
                if not self.shore.getState():
                    self.ignition.setState(state)
                else:
                    raise LTCError("Can't ignite with shorepower on")

            case Relay.State.OFF:
                self.ignition.setState(state)

    def shorepower(self, state: Relay.State):
        try:
            self.shore.setState(state)
        except PhidgetException as e:
            log.error(f"{e}")


# Relays 1014-2
# Voltage 1135-0 x5
# Temp 1124-0
# missing external temp/himid?
