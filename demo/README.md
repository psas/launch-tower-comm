# Launch Tower Comm, Demos

Several working programs demonstrating Phidgets into Kivy GUI's.

## `kv-ph-demo.py`

A demonstration of using a Kivy app as an GUI indicator for a Phidgets
Interface Kit sensor board, connected through the Phidgets Webservice.

This demo requires that you to have an Interface Kit board.  

The file `kvphdemo.kv` is that Kivy language file that describes much 
of the GUI layout.  Please refer to the Kivy documentation for more
information about the Kivy language and how it works with the Python
code.

## `kv-ph-demo-dict-keychanger.py`

Requires a running Phidgets webservice. Currently set to localhost:5001,
may be changed.  

Creates and updates four dictionary key/value pairs within the 
webservices' internal dictionary.  To be used in conjuction with the 
Kivy app.

## `kv-ph-demo-dict-listener.py`

A GUI indicator display of the four dictionary keys mentioned in 
'keychanger'.  

The Kivy language file `kvphdemodictlistener.kv` contains a few custom
widgets and layouts derived from the Kivy examples.  

Run the Phidgets webservice, then the keychanger, then this app.


