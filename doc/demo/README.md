# launch-tower-comm, Demos

Several programs demonstrating Phidgets integrated into Kivy GUIs.

# How to Run Them

* Install Kivy. (follow instructions at (kivy.org)[kivy.org]
* Install the (Phidgets)[phidgets.com] libraries, Python module, and Webservice 
* Install twisted

## InterfaceKit Demo - `kv-ph-demo.py`

You must have an Interface Kit board connected through the webservice.

## Webservice Demo - `kv-ph-demo-dict-listener.py`

You only need a working webservice. Follow instructions below.

# The Demo Files

## `kv-ph-demo.py`

A demonstration of using a Kivy app as an GUI indicator for a Phidgets
Interface Kit sensor board, connected through the Phidgets Webservice.

This demo requires that you to have an Interface Kit board.  

The file `kvphdemo.kv` is that Kivy language file that describes much 
of the GUI layout.  Please refer to the Kivy documentation for more
information about the Kivy language and how it works with the Python
code.

## `kv-ph-demo-dict-listener.py`

Start the Phidgets webservice, then the keychanger, then this app.

A GUI indicator display of the four dictionary keys mentioned in 
'keychanger'.  

The Kivy language file `kvphdemodictlistener.kv` contains a few custom
widgets and layouts derived from the Kivy examples.  

### `kv-ph-demo-dict-keychanger.py`

Requires a running Phidgets webservice. Currently set to localhost:5001,
may be changed.  

Creates and updates four dictionary key/value pairs within the 
webservices' internal dictionary.  To be used in conjuction with the 
Kivy app.

# Twisted/Kivy demo

`echo-client-app.py` and `echo-server-app.py` demo how to use Twisted with
Kivy.  The server is like launch control and the client like the LTC. 

The client will reconnect if you try to send text after the server comes
back up.  
