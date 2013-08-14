
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
    def __init__(self, ignite, abort, **kwargs):
        self.ignite = ignite
        self.abort = abort
        super(IgnitionPopup, self).__init__(auto_dismiss=False, **kwargs)

    def ignitefunc(self):
        self.ignite()

class LTCctrl(Accordion):
    ignition_abort_timeout = 10

    def __init__(self, ignite=lambda x: None, shorepower=lambda x: None, state=lambda x: None, **kwargs):
        super(LTCctrl, self).__init__(**kwargs)
        self.unarmed.collapse = False
        self.ignite = ignite
        self.shorepower = shorepower
        self.shorepower_button_off.state = 'normal'
        self.shorepower_sensor_state = False
        self.set_state = state

    def on_popup_ignite(self):
        try:
            self.ignite(True)
            Clock.schedule_once(lambda x:self.on_abort(), self.ignition_abort_timeout)
        except PhidgetException:
            self.on_abort()
            self.set_state('Phidget Call Failed')

    def on_popup_abort(self):
        self.ignite_button.state = 'normal'

    def on_arm(self):
        if self.shorepower_button_off.state == 'down' and self.shorepower_sensor_state is False:
            self.armed.collapse = False
            self.set_state('ARMED')

    def on_ignite(self):
        if self.ignite_button.state == 'normal':
            self.on_abort()
        else:
            IgnitionPopup(self.on_popup_ignite, self.on_popup_abort).open()

#     def on_ignite(self, state):
#         if state is True:
#             self.bttn_ignite.state = 'down'
#         elif state is False:
#             self.bttn_ignite.state = 'normal'

    def on_shorepower(self, state):
        if state is True:
            self.bttn_shorepower_on = True
            self.bttn_shorepower_off = False
        elif state is False:
            self.bttn_shorepower_on = False
            self.bttn_shorepower_off = True

    def on_abort(self):
        try:
            self.ignite(False)
            if self.ignite_button.state == 'down':
                self.ignite_button.state = 'normal'
            self.unarmed.collapse = False
            self.set_state('Nominal')
        except PhidgetException:
            self.set_state('Phidget Call Failed')



    def sp_callback(self, event):
        self.shorepower_sensor_state = event.state
        if event.state is True:
            self.shorepower_button_on.state = 'down'
        else:
            self.shorepower_button_off.state = 'down'

    def on_shorepower(self, button, state):
        try:
            self.shorepower(state)
            self.set_state('Nominal')
        except PhidgetException:
            button.state = 'normal'
            self.set_state('Phidget Call Failed')


#########Module test########

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

if __name__ == '__main__':
    ltcctrlApp().run()
