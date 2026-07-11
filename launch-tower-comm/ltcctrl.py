from collections.abc import Callable
from typing import TypedDict

import kivy
import ltclogger as log
from kivy.clock import Clock
from kivy.uix.accordion import Accordion
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from ltcbackend import LTCbackend, Relay
from ltcui import StatusDisplay
from Phidget22.PhidgetException import PhidgetException

kivy.require('1.0.5')


class IgnitionPopup(Popup):
    ignition_abort_timeout = 10

    def __init__(
        self,
        set_status_display_state: Callable[[StatusDisplay.State], None],
        ignite: Callable[[Relay.State], None] = lambda _: None,
        abort: Callable[[], None] = lambda: None,
        state: 'LTCctrl.StateType | None' = None,
        **kwargs: object,
    ) -> None:
        self.ignite = ignite
        self.abort = abort
        self.state = {'popup_abort_lockin': False} if state is None else state
        self.set_status_display_state = set_status_display_state
        super().__init__(auto_dismiss=False, **kwargs)

    def on_button_ignite(self) -> None:
        try:
            Clock.schedule_once(lambda _dt: self.abort(), self.ignition_abort_timeout)
            self.ignite(Relay.State.ON)
            self.state['popup_abort_lockin'] = True
            self.set_status_display_state(StatusDisplay.State.IGNITED)
        except PhidgetException as e:
            log.critical(e)
            self.abort()


class LTCctrl(Accordion):
    class StateType(TypedDict):
        popup_abort_lockin: bool

    def __init__(
        self,
        backend: LTCbackend,
        status: Callable[[StatusDisplay.State], None] = lambda _: None,
        **kwargs: object,
    ) -> None:
        self.backend = backend
        self.set_status_display_state = status

        backend.shore.add_callback(self._on_shorepower_attach, 'attach')
        backend.shore.add_callback(self._on_shorepower_detach, 'detach')
        backend.shore.add_callback(self._on_shorepower, "value")
        backend.ignition.add_callback(self._on_ignite_detach, "detach")
        backend.ignition.add_callback(self._on_ignite, "value")

        self.state: LTCctrl.StateType = {
            'popup_abort_lockin': False,
        }

        # setup GUI
        self.popup = IgnitionPopup(
            self.set_status_display_state,
            backend.ignite,
            self.abort,
            self.state,
        )
        super().__init__(**kwargs)
        self.accordion_unarmed.collapse = False

    def _on_shorepower_attach(self) -> None:
        self.button_shorepower_off.disabled = False
        self.button_shorepower_on.disabled = False

    def _on_shorepower_detach(self) -> None:
        self.button_shorepower_off.disabled = True
        self.button_shorepower_on.disabled = True
        self.button_arm.disabled = True

    def _on_shorepower(self, state: Relay.State) -> None:
        """Callback function to set shorepower buttons state"""
        # This function is the only place where the shorepower buttons are set
        match state:
            case Relay.State.ON:
                self.button_shorepower_off.state = 'normal'
                self.button_shorepower_on.state = 'down'
                self.button_arm.disabled = True
                if self.backend.ignition.getState():
                    log.critical('Shorepower enabled while ignition is on!')
                    self.abort()

            case Relay.State.OFF:
                self.button_shorepower_on.state = 'normal'
                self.button_shorepower_off.state = 'down'
                self.button_arm.disabled = False

    def _on_ignite_detach(self) -> None:
        self.accordion_armed.collapse = True
        self.accordion_unarmed.collapse = False
        self.popup.dismiss()

    def _on_ignite(self, state: Relay.State) -> None:
        """Callback function to set the ignite button state"""
        # This function is the only place where the ignite button is set

        match state:
            case Relay.State.ON:
                self.button_ignite.state = 'down'
                self.state['popup_abort_lockin'] = False
                # if ignite happens showing it takes precedence over everything
                self.accordion_armed.collapse = False
                self.popup.dismiss()
            case Relay.State.OFF:
                self.button_ignite.state = 'normal'
                self.button_abort.state = 'normal'
                Clock.unschedule(self.abort)
                self.arm(state=False)

    def arm(self, *, state: bool) -> None:
        if state:
            if not self.backend.shore.getState():
                self.accordion_armed.collapse = False
                self.set_status_display_state(StatusDisplay.State.ARMED)
            # TODO: else log that arm was attempted with sp true
        elif not self.backend.ignition.getState():
            self.accordion_unarmed.collapse = False
            self.set_status_display_state(StatusDisplay.State.DISARMED)
        else:
            raise RuntimeError("Attempt to disarm was made while ignition relay was closed")

    def abort(self) -> None:
        Clock.unschedule(self.abort)

        if not self.backend.ignition.getState() and not self.state['popup_abort_lockin']:
            self.arm(state=False)
        else:
            self.button_abort.state = 'down'
            try:
                self.backend.ignite(Relay.State.OFF)
            except PhidgetException:
                self.button_abort.state = 'normal'
                self.set_status_display_state(StatusDisplay.State.ABORT_FAILED)

    def on_button_ignite(self) -> None:
        if self.backend.ignition.getState():
            self.abort()
        else:
            self.popup.open()

    def on_button_shorepower(self, *, state: bool) -> None:
        try:
            self.backend.shorepower(Relay.State.ON if state else Relay.State.OFF)
            self.set_status_display_state(StatusDisplay.State.NOMINAL)
        except PhidgetException as e:
            self.set_status_display_state(StatusDisplay.State.ERROR)
            log.error(e)


######### Module test ########

if __name__ == '__main__':
    import sys

    from kivy.app import App
    from ltcbackend import MockBackend

    class LTCCtrlApp(App):
        def build(self) -> Widget:
            try:
                backend = LTCbackend() if sys.argv[1] == '-t' else MockBackend()
            except IndexError:
                backend = MockBackend()

            self.bind(on_stop=lambda _: backend.close())
            self.bind(on_start=lambda _: backend.start())
            return LTCctrl(backend)

    LTCCtrlApp().run()
