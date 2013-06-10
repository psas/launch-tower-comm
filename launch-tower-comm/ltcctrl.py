
import kivy
kivy.require('1.0.5')
from kivy.app import App
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock

from Phidgets.PhidgetException import PhidgetException

from ltcbackend import LTCbackend

class LTCAccordionItem(AccordionItem):
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        return super(AccordionItem, self).on_touch_down(touch)

class LTCctrl(Accordion):
    def __init__(self, ignite=lambda x: None, shorepower=lambda x: None, **kwargs):
        super(LTCctrl, self).__init__(**kwargs)
        self.unarmed.collapse = False
        self.ignite = ignite
        self.shorepower = shorepower
        self.shorepower_button.state = 'normal'

    def on_ignite(self):
        if self.ignite_button.state == 'normal':
            self.on_abort()
        else:
            IgnitionPopup(self.ignite, self.on_popup_abort).open()

    def on_popup_abort(self):
        self.ignite_button.state = 'normal'

    def on_arm(self):
        if self.shorepower_button.state == 'down': self.armed.collapse = False

    def on_abort(self):
        try:
            if self.ignite_button.state == 'down':
                self.ignite(False)
                self.ignite_button.state = 'normal'
            self.unarmed.collapse = False
        except PhidgetException:
            pass

    def on_shorepower(self, button, state):
        try:
            self.shorepower(state)
            button.state = 'down'
        except PhidgetException:
            button.state = 'normal'

class IgnitionPopup(Popup):
    def __init__(self, ignite, abort, **kwargs):
        self.ignite = ignite
        self.abort = abort
        super(IgnitionPopup, self).__init__(**kwargs)

    def ignitefunc(self):
        try:
            self.ignite(True)
        except PhidgetException:
            pass
            self.abort()

class ltcctrlApp(App):
    def build(self):
        cdict = dict()
        ltc = LTCbackend(cdict)

        return LTCctrl(ltc.ignite, ltc.shorepower)


if __name__ == '__main__':
    ltcctrlApp().run()
