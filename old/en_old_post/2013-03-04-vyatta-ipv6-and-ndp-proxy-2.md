---
title: Vyatta IPv6 and NDP proxy
slug: vyatta-ipv6-and-ndp-proxy-2
date_published: 2013-03-04T22:09:24.000Z
date_updated:   2014-09-02T19:06:28.000Z
tags: IPv6, IPv6, NDP, NDP, ndppd, ndppd, OVH, OVH, Proxy, Proxy, Vyatta, Vyatta
---


We use Vyatta on our OVH dedicated server to manage firewalling and routing and let me just say that OVH documentation is quite poor regarding IPv6 configuration. This article is not only about OVH but about all the services providers that give you an IPv6 subnet but want to see it flatten. This means that if your service provider does not use RIP or OSPF for example and therefore you cannot split your subnet in several smaller subnets. So what do I do because I really want to split my subnet because it’s cool and clean ? This where the Neighbor Discovery Protocol is going to be useful, it is pretty much like ARP for IPv6 and it is going to advertise its neighbors about your different IPv6 subnets.

Let’s say we want to split our network like this:

.----------. 2001:2:3:4500::/64 .---------------. | IPv6 |______________________| dedicated | | Router | eth0| server | *----------* *---------------* veth1 | | veth2 | | 2001:2:3:4500:1000:/80 | | 2001:2:3:4500:1:/80 | | eth0 | | eth0 [VM 1] [VM 2]

The OVH Gateway is 2001:2:3:45ff:ff:ff:ff:ff and our interfaces are configured as such:

Interface IP Address S/L Description --------- ---------- --- ----------- eth1 X.X.X.254/24 u/u LAN 2001:X:X:4500:1000:254/80 eth2 X.X.X.X/32 u/u WAN 2001:2:3:4500::1/64

Configuration of the default gateway:

configure set protocol static route6 ::/0 next-hop next-hop 2001:X:X:07ff:ff:ff:ff:ff commit

[Goretsoft](ftp://ftp.goretsoft.net/ "Goretsoft") is a repository that provided some packages that enhanced Vyatta with some features not yet implemented. We also need to install Debian repository because some of Goretsoft packages depend on it. DO NOT mess around with the Debian repo (I did and broke some parts of Vyatta), no apt-get upgrade, dist-upgrade etc, some packages might work though but it is totally up to you.

Add Debian and Goretsoft repository:

set system package repository debian components main contrib set system package repository debian distribution squeeze set system package repository debian url [http://mirrors.kernel.org/debian ](http://mirrors.kernel.org/debian)set system package repository debian components main set system package repository debian distribution pacifica set system package repository debian url ftp://ftp.goretsoft.net/vyatta commit save

As root:

apt-get update && apt-get install vyatta-cfg-quagga vyatta-cfg-op-pptp-client ndppd

The installation of vyatta-cfg-op-pptp client is mandatory as it would break some node.def files into Vyatta and crash the config loader at boot giving you an empty config file at each reboot not to install it. In fact vyatta-cfg-quagga modifies some node.def files giving you extra CLI commands. I’m not an expert on how Vyatta’s node.def system works but trust me and install the pptp-client.

Once the installation is done, you can access the x-proxyndp feature, we are going to tell the LAN network where the gateway is:

set protocol static x-proxyndp static 2001:41d0:2:7FF:FF:FF:FF:FF eth1 (Interface LAN)

Then we are going to announce on the WAN interface that our split subnets are here.

set protocols static x-proxyndp daemon proxy eth2 rule 2001:41d0:2:701:XXXX::/80 method auto commit

That’s pretty much it, with this 2 lines, you got a working NDP proxy, you can know assign your 1,84467440737096E19 IPs regardless of the routing protocols used by your provider (in our case none ![:)](http://blog.vsense.fr/wp-includes/images/smilies/simple-smile.png) )



