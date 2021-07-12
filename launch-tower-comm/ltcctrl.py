
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

    def _do_release(self, *args):
        pass


class LTCAccordionItem(AccordionItem):
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        return super(AccordionItem, self).on_touch_down(touch)


class IgnitionPopup(Popup):
    ignition_abort_timeout = 10

    def __init__(self, ignite=lambda: None, abort=lambda: None, state={}, **kwargs):
        self.ignite = ignite
        self.abort = abort
        self.state = state
        super(IgnitionPopup, self).__init__(auto_dismiss=False, **kwargs)

    def on_button_ignite(self):
        try:
            Clock.schedule_once(self.abort, self.ignition_abort_timeout)
            self.ignite(True)
            self.state['popup_abort_lockin'] = True
        except PhidgetException:
            self.abort()


class LTCctrl(Accordion):
    def __init__(self, ignite=lambda x: None, shorepower=lambda x: None, status=lambda x: None, **kwargs):
        # setup callbacks
        self.ignite = ignite
        self.shorepower = shorepower
        self.set_status = status
        # setup internal state
        self.state = dict()
        self.state['shorepower'] = None
        self.state['ignition'] = None
        self.state['abort'] = None
        self.state['popup_abort_lockin'] = None
        # nothing explicitly depends on the arm state
        # setup GUI
        self.popup = IgnitionPopup(ignite, self.abort, self.state)
        super(LTCctrl, self).__init__(**kwargs)
        self.accordion_unarmed.collapse = False

    def on_shorepower(self, event):
        """Callback function to set shorepower buttons state"""
        # This function is the only place where the shorepower buttons are set
        if event.state is True:
            self.button_shorepower_on.state = 'down'
            self.button_shorepower_off.state = 'normal'
            if self.state['ignition'] is True:
                # TODO: log that shorepower was turned on while ignition is on
                self.abort()
        elif event.state is False:
            self.button_shorepower_on.state = 'normal'
            self.button_shorepower_off.state = 'down'
        else:
            raise TypeError

        self.state['shorepower'] = event.state

    def on_ignite(self, event):
        """Callback function to set the ignite button state"""
        # This function is the only place where the ignite button is set
        if event.state is True:
            self.button_ignite.state = 'down'
            self.state['ignition'] = True
            self.state['popup_abort_lockin'] = False
            # if ignite happens showing it takes precedence over everything
            self.accordion_armed.collapse = False
            self.popup.dismiss()
        elif event.state is False:
            self.button_ignite.state = 'normal'
            self.button_abort.state = 'normal'
            self.state['abort'] = False
            Clock.unschedule(self.abort)
            # self.arm depends on self.state['ignition'] being correct
            self.state['ignition'] = False
            self.arm(False)
        else:
            raise TypeError

    def arm(self, state):
        if state is True:
            if self.state['shorepower'] is False:
                self.accordion_armed.collapse = False
                self.set_status('ARMED')
            # TODO: else log that arm was attempted with sp true
        elif state is False:
            if self.state['ignition'] is False:
                self.accordion_unarmed.collapse = False
                self.set_status('Disarmed')
            else:
                raise RuntimeError("Attempt to disarm was made while \
                        ignition relay was closed")
        else:
            raise TypeError

    def abort(self, event=None):
        Clock.unschedule(self.abort)
        if self.state['ignition'] is False and self.state['popup_abort_lockin'] is not True:
            self.arm(False)
        else:
            self.button_abort.state = 'down'
            self.state['abort'] = True
            try:
                self.ignite(False)
            except PhidgetException:
                self.button_abort.state = 'normal'
                self.state['abort'] = False
                self.set_status('Abort Failed')

    def on_button_ignite(self):
        if self.state['abort'] is True:
            # TODO: log that ignite can't happen becuase abort is in progress
            pass
        elif self.state['ignition'] is True:
            self.abort()
        else:
            self.popup.open()

    def on_button_shorepower(self, state):
        try:
            self.shorepower(state)
        except PhidgetException:
            pass

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
