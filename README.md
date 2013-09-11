# launch-tower-comm

The launch control software for Portland State Aerospace Society.

A GUI written in Kivy (a multi-touch UI framework) that talks to the
Phidgets Webservice over the network.  

We use it to control relays connected to a Beagleboard on our launch
tower computer, and to watch voltages and temperatures of various other
things.

If you have a remote Beagleboard or Raspberry Pi or similar connected to
Phidget Interface Kit boards, and want to control and observe them remotely,
this app could be made to work for you.  

## Dependencies

The following list is not complete, in other words, each of the three items
may require dependencies not listed here.

* [Phidgets C library, Python module and Phidgets Webservice](http://www.phidgets.com/docs/Software_Overview#Operating_System_Support)
* [Kivy](http://kivy.org/#download)
* At least one Phidgets Interfacekit connected throught the Phidgets webservice 
