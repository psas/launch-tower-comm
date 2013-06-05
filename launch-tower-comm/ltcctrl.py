'''
Created on May 28, 2013

@author: theo
'''

import kivy
kivy.require('1.0.5')
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config, ConfigParser
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.extras.highlight import KivyLexer

from Phidgets.PhidgetException import PhidgetException

from ltcbackend import LTCbackend

class LTCAccordionItem(AccordionItem):
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        return super(AccordionItem, self).on_touch_down(touch)

# TODO: exception safe. On exception don't change gui state

class ltcctrl(Accordion):
    def __init__(self, ignite=lambda x: None, shorepower=lambda x: None, **kwargs):
        super(ltcctrl, self).__init__(**kwargs)
        self.unarmed.collapse = False
        self.ignitefunc = ignite
        self.spfunc = shorepower

    def on_ignite(self):
        if self.ignite.state == 'normal':
            self.unarmed.collapse = False
        else:
            IgnitionPopup(self.ignitefunc, self.popupabortfunc).open()

    def popupabortfunc(self):
        self.ignite.state = 'normal'

    def shorepowerfunc(self, state):
        try:
            self.spfunc(state)
        except PhidgetException:
            pass

    def on_armed_collapse(self, value):
        if not value:
            self.ignite.state = 'normal'
            try:
                self.ignitefunc(False)
            except PhidgetException:
                pass

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

class ltcctrlApp(App):
    def build(self):
        cdict = dict()
        ltc = LTCbackend(cdict)

        return ltcctrl(ltc.ignite, ltc.shorepower)


if __name__ == '__main__':
    ltcctrlApp().run()
