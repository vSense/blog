---
title: OVH Architecture
slug: ovh-architecture
date_published: 2013-03-24T18:18:12.000Z
date_updated:   2014-08-28T23:41:25.000Z
tags: ESX, ESX, ESXi, ESXi, Kimsufi, Kimsufi, OVH, OVH, VMware, VMware, Vyatta, Vyatta
---


For this first article, we are going to talk about our new server at OVH, we acquired a Kimsufi 16G which is equivalent to the KS2 in the USA. We’are aiming at using this server for hosting our personal apps (Minecraft, Subsonic, blog, seedbox, VPS) and also for testing purposes. So we installed ESXi 5, why ? Because ESXi is free, easy to manage and works well, as good as KVM or XEN, maybe better and it is more separated than OpenVZ, even if some of my open source nazis friends would like to differ. The installation is done via the OVH manager and takes about 20 minutes. After that, we need to login the ESXi public IP provided by OVH.VMware offers free license with basic features for ESXi 5 which is enough for a single host without shared storage.

What now ? because for now you only have 1 public IP and it is bind to the ESXi Management. You need to purchase some failover IP, at least one if you want to be able to bridge a VM onto the WAN. At OVH, you can buy 2 failover and then, if you want more, you need to buy IP from the RIPE. Each IP needs to be associated with a specific MAC address in the OVH manager.

Once you have purchase and set up your IP, we can start doing some configuration:


## Virtual Machine Management

Vocabulary:

- pNIC: Physical Network Card
- VM: Virtual Machine
- vNIC: Virtual Network Adapter
- vSwitch: Virtual switch where virtual machines are connected
- Port group: Group of port on a vswitch, can be compare to a VLAN

We split our network in 2: LAN and WAN. We chose [Vyatta](http://www.vyatta.org/ "Vyatta") for routing and firewalling. We placed services which does not require direct access to the internet into the LAN, on the WAN, we have the firewall and some personal servers.


## Gérer les IPs publiques:

One of the downside of VMware, compared to others hypervisors is that with only one IP, we cannot do anything. We need more IPs and a router.

Routing will be assured by Vyatta which is an OS based on Debian with the Quagga suit. Its CLI is very cool and familiar when you have already worked on Juniper or Cisco hardware. Vyatta will be sort of bridged on our only physical NIC onto the OVH network but we need a failover IP for it.

Advantages of virtualisation is that you can split your service on a virtual machines basis, mainly based on the RAM used by a services. But we’are not gonna give a public IPv4 at each virtual machine ($$$ Buying from RIPE is expansive). We are going to use NAT/PAT to give access to the internet to our virtual machines. After that, you can use all sorts of proxy to redistribute your services (mostly web proxy). Also every machine has a routable IPv6 address but who uses ipv6 ? :p

OVH gives a [bridging guide](http://guide.ovh.com/BridgeClient "Bridging Guide"). We need to associate a specific mac address to one of our failover IPs. Then we give this mac-address to our virtual machine. If you split your failover subnet (for example we had a /30 that we split into 4 /32) you need to give a /32 ip address to the machine. The default gateway will be the same as the ESXi (OVH Gateway are on /24 network and are in .254). Problem is the gateway is not on the same subnet so you will need to declare an interface route. After that you should be able to access the internet.

We adapted the guide to work with Vyatta:

interfaces {    ethernet eth1 {       address 10.0.10.254/24       description LAN       duplex auto    }    ethernet eth2 {       address 46.x.x.123/32       description WAN       duplex auto    } } protocols {    static {       interface-route 91.y.y.254/32 {          next-hop-interface eth2 {          }       }    } } system {    gateway-address 91.y.y.254 }

It was working OK for a while but we received an email from OVH telling us to stop ARPing all of the time. In fact an ARP request was issued for every IPs Vyatta tried to contact:

Wed Jun 20 22:21:45 2012 : arp who-has 46.102.50.20 tell 46.x.x.123 Wed Jun 20 22:27:08 2012 : arp who-has 212.194.27.120 tell 46.x.x.123 Wed Jun 20 22:27:27 2012 : arp who-has 159.253.152.251 tell 46.x.x.123 Wed Jun 20 22:34:10 2012 : arp who-has 83.152.137.175 tell 46.x.x.123 Wed Jun 20 22:55:47 2012 : arp who-has 8.8.8.8 tell 46.x.x.123 Wed Jun 20 22:56:23 2012 : arp who-has 178.162.149.42 tell 46.x.x.123 Wed Jun 20 22:56:29 2012 : arp who-has 173.194.35.191 tell 46.x.x.123 Wed Jun 20 22:56:32 2012 : arp who-has 50.22.155.163 tell 46.x.x.123 Wed Jun 20 22:56:33 2012 : arp who-has 98.111.131.98 tell 46.x.x.123 Wed Jun 20 22:56:33 2012 : arp who-has 66.241.101.63 tell 46.x.x.123

Vyatta included in its ARP table every IP contacted (associated with the gateway) but no trace of the gateway. Even with manual entry in the ARP table, Vyatta kept sending request.

This bug is due to this part of the configuration :

protocols {     static {        interface-route 91.y.y.254/32 {           next-hop-interface eth2 {           }        }     }  }

It is a [Quagga bug](https://bugzilla.vyatta.com/show_bug.cgi?id=6974). One solution is to manually add routes via classic Linux commands such as ifconfig or route. Not that clean but it worked.

Remove the interface route:

vyatta@vyatta# delete protocoles interface-route 91.y.y.254/32

We are going to re-apply this command but with debian commands. You need to be logged as root to be able to issue this commands:

route add @**gateway** dev eth2 route add default gw @**gateway**

It is the same principle as before, here is the routing table obtained:

vyatta@vyatta:~$ ip route default via 94.23.6.254 dev eth2 94.23.6.254 dev eth2  scope link

Obviously, this is a configuration which will no longer exist after a reboot. You need to apply this configuration juste after your system boot.

Thank you fo your attention on this first article.


## 



