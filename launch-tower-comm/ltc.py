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
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label  import Label
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.codeinput import CodeInput
from kivy.extras.highlight import KivyLexer
from kivy.config import ConfigParser
from kivy.uix.settings import Settings


########### KIVY Setup ############

class LTC(FloatLayout):
    # Loaded from the kv lang file
    pass
    
#class StandardWidgets(FloatLayout):

    #value = NumericProperty(0)

    #def __init__(self, **kwargs):
        #super(StandardWidgets, self).__init__(**kwargs)
        #Clock.schedule_interval(self.increment_value, 1 / 30.)

    #def increment_value(self, dt):
        #self.value += dt

class LTCApp(App):

    #~ def __init__(self, **kwargs):
        #~ super(App, self).__init__(**kwargs)

    def build(self):
        # The 'build' method is called when the object is run.

        root = BoxLayout(spacing=10)

        btn1 = Button(text='Hello', size_hint=(.7, 1))
        btn2 = Button(text='World', size_hint=(.3, 1))
        lbl1 = Label(text='Devices are involved')

        root.add_widget(btn1)
        root.add_widget(btn2)
        ltc = LTC()
        ltc.content.add_widget(root) 
        return ltc
    
    def build_config(self, config):
        config.add_section('kinect')
        config.set('kinect', 'index', '0')
        config.add_section('shader')
        config.set('shader', 'theme', 'rgb')

    def build_settings(self, settings):
        settings.add_json_panel('Testing', self.config, data='''[
            { "type": "title", "title": "Kinect" },
            { "type": "numeric", "title": "Index",
              "desc": "Kinect index, from 0 to X",
              "section": "kinect", "key": "index" },
            { "type": "title", "title": "Shaders" },
            { "type": "options", "title": "Theme",
              "desc": "Shader to use for a specific visualization",
              "section": "shader", "key": "theme",
              "options": ["rgb", "hsv", "points"]}
        ]''')


if __name__ == '__main__':
    LTCApp().run()
