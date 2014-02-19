# Phidgets, Twisted, Kivy

At launch L10, the Phidgets Webservice performed poorly over WiFi, specifically,
some segfaults occured and severe latency. 

To address this, we seek to use a more configurable and (hopefully) resilient
communication library for relaying commands and status to and from the launch
tower computer.

In this case, the ground control program is a client, and the launch tower
computer program is a server.
