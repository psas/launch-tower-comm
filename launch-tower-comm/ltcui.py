from dataclasses import dataclass
from enum import Enum, unique
from typing import Any

import ltclogger as log
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from ltcbackend import Relay
from Phidget22.Phidget import Phidget

# TODO: Color Enum
RED = (1, 0, 0, 1)
GREEN = (0, 1, 0, 1)
SPRING_GREEN = (0, 1, 0.5, 1)
WHITE = (1, 1, 1, 1)
LIGHT_GRAY = (0.7, 0.7, 0.7, 1)
GRAY = (0.5, 0.5, 0.5, 1)
DARK_GRAY = (0.1, 0.1, 0.1, 1)
CYAN = (0, 1, 1, 1)
YELLOW = (1, 1, 0, 1)
BLACK = (0, 0, 0, 1)


class LTCLabel(Label):
    '''A display widget for the Phidget Devices in the launch tower computer.

    Loads from the kv lang file. Used by ltcbackend sensors.
    '''

    @dataclass(frozen=True)
    class StateField:
        text: str
        color: tuple[float, float, float, float]

    @unique
    class State(StateField, Enum):
        DETACHED = "Detached", DARK_GRAY
        THINKING = "", CYAN
        OK = "", WHITE
        ON = "On", RED
        OFF = "Off", SPRING_GREEN
        ERROR = "Error", YELLOW
        UNKNOWN = "Unknown", BLACK

    # TODO: ref Error, on click pop up detailed description
    background_color = ListProperty(WHITE)

    def __init__(self, **kwargs: object) -> None:
        # load from kv lang file first. Values in the kv will be applied after this method though.
        super().__init__(**kwargs)
        self.color = WHITE  # Set font color to white
        self.set_state(self.State.UNKNOWN)

    def set_state(self, state: State, text: str = '') -> None:
        self.background_color = state.color
        self.text = text if text else state.text

    def on_button(self) -> None:
        # FIXME: Use for something?
        self.set_state(self.State.THINKING)


class InterfaceKitPanel(BoxLayout):
    '''Container for IOIndicators. Loaded from kv lang file.'''


class IOIndicator(BoxLayout):
    def __init__(self, sensor: Phidget, **kwargs: object) -> None:
        '''Indicator widget. Includes a name label, and status label.'''
        super().__init__(**kwargs)

        self.sensor = sensor
        self.device_label.text = sensor.name

        sensor.add_callback(self.on_attach, 'attach')
        sensor.add_callback(self.on_detach, 'detach')
        sensor.add_callback(self.on_error, 'error')
        sensor.add_callback(self.on_value, 'value')

    def on_attach(self) -> None:
        log.debug(f"on_attach {self}")
        self.ltc_label.set_state(LTCLabel.State.THINKING)

    def on_detach(self) -> None:
        log.debug(f"on_detach {self}")
        self.ltc_label.set_state(LTCLabel.State.DETACHED)

    def on_error(self, errno: int) -> None:
        log.debug(f"on_error {errno} {self}")
        self.ltc_label.set_state(LTCLabel.State.ERROR, f"Error {errno}")

    def on_value(self, value: Any) -> None:
        raise NotImplementedError("IOIndicator should only be used through subclases")


class VoltageSensorIndicator(IOIndicator):
    def on_value(self, value: float) -> None:
        if not isinstance(value, float):
            raise TypeError

        state = LTCLabel.State.ON if self.sensor.is_nominal(value) else LTCLabel.State.OFF
        self.ltc_label.set_state(state, f"{value:.1f} {self.sensor.unit}")


class RelayIndicator(IOIndicator):
    def on_value(self, value: Relay.State) -> None:
        if not isinstance(value, Relay.State):
            raise TypeError

        state = LTCLabel.State.ON if self.sensor.is_nominal(value) else LTCLabel.State.OFF
        self.ltc_label.set_state(state, value.name)


class RocketReadyIndicator(IOIndicator):
    def on_value(self, value: float) -> None:
        if not isinstance(value, float):
            raise TypeError

        if self.sensor.is_nominal(value):
            self.ltc_label.set_state(LTCLabel.State.ON, "Yes")
        else:
            self.ltc_label.set_state(LTCLabel.State.OFF, "No")


class StatusDisplay(BoxLayout):
    '''Displays the overall state of the LTC Phidget sensors, and a message.

    Loaded from kv lang file first.
    '''

    @dataclass(frozen=True)
    class StateField:
        title: str
        message: str
        color: tuple[float, float, float, float]

    @unique
    class State(StateField, Enum):
        NOMINAL = "Nominal", "Shore power must be off to arm", GRAY
        ARMED = (
            "Armed",
            "Press abort to disarm and return to unarmed tab",
            RED,
        )
        DISARMED = "Disarmed", "The igniter is now off and safe", GRAY
        IGNITED = (
            "Ignited",
            "Click Ignite again to disable Ignition power",
            SPRING_GREEN,
        )
        ERROR = (
            "Error",
            "An error occurred, \nPlease try again",
            RED,
        )
        DISCONNECTED = (
            "Disconnected",
            "Please leave a message or call again.",
            YELLOW,
        )
        ABORT_FAILED = (
            "Abort Failed",
            "The attempt to shut off the igniter failed.",
            RED,
        )

    # TODO: scrollable log

    def __init__(self, **kwargs: object) -> None:
        # load from the kv lang file
        super().__init__(**kwargs)
        self.set_state(self.State.DISCONNECTED)

    def on_attach(self) -> None:
        self.set_state(self.State.NOMINAL)

    def on_detach(self) -> None:
        self.set_state(self.State.DISCONNECTED)

    def on_error(self, errno: int) -> None:
        match errno:
            case 4103:
                log.error("Sensor value out of range")
            case _:
                self.set_state(self.State.ERROR)

    def on_value(self, _value: object) -> None:
        self.set_state(self.State.NOMINAL)

    def set_state(self, state: State, text: str = '') -> None:
        log.info(f"Setting StatusDisplay state to {state}")
        self.state_info.text = state.title
        self.state_info.color = state.color
        self.state_message.text = text if text else state.message
