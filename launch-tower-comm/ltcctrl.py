from collections.abc import Callable
from typing import Any, TypedDict, override

import kivy
import ltclogger as log
from kivy.clock import Clock
from kivy.input.providers.mouse import MouseMotionEvent
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from ltcbackend import LTCbackend, Relay
from ltcui import StatusDisplay
from Phidget22.PhidgetException import PhidgetException

kivy.require('1.0.5')


class LTCAccordionItem(AccordionItem):
    @override
    def on_touch_down(self, touch: MouseMotionEvent) -> Any:
        if not self.collide_point(*touch.pos):
            return None
        return super().on_touch_down(touch)


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
        self.state = (
            {
                'shorepower': None,
                'ignition': None,
                'abort': None,
                'popup_abort_lockin': None,
            }
            if state is None
            else state
        )
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
        shorepower: bool | None
        ignition: bool | None
        abort: bool | None
        popup_abort_lockin: bool | None

    def __init__(
        self,
        ignite: Callable[[Relay.State], None] = lambda _: None,
        shorepower: Callable[[Relay.State], None] = lambda _: None,
        status: Callable[[StatusDisplay.State], None] = lambda _: None,
        **kwargs: object,
    ) -> None:
        # setup callbacks
        self.ignite = ignite
        self.shorepower = shorepower
        self.set_status_display_state = status

        # setup internal state
        # nothing explicitly depends on the arm state

        self.state: LTCctrl.StateType = {
            'shorepower': None,
            'ignition': None,
            'abort': None,
            'popup_abort_lockin': None,
        }

        # setup GUI
        self.popup = IgnitionPopup(self.set_status_display_state, ignite, self.abort, self.state)
        super().__init__(**kwargs)
        self.accordion_unarmed.collapse = False

    def on_shorepower_attach(self) -> None:
        self.button_shorepower_off.disabled = False
        self.button_shorepower_on.disabled = False

    def on_shorepower_detach(self) -> None:
        self.button_shorepower_off.disabled = True
        self.button_shorepower_on.disabled = True
        self.button_arm.disabled = True

    def on_shorepower(self, state: Relay.State) -> None:
        """Callback function to set shorepower buttons state"""
        # This function is the only place where the shorepower buttons are set
        match state:
            case Relay.State.ON:
                self.button_shorepower_off.state = 'normal'
                self.button_shorepower_on.state = 'down'
                self.button_arm.disabled = True
                if self.state['ignition'] is True:
                    # TODO: log that shorepower was turned on while ignition is on
                    self.abort()

            case Relay.State.OFF:
                self.button_shorepower_on.state = 'normal'
                self.button_shorepower_off.state = 'down'
                self.button_arm.disabled = False

        self.state['shorepower'] = state.value

    def on_ignite_detach(self) -> None:
        self.accordion_armed.collapse = True
        self.accordion_unarmed.collapse = False
        self.popup.dismiss()

    def on_ignite(self, state: Relay.State) -> None:
        """Callback function to set the ignite button state"""
        # This function is the only place where the ignite button is set

        match state:
            case Relay.State.ON:
                self.button_ignite.state = 'down'
                self.state['ignition'] = True
                self.state['popup_abort_lockin'] = False
                # if ignite happens showing it takes precedence over everything
                self.accordion_armed.collapse = False
                self.popup.dismiss()
            case Relay.State.OFF:
                self.button_ignite.state = 'normal'
                self.button_abort.state = 'normal'
                self.state['abort'] = False
                Clock.unschedule(self.abort)
                # self.arm depends on self.state['ignition'] being correct
                self.state['ignition'] = False
                self.arm(state=False)

    def arm(self, *, state: bool) -> None:
        if state:
            if self.state['shorepower'] is False:
                self.accordion_armed.collapse = False
                self.set_status_display_state(StatusDisplay.State.ARMED)
            # TODO: else log that arm was attempted with sp true
        elif not self.state['ignition']:
            self.accordion_unarmed.collapse = False
            self.set_status_display_state(StatusDisplay.State.DISARMED)
        else:
            raise RuntimeError("Attempt to disarm was made while ignition relay was closed")

    def abort(self) -> None:
        Clock.unschedule(self.abort)

        if self.state['ignition'] is False and self.state['popup_abort_lockin'] is not True:
            self.arm(state=False)
        else:
            self.button_abort.state = 'down'
            self.state['abort'] = True
            try:
                self.ignite(Relay.State.OFF)
            except PhidgetException:
                self.button_abort.state = 'normal'
                self.state['abort'] = False
                self.set_status_display_state(StatusDisplay.State.ABORT_FAILED)

    def on_button_ignite(self) -> None:
        if self.state['abort'] is True:
            # TODO: log that ignite can't happen becuase abort is in progress
            pass
        elif self.state['ignition'] is True:
            self.abort()
        else:
            self.popup.open()

    def on_button_shorepower(self, *, state: bool) -> None:
        try:
            self.shorepower(Relay.State.ON if state else Relay.State.OFF)
            self.set_status_display_state(StatusDisplay.State.NOMINAL)
        except PhidgetException as e:
            self.set_status_display_state(StatusDisplay.State.ERROR)
            log.error(e)


######### Module test ########

if __name__ == '__main__':
    import sys

    from kivy.app import App

    class LTCCtrlApp(App):
        def build(self) -> Widget:
            try:
                if sys.argv[1] == '-t':
                    ltc = LTCbackend()
                    return LTCctrl(ltc.ignite, ltc.shorepower)
                return LTCctrl()
            except IndexError:
                return LTCctrl()

    LTCCtrlApp().run()
