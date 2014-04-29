---
title: Launch Tower Instructions
layout: base
---


# Wireless Network Configuration

Channel:  802.11b – Ch1
SSID:   psas
WPA-2:  psasrocket
Router IP Address:  192.168.128.1
DHCP Range:   .50 - .100
Static Range:   .10 - .40

Original LTC Computer:  192.168.128.2/24

New LTC Computer:     192.168.128.250/24 (wireless)
192.168.128.251/24 (wired)

Access point
IP Address:   192.168.128.1
Username: admin
Password: psaslv1b
(if password doesn’t work – try leaving it blank)



# Basic Setup

## Tools Needed

* Miniature flathead screwdriver
* Miniature flathead screwdriver
* Large Phillips screwdriver


## Mounting
1. Mount LTC box to already-standing launch tower [graphic]
1. Turn “side bulkhead” POWER and ARMING switches to “OFF” position
   [graphic]
1. Place breaker-bar in LTC [graphic]
1. Remove bottom plate cover from cable enclosure [graphic]


## Power Cable Routing

Note: Route each powerpole connector one at a time and they will fit
through opening. If you attempt to run all three at once, they will
not fit.

1. Run Ignite leads through “bottom bulkhead” opening “A” and connect
   to 3&4
1. Run Battery leads though “bottom bulkhead” opening “A” and connect
   to 1&2
1. Run Solar Panel leads through “bottom bulkhead” opening “A” and
   connect to 5&6


## Data Cable Routing

1. Connect rocket umbilical to “bottom bulkhead” receptor “B”
1. Connect sensor data cable into “bottom bulkhead” receptor “C”
1. Connect Wireless antenna cable to “bottom bulkhead” receptor “D”

### Initializing
1. Turn “side bulkhead” Power switch to “ON”
1. Look for lights on devices to indicate operation 
  * L7/L8/L9 should be flashing
  * L2/L6 should light
  * Note: if no lights – immediately turn off power and troubleshoot
1. Replace bottom plate cover onto cable enclosure
1. Begin login process for testing checkout



# Login

1. Open Telnet / SSH session
  * Ip Address (wireless): 192.168.128.250
  * Ip Address (wired): 192.168.128.251

Instructions fer setting up wifi:
https://help.ubuntu.com/community/WifiDocs/WiFiHowTo

```sh
sudo /etc/init.d/networking stop
sudo /etc/init.d/networking start
```


## Start Up

1. Power up the BeagleBoard
2. Begin pinging the IP address of the BeagleBoard to determine when
   up.  (Currently: 192.168.128.250)
3. Connect via SSH to BeagleBoard
4. Login as root user
  * Username: root
  * Password: psaslv1b 
5. Start the Phidget web service (verbose)
  * Because verbose flag any additional root control will require a
    separate SSH connection
  * /phidgetwebservice/phidgetwebservice21 -v
6. Start launch tower computer software



# Common Commands

Reboot Computer Instantly:
        # reboot –t now

Turn off computer instantly:
        # poweroff –t now

View IP Addresses assigned to interfaces:
        # ip address show



# Internal Connections


## PowerPole Connection

![PowerPole Connection](diagrams/Powerpole_Connection.png)


## Umbilical Connection

![Umbilical Connection](diagrams/Umbilical_Connection.png)


## Phidgets

![Phidgets](diagrams/Phidgets.png)



# Internal Routing

## LTC Connections Schematic

![LTC Connections Schematic](diagrams/LTC_connections_schematic.png)



# Bottom Bulkhead

![Bottom Bulkhead](diagrams/Bottom_Bulkhead.png)



# Side Bulkhead

![Side Bulkhead](diagrams/Side_Bulkhead.png)
