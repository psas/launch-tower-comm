# DHCP Server on the Beaglebone

In order to set a static ip address for devices connecting over ethernet, the beaglebone has [dnsmasq](https://thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html) installed on it.

The config file for dnsmasq is located at `/etc/dnsmasq.conf`

The key changes to make this work are as follows:

- `interface=eth0` *Set the interface for the server to eth0*
- `bind-interfaces` *Required so that it always binds on connection, otherwise you have to do it manually*
- `dhcp-range=10.0.0.100, 10.0.0.200,infinite` *Enables the DHCP server and sets the range of ip addrs it will give out, and the length of time they are valid*

