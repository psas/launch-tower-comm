from collections.abc import Callable
from enum import Enum, unique
from typing import Any, Self, override

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


class CallbackFanout[V]:
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        # detach fires both on network disconnect and USB cable disconnect.
        # attach fires on open() and USB cable connect but not network reattach?
        self._callback: dict[str, list[Callable[..., None]]] = {
            'attach': [],
            'detach': [],
            'error': [],
            'property': [],
            'value': [],
        }
        if isinstance(self, Phidget):
            self.setOnAttachHandler(lambda _: self._on_attach())
            self.setOnDetachHandler(lambda _: self._on_detach())
            self.setOnErrorHandler(lambda _, code, desc: self._on_error(code, desc))

            def on_property(self: Self, device: Phidget, name: str) -> None:
                # Why the callback can't just give us the value I'll never know. Here
                # we reconstruct the getter method for the associated property and then
                # get that propterty. Its TOCTOU but I am unaware of a better way.
                value = getattr(device, 'get' + name)()
                self._on_property(name, value)

            self.setOnPropertyChangeHandler(on_property)
            if hasattr(self, "setOnSensorChangeHandler"):
                self.setOnSensorChangeHandler(lambda _d, v, _u: self._on_value(v))

    def add_callback(self, cb: Callable[..., None], event_type: str) -> None:
        cbname = cb.__name__
        if hasattr(cb, "__self__"):
            cbname = f"{cb.__self__.__class__.__name__}.{cb.__name__}"
        log.debug(f"Adding {event_type:6} callback to {self.name}: {cbname}")
        self._callback[event_type].append(cb)

    def _on_attach(self) -> None:
        log.verbose(f"{self.name} Attached")
        for cb in self._callback['attach']:
            cb()

    def _on_detach(self) -> None:
        log.verbose(f"{self.name} Detached")
        for cb in self._callback['detach']:
            cb()

    def _on_error(self, code: int, description: str) -> None:
        log.error(f"{self.name} error {code}: {description}")
        for cb in self._callback['error']:
            cb(code)

    def _on_property(self, name: str, value: Any) -> None:
        log.verbose(f"{self.name} property {name} -> {value}")
        for cb in self._callback['property']:
            cb(name, value)

    def _on_value(self, val: V) -> None:
        for cb in self._callback['value']:
            cb(val)

    def is_nominal(self, _val: V) -> bool:
        return False


class Relay(CallbackFanout['Relay.State'], DigitalOutput):
    def __init__(self, name: str, devserial: int, channel: int, *, invert: bool = False) -> None:
        super().__init__(name)
        self.setDeviceSerialNumber(devserial)
        self.setChannel(channel)

        self.unit = ''
        # invert == True ? Nominal closed : Nominal open
        self.invert = self.State.OFF if invert else self.State.ON
        self.channel = channel

    @unique
    class State(Enum):
        ON = True
        OFF = False

        def __bool__(self) -> bool:
            return self.value

    @override
    def _on_attach(self) -> None:
        state = self.State(self.getState())
        super()._on_attach()
        self._on_value(state)

    @override
    def setState(self, state: State) -> None:
        log.info(f"Setting {self.name} to {state}")
        super().setState(state.value)
        self._on_value(state)

    @override
    def is_nominal(self, val: State) -> bool:
        return val != self.invert


class TemperatureSensor(CallbackFanout[float], VoltageRatioInput):
    def __init__(self, name: str, devserial: int, channel: int, upper: float, lower: float) -> None:
        super().__init__(name)
        self.setDeviceSerialNumber(devserial)
        self.setChannel(channel)

        self.unit = "C"
        self.upper = upper
        self.lower = lower

    @override
    def _on_attach(self) -> None:
        self.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1124)
        super()._on_attach()

    @override
    def is_nominal(self, val: float) -> bool:
        return self.lower < val < self.upper


class VoltageSensor(CallbackFanout[float], VoltageInput):
    def __init__(self, name: str, devserial: int, channel: int, upper: float, lower: float) -> None:
        super().__init__(name)
        self.setDeviceSerialNumber(devserial)
        self.setChannel(channel)

        self.unit = "V"
        self.upper = upper
        self.lower = lower

    @override
    def _on_attach(self) -> None:
        self.setSensorType(VoltageSensorType.SENSOR_TYPE_1135)
        super()._on_attach()

    @override
    def is_nominal(self, val: float) -> bool:
        return self.lower < val < self.upper


class LTCError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class LTCbackend:
    def __init__(self) -> None:
        log.info("Starting Backend")
        # Interface Kit 0/0/4 with relays - 1014
        self.ignition: Relay | MockRelay = Relay(
            'Ignition Relay', devserial=259173, channel=0, invert=True
        )
        self.ignition.add_callback(self._on_attach, 'attach')
        self.shore: Relay | MockRelay = Relay(
            'Shorepower Relay', devserial=259173, channel=3, invert=True
        )

        # Interface Kit 8/8/8 with sensors attached - 1018
        self.sensors: list[Phidget] = [
            TemperatureSensor("Internal Temperature", 178346, 0, 40.0, 10.0),
            VoltageSensor("Ignition Battery", 178346, 1, 4.1 * 4, 3.6 * 4),
            VoltageSensor("Rocket Ready", 178346, 2, 5.0, 2.0),
            VoltageSensor("System Battery", 178346, 5, 15.0, 11.0),
            VoltageSensor("Solar Voltage", 178346, 6, 25.0, 11.0),
            VoltageSensor("Shore Power", 178346, 7, 20.0, 18.0),
        ]

    def start(self) -> None:
        # Net.addServer('ltc', 'ltc.psas.lan', 5001, '', 0)
        Net.addServer('ltc', '10.0.0.1', 5661, '', 0)
        # async open - wait for associated on_attach callback to fire before using devices
        self.ignition.open()
        self.shore.open()
        for sensor in self.sensors:
            sensor.open()

    def _on_attach(self) -> None:
        # TODO: Handle Possible Error
        # FIXME: phidget failsafe mode?
        self.ignite(Relay.State.OFF)

    def close(self) -> None:
        log.debug("Closing LTCBackend")
        try:
            self.ignite(Relay.State.OFF)
        except PhidgetException as e:
            log.critical(f"Unable to turn off ignite on quit: {e}")
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
        self.shore.setState(state)


class MockRelay(CallbackFanout['Relay.State']):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._state = Relay.State.OFF

    def open(self) -> None:
        self._on_attach()
        self._on_value(self._state)

    def close(self) -> None:
        self._on_detach()

    def getState(self) -> Relay.State:  # noqa: N802
        return self._state

    def setState(self, state: Relay.State) -> None:  # noqa: N802
        self._state = state
        self._on_value(state)

    def is_nominal(self, _val: Any) -> bool:
        return False


class MockSensor(CallbackFanout[float]):
    def __init__(self, name: str, value: float, unit: str) -> None:
        super().__init__(name)
        self._value = value
        self.unit = unit

    def open(self) -> None:
        self._on_attach()
        self._on_value(self._value)

    def close(self) -> None:
        self._on_detach()


class MockBackend(LTCbackend):
    def __init__(self) -> None:
        self.shore = MockRelay('Shore')
        self.ignition = MockRelay('Ignition')
        self.sensors: list[Phidget] = [
            MockSensor("Internal Temperature", 25.0, "C"),
            MockSensor("Ignition Battery", 19.0, "V"),
            MockSensor("Rocket Ready", 2.0, "V"),
            MockSensor("System Battery", 13.0, "V"),
            MockSensor("Solar Voltage", 14.0, "V"),
            MockSensor("Shore Power", 17.0, "V"),
        ]

    @override
    def start(self) -> None:
        self.shore.open()
        self.ignition.open()
        for sensor in self.sensors:
            sensor.open()
