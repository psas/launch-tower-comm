from collections.abc import Callable
from enum import Enum, unique
from typing import Any, override

import ltclogger as log

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


class LTCPhidget(Phidget):
    def __init__(self) -> None:
        super().__init__()
        # detach fires both on network disconnect and USB cable disconnect.
        # attach fires on open() and USB cable connect but not network reattach?
        self._callback: dict[str, list[Callable[..., None]]] = {
            'attach': [],
            'detach': [],
            'error': [],
            'property': [],
        }

        self.setOnAttachHandler(self._on_attach)
        self.setOnDetachHandler(self._on_detach)
        self.setOnErrorHandler(self._on_error)
        self.setOnPropertyChangeHandler(self._on_property)

    def add_callback(self, cb: Callable[..., None], event_type: str) -> None:
        log.debug(f"Adding callback to {self.name}")
        self._callback[event_type].append(cb)

    def _on_attach(self, _device: Phidget) -> None:
        log.verbose(f"{self.name} Attached")
        for cb in self._callback['attach']:
            cb()

    def _on_detach(self, _device: Phidget) -> None:
        log.verbose(f"{self.name} Detached")
        for cb in self._callback['detach']:
            cb()

    def _on_error(self, _device: Phidget, code: int, description: str) -> None:
        log.error(f"{self.name} error {code}: {description}")
        for cb in self._callback['error']:
            cb(code)

    def _on_property(self, _device: Phidget, name: str) -> None:
        # Why the callback can't just give us the value I'll never know. Here
        # we reconstruct the getter method for the associated property and then
        # get that propterty. Its TOCTOU but I am unaware of a better way.
        value = getattr(self, 'get' + name)()
        log.verbose(f"{self.name} property {name} -> {value}")
        for cb in self._callback['property']:
            cb(name, value)

    def is_nominal(self, _val: Any) -> bool:
        return False


class Relay(LTCPhidget, DigitalOutput):
    def __init__(self, name: str, devserial: int, channel: int, *, invert: bool = False) -> None:
        super().__init__()
        self._callback['value'] = []
        self.setDeviceSerialNumber(devserial)
        self.setChannel(channel)

        self.unit = ''
        self.name = name
        self.invert = invert  # invert == True ? Nominal closed : Nominal open
        self.channel = channel

    @unique
    class State(Enum):
        ON = True
        OFF = False

    def _on_value(self, val: State) -> None:
        for cb in self._callback['value']:
            cb(val)

    @override
    def _on_attach(self, device: Phidget) -> None:
        super()._on_attach(device)
        state = self.getState()
        self._on_value(self.State(state))

    @override
    def setState(self, state: State) -> None:
        log.info(f"Setting {self.name} to {state}")
        super().setState(state.value)
        self._on_value(state)

    @override
    def is_nominal(self, val: State) -> bool:
        return val != self.invert


class TemperatureSensor(LTCPhidget, VoltageRatioInput):
    def __init__(self, name: str, devserial: int, channel: int, upper: float, lower: float) -> None:
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
        self.add_callback(self._set_type, 'attach')

    def _on_voltage(self, _device: Phidget, ratio: float, _unit: str) -> None:
        for cb in self._callback['value']:
            cb(ratio)

    @override
    def is_nominal(self, val: float) -> bool:
        return self.lower < val < self.upper

    def _set_type(self) -> None:
        try:
            self.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1124)
        except PhidgetException as e:
            log.error(f"Error setting sensor type for {self.name}: {e}")
            raise


class VoltageSensor(LTCPhidget, VoltageInput):
    def __init__(self, name: str, devserial: int, channel: int, upper: float, lower: float) -> None:
        super().__init__()
        self.setDeviceSerialNumber(devserial)
        self.setChannel(channel)
        self._callback['value'] = []

        self.setOnSensorChangeHandler(self._on_voltage)

        self.unit = "V"
        self.name = name
        self.upper = upper
        self.lower = lower

        self.add_callback(self._set_type, 'attach')

    def _on_voltage(self, _device: Phidget, value: float, _unit: str) -> None:
        for cb in self._callback['value']:
            cb(value)

    @override
    def is_nominal(self, val: float) -> bool:
        return self.lower < val < self.upper

    def _set_type(self) -> None:
        self.setSensorType(VoltageSensorType.SENSOR_TYPE_1135)


class LTCError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class LTCbackend:
    def __init__(self) -> None:
        log.info("Starting Backend")
        # Interface Kit 0/0/4 with relays - 1014
        self.ignition = Relay('Ignition Relay', devserial=259173, channel=0)
        self.ignition.add_callback(self._on_attach, 'attach')
        self.shore = Relay('Shorepower Relay', devserial=259173, channel=3, invert=True)

        # Interface Kit 8/8/8 with sensors attached - 1018
        self.sensors = [
            TemperatureSensor("Internal Temperature", 178346, 0, 40.0, 10.0),
            VoltageSensor("Ignition Battery", 178346, 1, 4.1 * 4, 3.6 * 4),
            VoltageSensor("Rocket Ready", 178346, 2, 5.0, 1.5),
            VoltageSensor("System Battery", 178346, 5, 15.0, 11.0),
            VoltageSensor("Solar Voltage", 178346, 6, 25.0, 11.0),
            VoltageSensor("Shore Power", 178346, 7, 20.0, 18.0),
        ]

    def start(self) -> None:
        # Net.addServer('ltc', 'ltc.psas.lan', 5001, '', 0)
        Net.addServer('ltc', '10.0.0.1', 5661, '', 0)
        self.ignition.open()
        self.shore.open()
        for sensor in self.sensors:
            sensor.open()

    def _on_attach(self) -> None:
        # TODO: Handle Possible Error
        self.ignite(Relay.State.OFF)

    def close(self) -> None:
        log.debug("Closing LTCBackend")
        try:
            self.ignite(Relay.State.OFF)
        except PhidgetException:
            log.info("Unable to turn off ignite on quit")
        self.ignition.close()
        self.shore.close()
        for sensor in self.sensors:
            sensor.close()

    def ignite(self, state: Relay.State) -> None:
        match state:
            case Relay.State.ON:
                if not self.shore.getState():
                    self.ignition.setState(state)
                else:
                    raise LTCError("Can't ignite with shorepower on")

            case Relay.State.OFF:
                self.ignition.setState(state)

    def shorepower(self, state: Relay.State) -> None:
        try:
            self.shore.setState(state)
        except PhidgetException as e:
            log.error(f"{e}")
