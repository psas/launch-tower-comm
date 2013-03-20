#!/usr/bin/env python

"""Nearly all of the Phidgets code comes from
InterfaceKit-simple.py, written by Adam Stelmack of Phidgets Inc,
Copyright 2010.  


Known Issues:
    Does not check/update output state indicators after a re-connect.
    **** Therefore, after re-connect, buttons and indicators may be 
         opposite actual state!


General Issues:
    The phidget main loop is separate from the Kivy main loop. 
    Many hacks ensue.
"""

__author__ = 'John Boyle'
__date__ = '22 Jan 2012'


import random
import sys
from ctypes import *
from time import sleep

#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, \
                                ErrorEventArgs, InputChangeEventArgs, \
                                OutputChangeEventArgs, SensorChangeEventArgs
from Phidgets.Dictionary import Dictionary, DictionaryKeyChangeReason
                                

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


##### Phidgets Event Handler Callback Functions #####
def DictionaryError(e):
    print("Dictionary Error %i: %s" % (e.eCode, e.description))
    return 0

def DictionaryServerConnected(e):
    print("Dictionary connected to server %s" % (e.device.getServerAddress()))
    try:
        #keyListener.start()
        pass
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
    return 0

def DictionaryServerDisconnected(e):
    print("Dictionary disconnected from server")
    try:
        #keyListener.stop()
        pass
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
    return 0

def setup_ph_dict():
    #Create a Dictionary object and a key listener object
    try:
        dictionary = Dictionary()
        
    except RuntimeError as e:
        print("Runtime Exception: %s" % e.details)
        print("Exiting....")
        exit(1)

    try:
        dictionary.setErrorHandler(DictionaryError)
        dictionary.setServerConnectHandler(DictionaryServerConnected)
        dictionary.setServerDisconnectHandler(DictionaryServerDisconnected)

    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

    print("Opening phidget object....")

    try:
        dictionary.openRemoteIP('localhost', port=5001)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

    try:
        while dictionary.isAttachedToServer() == False:
            pass
        else:
            print("Connected: %s" % (dictionary.isAttachedToServer()))
            print("Server: %s:%s" % (dictionary.getServerAddress(), dictionary.getServerPort()))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    return dictionary


########### KIVY Setup ############

class LogoFrame(FloatLayout):
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

    def set_properties(self, name):
        self.device_label.text = name # an attribute from kv file
        self.ioindex = name.lower()
        # Check connection status every half second.
        Clock.schedule_interval(self.check_status, 0.1)

    def check_status(self, instance):
        self.status_ind.text = dictionary.getKey(self.ioindex)
        self.conn_ind.text = dictionary.getKey('dev_state') 

class KvPhDictDemoListenerApp(App):

    def build(self):
        # The 'build' method is called when the object is run.

        dictlisten = LogoFrame()
        controlpanel = ControlPanel()

        #This LED setup may seem repetitive in this simple example.
        # It would be useful in more complex situations
        ai1 = OutDevice()
        ai2 = OutDevice()
        ai3 = OutDevice()

        ai1.set_properties(name='AI1')
        ai2.set_properties(name='AI2')
        ai3.set_properties(name='AI3')

        controlpanel.add_widget(ai1)
        controlpanel.add_widget(ai2)
        controlpanel.add_widget(ai3)

        dictlisten.content.add_widget(controlpanel) # 'content' is a reference to a
                                                  # layout placeholder in the
                                                  # kv lang file
        return dictlisten


if __name__ == '__main__':
    dictionary = setup_ph_dict()
    KvPhDictDemoListenerApp().run()
