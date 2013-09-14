# Launch Tower Comm
Launch Tower Comm is the Portland State Aerospace Society's launch tower 
control.  

It is run by [Kivy](http://kivy.org), a multi-touch GUI framework, and 
[Phidgets](https://www.phidgets.com), "Unique and Easy to Use USB Interfaces."

[Portland State Aerospace Society](https://psas.pdx.edu)

---

## How to use it if you don't have a launch tower

If you have a remote Beagleboard or Raspberry Pi or similar connected to
Phidget Interface Kit boards, and want to control and observe them remotely,
this app could work for you.  

We use it to control relays connected to a Beagleboard on our launch
tower computer, and to display voltages and temperatures on the tower.


## Dependencies

The following list is not complete, in other words, each of the three items
may require dependencies not listed here.

* [Phidgets C library, Python module and Webservice](http://www.phidgets.com/docs/Software_Overview#Operating_System_Support)
* [Kivy](http://kivy.org/#download)
* At least one Phidgets Interfacekit connected throught the Phidgets webservice 
