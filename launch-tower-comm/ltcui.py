from dataclasses import dataclass
from enum import Enum, unique

import ltclogger as log
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from ltcbackend import Relay
from Phidget22.Phidget import Phidget

# TODO: Color Enum
RED = (1, 0, 0, 1)
GREEN = (0, 1, 0, 1)
WHITE = (1, 1, 1, 1)
GRAY = (0.7, 0.7, 0.7, 1)


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
        DETACHED = "Detached", (0.1, 0.1, 0.1, 1)
        THINKING = "Thinking", (0, 1, 1, 1)
        OK = "", (1, 1, 1, 1)
        ON = "On", (1, 0, 0, 1)
        OFF = "Off", (0, 1, 0.5, 1)
        ERROR = "Error", (1, 1, 0, 1)
        UNKNOWN = "Unknown", (0, 0, 0, 1)

    # TODO: ref Error, on click pop up detailed description
    background_color = ListProperty((1, 1, 1, 1))

    def __init__(self, **kwargs):
        # load from kv lang file first
        super().__init__(**kwargs)
        self.color = WHITE  # Set font color to white
        self.set_state(self.State.DETACHED)

    def set_state(self, state: State, text: str = ''):
        match state:
            case self.State.THINKING:
                self.text = ""

            case _:
                if len(text) > 0:
                    self.text = text
                else:
                    self.text = state.text

    def on_attach(self):
        self.set_state(self.State.THINKING)

    def on_detach(self):
        self.set_state(self.State.DETACHED)

    def on_error(self, _errno: int):
        self.set_state(self.State.ERROR)

    def on_button(self):
        self.set_state(self.State.THINKING)


class InterfaceKitPanel(BoxLayout):
    '''Container for IOIndicators. Loaded from kv lang file.'''


class IOIndicator(BoxLayout):
    def __init__(self, sensor: Phidget, **kwargs):
        '''Indicator widget. Includes a name label, and status label.'''
        super().__init__(**kwargs)

        self.nominal_value = sensor.nominal_value
        self.name = sensor.name
        self.unit = sensor.unit
        self.device_label.text = sensor.name

        sensor.add_callback(self.on_attach, 'attach')
        sensor.add_callback(self.on_detach, 'detach')
        sensor.add_callback(self.on_value, 'value')

    def on_attach(self):
        self.ltc_label.background_color = GRAY
        self.ltc_label.set_state(LTCLabel.State.UNKNOWN)

    def on_detach(self):
        self.ltc_label.set_state(LTCLabel.State.DETACHED)


class VoltageSensorIndicator(IOIndicator):
    def __init__(self, sensor: Phidget, **kwargs):
        super().__init__(sensor, **kwargs)

    def on_value(self, sensor_reading: float):
        if isinstance(sensor_reading, float):
            self.ltc_label.set_state(LTCLabel.State.OK)
            self.ltc_label.text = f"{sensor_reading:.1f} {self.unit}"
            self.ltc_label.background_color = GREEN if self.nominal_value(sensor_reading) else RED
        else:
            log.error(
                f"Unsupported type passed to {self.name} value callback: {type(sensor_reading)}"
            )


class RelayIndicator(IOIndicator):
    def __init__(self, sensor: Phidget, **kwargs):
        super().__init__(sensor, **kwargs)
        self.sensor = sensor

    def on_value(self, sensor_reading: Relay.State):
        if self.sensor.getAttached():
            self.ltc_label.text = sensor_reading.name
            self.ltc_label.background_color = (
                GREEN if self.nominal_value(val=sensor_reading.value) else RED
            )
        else:
            log.error("Could not set label state: device not attached")


class RocketReadyIndicator(IOIndicator):
    def __init__(self, sensor: Phidget, **kwargs):
        super().__init__(sensor, **kwargs)

    def on_value(self, sensor_reading: float):
        if isinstance(sensor_reading, float):
            self.ltc_label.text = "Yes" if sensor_reading >= 2.0 else "No"
            self.ltc_label.background_color = GREEN if self.nominal_value(sensor_reading) else RED
        else:
            log.error(
                f"Unsupported type passed to {self.name} value callback: {type(sensor_reading)}"
            )


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
        NOMINAL = "Nominal", "Shore power must be off to arm", (0.5, 0.5, 0.5, 1)
        ARMED = (
            "Armed",
            "Press abort to disarm and return to unarmed tab",
            (1, 0, 0, 1),
        )
        DISARMED = "Disarmed", "The igniter is now off and safe", (0.5, 0.5, 0.5, 1)
        IGNITED = (
            "Ignited",
            "Click Ignite again to disable Ignition power",
            (0, 1, 0.5, 1),
        )
        ERROR = (
            "Error",
            "An error occurred, \nPlease try again",
            (1, 0, 0, 1),
        )
        DISCONNECTED = (
            "Disconnected",
            "Please leave a message or call again.",
            (1, 1, 0, 1),
        )
        ABORT_FAILED = (
            "Abort Failed",
            "The attempt to shut off the igniter failed.",
            (1, 0, 0, 1),
        )

    # TODO: scrollable log

    def __init__(self, **kwargs):
        # load from the kv lang file
        super().__init__(**kwargs)
        self.set_state(self.State.DISCONNECTED)

    def on_attach(self):
        self.set_state(self.State.NOMINAL)

    def on_detach(self):
        self.set_state(self.State.DISCONNECTED)

    def on_error(self, errno: int):
        match errno:
            case 4103:
                log.error("Sensor value out of range")
            case _:
                self.set_state(self.State.ERROR)

    def on_value(self, _value):
        self.set_state(self.State.NOMINAL)

    def set_state(self, state: State, *args):
        log.info(f"Setting StatusDisplay state to {state}")
        self.state_info.text = state.title
        self.state_info.color = state.color
        if args:
            self.state_message.text = args[0].message
        else:
            self.state_message.text = state.message
