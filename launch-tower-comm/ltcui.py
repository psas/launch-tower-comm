from enum import Enum

from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

import ltclogger as log

RED = (1, 0, 0, 1)
GREEN = (0, 1, 0, 1)


class LTCLabel(Label):
    '''A display widget for the Phidget Devices in the launch tower computer.

    Loads from the kv lang file. Used by ltcbackend sensors.
    '''

    class State(Enum):
        DETACHED = [0.1, 0.1, 0.1, 1]
        THINKING = [0, 1, 1, 1]
        ON = [1, 0, 0, 1]
        OFF = [0, 1, 0.5, 1]
        ERROR = [1, 1, 0, 1]
        UNKNOWN = [0.1, 0.1, 0.1, 1]

    # TODO: ref Error, on click pop up detailed description
    background_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        # load from kv lang file first
        super().__init__(**kwargs)
        self.color = [1, 1, 1, 1]  # Set font color to white
        self.set_state(self.State.DETACHED)

    def set_state(self, state: State, text=''):
        match state:
            case self.State.THINKING:
                self.text = ""
            case _:
                if len(text) > 0:
                    self.text = text
                else:
                    self.text = state.name

    def on_attach(self, *args, **kwargs):
        self.set_state(self.State.THINKING)

    def on_detach(self, *args, **kwargs):
        self.set_state(self.State.DETACHED)

    def on_output_changed(self, event):
        if event.state:
            self.set_state(self.State.OFF)
        else:
            self.set_state(self.State.ON)

    def on_error(self, *args, **kwargs):
        self.set_state(self.State.ERROR)

    def on_button(self, *args, **kwargs):
        self.set_state(self.State.THINKING)


class InterfaceKitPanel(BoxLayout):
    '''Container for IOIndicators. Loaded from kv lang file.'''


class IOIndicator(BoxLayout):
    def __init__(self, sensor, **kwargs):
        '''Indicator widget. Includes a name label, and status label.'''
        super().__init__(**kwargs)

        self.nominal_value = sensor.nominal_value
        self.name = sensor.name
        self.unit = sensor.unit
        self.device_label.text = sensor.name

        sensor.add_callback(self.on_attach, 'attach')
        sensor.add_callback(self.on_detach, 'detach')
        sensor.add_callback(self.on_value, 'value')

    def on_attach(self, *args, **kwargs):
        self.ltc_label.set_state(LTCLabel.State.UNKNOWN)

    def on_detach(self, *args, **kwargs):
        self.ltc_label.set_state(LTCLabel.State.DETACHED)


class VoltageSensorIndicator(IOIndicator):
    def __init__(self, sensor, **kwargs):
        super().__init__(sensor, **kwargs)

    def on_value(self, sensor_reading, *args, **kwargs):
        if isinstance(sensor_reading, float):
            self.ltc_label.text = f"{sensor_reading:.1f} {self.unit}"
            self.ltc_label.background_color = (
                GREEN if self.nominal_value(sensor_reading) else RED
            )
        else:
            log.error(
                f"Unsupported type passed to {self.name} value callback: {type(sensor_reading)}"
            )


class RelayIndicator(IOIndicator):
    from ltcbackend import Relay

    def __init__(self, sensor, **kwargs):
        super().__init__(sensor, **kwargs)

    def on_value(self, sensor_reading: Relay.State, *args, **kwargs):
        self.ltc_label.text = sensor_reading.name
        self.ltc_label.background_color = (
            GREEN if self.nominal_value(sensor_reading.value) else RED
        )


class RocketReadyIndicator(IOIndicator):
    def __init__(self, sensor, **kwargs):
        super().__init__(sensor, **kwargs)

    def on_value(self, sensor_reading, *args, **kwargs):
        if isinstance(sensor_reading, float):
            self.ltc_label.text = "High" if sensor_reading >= 2.0 else "Low"
            self.ltc_label.background_color = (
                GREEN if self.nominal_value(sensor_reading) else RED
            )
        else:
            log.error(
                f"Unsupported type passed to {self.name} value callback: {type(sensor_reading)}"
            )


class StatusDisplay(BoxLayout):
    '''Displays the overall state of the LTC Phidget sensors, and a message.

    Loaded from kv lang file first.
    '''

    class State(Enum):
        NOMINAL = ("Shore power must be off to arm", [0.5, 0.5, 0.5, 1])
        ARMED = (
            "Press abort to disarm and return to unarmed tab",
            [1, 0, 0, 1],
        )
        DISARMED = ("The igniter is now off and safe", [0.5, 0.5, 0.5, 1])
        IGNITED = (
            "Click Ignite again to disable Ignition power",
            [0, 1, 0.5, 1],
        )
        ERROR = (
            "An error occurred, \nPlease try again",
            [1, 0, 0, 1],
        )
        DISCONNECTED = ("Please leave a message or call again.", [1, 1, 0, 1])
        ABORT_FAILED = (
            "The attempt to shut off the igniter failed.",
            [1, 0, 0, 1],
        )

        @property
        def message(self):
            return self.value[0]

        @property
        def color(self):
            return self.value[1]

    # TODO: scrollable log

    def __init__(self, **kwargs):
        # load from the kv lang file
        super().__init__(**kwargs)
        self.set_state(self.State.DISCONNECTED)

    def on_attach(self, *args, **kwargs):
        self.set_state(self.State.NOMINAL)

    def on_detach(self, *args, **kwargs):
        self.set_state(self.State.DISCONNECTED)

    def on_error(self, errno, *args, **kwargs):
        match errno:
            case 4103:
                log.error("Sensor value out of range")
            case _:
                self.set_state(self.State.ERROR)

    def on_ignite(self, event):
        if event.state:
            self.set_state(self.State.IGNITED)
        else:
            self.set_state(self.State.NOMINAL)

    def on_value(self, *args, **kwargs):
        self.set_state(self.State.NOMINAL)

    def set_state(self, state: State, *args):
        log.info(f"Setting StatusDisplay state to {state}")
        self.state_info.text = state.name
        self.state_info.color = state.color
        if args:
            self.state_message.text = args[0].message
        else:
            self.state_message.text = state.message
