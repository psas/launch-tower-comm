#!/usr/bin/env python

'''ltc.py - the launch-tower-comm program.
Runs on Phidgets and Kivy.

'''

#Kivy specific imports
import kivy
kivy.require('1.0.5')
from kivy.app import App
from kivy.clock import Clock
from kivy.config import ConfigParser
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label  import Label
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty

########### KIVY Setup ############

class KvPhDemo(FloatLayout):
    ''' Loaded from the kv lang file
    '''

class ControlPanel(BoxLayout):
    '''Loaded from the kv lang file.
    '''

class OutDevice(BoxLayout):
    ''' Loaded from the kv lang file.
    '''
    # 'self.__init__' didn't work to do what 'set_properties' does
    # b/c I found I can't call object attributes defined within the
    # kv lang file until apparently AFTER the object has been initialized.
    # That isn't to say that there is a more natural way of doing this
    # that is provided by Kivy.

    def set_properties(self, name, iotype, ioindex):
        self.device_label.text = name + ' ' + str(ioindex)# an attribute from kv file
        self.iotype = iotype
        self.ioindex = ioindex

        # Explicitly set outputs to OFF (good habit in control situations)
        # Just as easily could read the current status instead.
        self.status_ind.text = 'OFF'
        interfaceKit.setOutputState(self.ioindex, False)

        # Check connection status every half second.
        Clock.schedule_interval(self.check_connection, 0.5)

    def check_connection(self, instance):
        # 'ik_attached' is set by the phidgets 'interfaceKitDetached' and
        # 'interfaceKitAttached' event handlers
        self.conn_ind.text = 'Connected' if bool(ik_attached) else 'disconnected'

    def toggle_state(self, state):
        ledstate = interfaceKit.getOutputState(self.ioindex)
        ledstate = not ledstate
        interfaceKit.setOutputState(self.ioindex, ledstate)
        self.status_ind.text = 'OFF' if state=='normal' else 'ON'


class KvPhDemoApp(App):

    def build(self):
        # The 'build' method is called when the object is run.

        kvphdemo = KvPhDemo()
        controlpanel = ControlPanel()

        #This LED setup may seem repetitive in this simple example.
        # It would be useful in more complex situations
        led1 = OutDevice()
        led4 = OutDevice()
        led6 = OutDevice()

        led1.set_properties(name='LED', iotype='output', ioindex=1)
        led4.set_properties(name='LED', iotype='output', ioindex=4)
        led6.set_properties(name='LED', iotype='output', ioindex=6)

        controlpanel.add_widget(led1)
        controlpanel.add_widget(led4)
        controlpanel.add_widget(led6)

        kvphdemo.content.add_widget(controlpanel) # 'content' is a reference to a
                                                  # layout placeholder in the
                                                  # kv lang file
        return kvphdemo


if __name__ == '__main__':
    interfaceKit = setup_interfaceKit()
    KvPhDemoApp().run()
