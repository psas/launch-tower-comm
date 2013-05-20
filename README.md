# launch-tower-comm

## Phidget-free Dev. Mode

In `ltc.py,` there is a variable `USE_PHIDGETS`. Set it to False if you wish
to do layout work that doesn't require connected Phidgets.

## Dependencies

The following list is not complete, in other words, each of the three items
may require dependencies not listed here.

* [Phidgets C library, Python module and Phidgets Webservice](http://www.phidgets.com/docs/Software_Overview#Operating_System_Support)
* [Kivy](http://kivy.org/#download)
* At least one Phidgets Interfacekit connected throught the Phidgets webservice 

### Kivy Installation

* `sudo pip install kivy`
