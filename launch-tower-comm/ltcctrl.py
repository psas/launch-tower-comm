
import kivy
kivy.require('1.0.5')
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.button import Button
from Phidgets.PhidgetException import PhidgetException

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
    ignition_abort_timeout = 10

    def __init__(self, ignite=lambda: None, abort=lambda: None, **kwargs):
        self.ignite = ignite
        self.abort = abort
        super(IgnitionPopup, self).__init__(auto_dismiss=False, **kwargs)

    def on_button_ignite(self):
        try:
            Clock.schedule_once(self.abort, self.ignition_abort_timeout)
            self.ignite(True)
        except PhidgetException:
            self.abort()
            self.set_state('Phidget Call Failed')


class LTCctrl(Accordion):
    # TODO move Call Failed and Nominal state displays to backend
    # LTCctrl should only issue ARM and ARM -> Nominal changes
    # because they're the only state changes it has a say in.

    # TODO: checks that buttons are displaying the right thing?

    def __init__(self, ignite=lambda x: None, shorepower=lambda x: None, state=lambda x: None, **kwargs):
        # setup callbacks
        self.ignite = ignite
        self.shorepower = shorepower
        self.set_state = state
        # setup internal state
        self.state_shorepower = None
        self.state_ignition = None
        self.state_abort = None
        # nothing explicitly depends on the arm state
        # setup GUI
        self.popup = IgnitionPopup(ignite, self.abort)
        super(LTCctrl, self).__init__(**kwargs)
        self.accordian_unarmed.collapse = False


    def on_shorepower(self, event):
        """Callback function to set shorepower buttons state"""
        # This function is the only place where the shorepower buttons are set
        if event.state is True:
            self.button_shorepower_on.state = 'down'
            self.button_shorepower_off.state = 'normal'
            if self.state_ignition is True:
                # TODO: log that shorepower was turned on while ignition is on
                self.abort()
        elif event.state is False:
            self.button_shorepower_on.state = 'normal'
            self.button_shorepower_off.state = 'down'
        else:
            raise TypeError

        self.state_shorepower = event.state

    def on_ignite(self, event):
        """Callback function to set the ignite button state"""
        # This function is the only place where the ignite button is set
        if event.state is True:
            self.button_ignite.state = 'down'
            self.state_ignition = True
            # if ignite happens showing it takes precedence over everything
            self.accordion_armed.collapse = False
            self.popup.dismiss()
        elif event.state is False:
            self.button_ignite.state = 'normal'
            self.button_abort.state = 'normal'
            self.state_abort = False
            Clock.unschedule(self.abort)
            # self.arm depends on self.state_ignition being correct
            self.state_ignition = False
            self.arm(False)
        else:
            raise TypeError

    def arm(self, state):
        if state is True:
            if self.state_shorepower is False:
                self.accordion_armed.collapse = False
                self.set_state('ARMED')
            # TODO: else log that arm was attempted with sp true
        elif state is False:
            if self.state_ignition is False:
                self.accordion_unarmed.collapse = False
                self.set_state('Nominal')  # TODO: this should be disarm state
            else:
                raise RuntimeError("Attempt to disarm was made while ignition relay was closed")
        else:
            raise TypeError

    def abort(self, event=None):
        Clock.unschedule(self.abort)
        if self.state_ignition == False:
            self.arm(False)
        else:
            self.button_abort.state = 'down'
            self.state_abort = True
            try:
                self.ignite(False)
            except PhidgetException:
                self.button_abort.state = 'normal'
                self.state_abort = False
                # TODO: log abort failed
                self.set_state('Phidget Call Failed')

    def on_button_ignite(self):
        if self.state_abort is True:
            pass  # TODO: log that ignite can't happen becuase abort is in progress
        elif self.state_ignition is True:
            self.abort()
        else:
            self.popup.open()

    def on_button_shorepower(self, state):
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
