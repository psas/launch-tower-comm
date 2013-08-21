
import kivy
kivy.require('1.0.5')
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.button import Button
from Phidgets.PhidgetException import PhidgetException
from time import sleep

from ltcbackend import LTCbackend

class LTCButton(Button):
    def _do_press(self):
        pass

    def _do_release(self):
        pass

class LTCAccordionItem(AccordionItem):
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        return super(AccordionItem, self).on_touch_down(touch)

class IgnitionPopup(Popup):
    # TODO: popup should never be up when ignite button is lit
    def __init__(self, ignite=lambda: None, abort=lambda: None, **kwargs):
        self.ignite = ignite
        self.abort = abort
        super(IgnitionPopup, self).__init__(auto_dismiss=False, **kwargs)

    def ignitefunc(self):
        self.ignite()

class LTCctrl(Accordion):
    # TODO move Call Failed and Nominal state displays to backend
    # LTCctrl should only issue ARM and ARM -> Nominal|Abort Failed changes
    # because they're the only state changes it has a say in.

    # Assumption: trust that buttons are always synched to internal state

    ignition_abort_timeout = 10

    def __init__(self, ignite=lambda x: None, shorepower=lambda x: None, state=lambda x: None, **kwargs):
        # setup accordion
        super(LTCctrl, self).__init__(**kwargs)
        self.unarmed.collapse = False

        # setup callbacks
        self.ignite = ignite
        self.shorepower = shorepower
        self.set_state = state
        # setup internal state. The button states could be used, but this seems
        # safer becuase the buttons aren't always under our explicit control
        # (e.g. they're from Kivy)
        self._shorepower_state = None
        self._ignition_state = None


    def on_shorepower(self, event):
        """Callback function to set shorepower buttons state"""
        # This function should be the only place where the shorepower buttons
        # are set.
        if event.state is True:
            self.shorepower_button_on.state = 'down'
            self.shorepower_button_off.state = 'normal'
            if self._ignition_state is True:
                self._on_abort()
                # TODO: what happens when we can't successfully abort but shorepower comes on?
        elif event.state is False:
            self.shorepower_button_on.state = 'normal'
            self.shorepower_button_off.state = 'down'
        else:
            raise TypeError
        self._shorepower_state = event.state

    def on_ignite(self, event):
        """Callback function to set the ignite button state"""
        # This function should be the only place where the ignite button is set
        if event.state is True:
            self.ignite_button.state = 'down'
            self._ignition_state = True
        elif event.state is False:
            self.ignite_button.state = 'normal'
            # self.arm depends on self._ignition_state being correct
            self._ignition_state = False
            self.arm(False)
        else:
            raise TypeError

    def _on_popup_ignite(self):
        try:
            self.ignite(True)
            Clock.schedule_once(lambda x:self._on_abort(), self.ignition_abort_timeout)
        except PhidgetException:
            self.on_abort()
            self.set_state('Phidget Call Failed')

    def arm(self, state):
        if state is True:
            if self._shorepower_state is False:
                self.armed.collapse = False
                self.set_state('ARMED')
            # else: error
        elif state is False:
            if self._ignition_state is False:
                self.unarmed.collapse = False
                self.set_state('Nominal')
            # else: error
        else:
            raise TypeError

    def _ignition_popup(self):
        if self._ignition_state is True:
            self._on_abort()
        else:
            IgnitionPopup(self._on_popup_ignite).open()

    def _on_abort(self):
        # TODO: cancel scheduled abort
        try:
            self.ignite(False)
            # TODO: abort failed timeout, abort failed state,
            #  keep button lit while attempting to abort
            if self._ignition_state is False:
                self.arm(False)
            # else:
            #    self.set_state("Abort Failed")
        except PhidgetException:
            self.set_state('Phidget Call Failed')

    def _on_shorepower_button(self, state):
        try:
            self.shorepower(state)
            self.set_state('Nominal')
        except PhidgetException:
            self.set_state('Phidget Call Failed')

#########Module test########

if __name__ == '__main__':
    import sys
    from kivy.app import App
    class ltcctrlApp(App):
        def build(self):
            try:
                if sys.argv[1] == '-t':
                    cdict = dict()
                    ltc = LTCbackend(cdict)
                    return LTCctrl(ltc.ignite, ltc.shorepower)
                else:
                    return LTCctrl()
            except IndexError:
                return LTCctrl()

    ltcctrlApp().run()
