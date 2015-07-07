---
title: Vyatta OpenVPN
slug: vyatta-openvpn
date_published: 2013-04-01T17:19:39.000Z
date_updated:   2015-06-28T17:20:20.000Z
tags: OpenVPN, OpenVPN, OVH, OVH, Vyatta, Vyatta
---


Before going at OVH we had some servers at Virpus, an American hosting service based in Houston, Texas. We had a VPN there to bypass some country restrictions but at 300ms latency,not ideal for downloading or other services than web. Now our servers are in France and it is another story.

VPN have mainly two purpuses. Either interconnect 2 remote networks, or to connect remote clients to a network and by extension provide (possibly) more secure access to some services. In our case, we can bypass some limitations that we have in school for example (port filtered, protocols filtered, every non « standard » traffic).

OpenVPN propose virtual appliance but it is also well integrated into Vyatta, the router we use. It can function as a Client/Server or Site-to-Site OpenVPN. We can create OpenVPN interfaces easily via Vyatta CLI, not all the options are implemented but we can add them manually via customs arguments.

Lets have a look at the network :

<div class="wp-caption aligncenter" id="attachment_140" style="width: 310px">[![openvpn](http://res.cloudinary.com/vsense/image/upload/h_204,w_300/v1435508420/openvpn1_yu0vn1.png "openvpn")](http://blog.vsense.fr/wp-content/uploads/2012/07/openvpn.png)OpenVPN tunnel in blue

</div>Vyatta is our OpenVPN server and each client establish a remote connexion with it. We allocate IP address via DHCP-server also via Vyatta.

Our OpenVPN options are the following:

- Protocole : TCP (cause UDP maybe block, like in our school)
- Port : 1863 (used by MSN, often open, else use a port that you know is open)
- Hash : SHA1
- Cypher : AES256
- comp-lzo

Vyatta configuration :

openvpn vtun0 {         description TUNNEL-VPN         encryption aes256         hash sha1         local-port 1863         mode server         openvpn-option --comp-lzo         protocol tcp-passive         replace-default-route {         }         server {                   subnet 10.0.1.0/24             topology subnet         }         tls {             ca-cert-file /config/auth/ca.crt             cert-file /config/auth/vyatta.crt             dh-file /config/auth/dh1024.pem             key-file /config/auth/vyatta.key         }     }

You need of course valid certificate to do that. Check the internet on how to quickly create a PKI with easy-rsa for example.

The parameter *replace-default-route *tell the client to use the end-tunnel IP as default gateway to route all internet traffic inside the tunnel. After that, we access the internet with Vyatta public IP.

To check if OpenVPN is running correctly, you can check the /var/log/message for:

Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: Diffie-Hellman initialized with 1024 bit key Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: /usr/bin/openssl-vulnkey -q -b 1024 -m <modulus omitted> Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: TLS-Auth MTU parms [ L:1560 D:140 EF:40 EB:0 ET:0 EL:0 ] Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: Socket Buffers: R=[87380->131072] S=[16384->131072] Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: TUN/TAP device vtun0 opened Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: TUN/TAP TX queue length set to 100 Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: /sbin/ifconfig vtun0 10.0.1.1 netmask 255.255.255.0 mtu 1500 broadcast 10.0.42.255 Jul 25 03:09:48 vyatta zebra[1709]: interface vtun0 index 9 <POINTOPOINT,NOARP,MULTICAST> added. Jul 25 03:09:48 vyatta zebra[1709]: warning: PtP interface vtun0 with addr 10.0.1.1/32 needs a peer address Jul 25 03:09:48 vyatta zebra[1709]: interface vtun0 index 9 changed <UP,POINTOPOINT,RUNNING,NOARP,MULTICAST>. Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: Data Channel MTU parms [ L:1560 D:1450 EF:60 EB:135 ET:0 EL:0 AF:3/1 ] Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: Listening for incoming TCP connection on [undef] Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: TCPv4_SERVER link local (bound): [undef] Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: TCPv4_SERVER link remote: [undef] Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: MULTI: multi_init called, r=256 v=256 Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: IFCONFIG POOL: base=10.0.1.2 size=252 Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: MULTI: TCP INIT maxclients=1024 maxevents=1028 Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: **Initialization Sequence Completed**

Then you have to generated ovpn configuration file for your clients:

proto tcp-client tls-client remote 46.x.x.123 rport 1863 dev tun ca ca.crt cert romain.crt key romain.key cipher AES-256-CBC auth SHA1 comp-lzo verb 3 pull

Once the tunnel is up, check the routing table to see if everything is as it should be:

Destination réseau    Masque réseau  Adr. passerelle   Adr. interface Métrique           0.0.0.0          0.0.0.0        10.0.1.1        10.0.1.2     30

The default route is know Vyatta’s tunnel IP and our traffic is routed in the tunnel. There is one more thing to do to be able to access the internet: to NAT OpenVPN traffic to the WAN interface.

With a functional PKI, it is pretty simple to have OpenVPN working on Vyatta and secure your connexion for various purposes.

Enjoy ~.°



