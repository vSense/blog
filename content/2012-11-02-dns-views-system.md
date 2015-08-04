---
title: DNS - Multiples Views
slug: dns-views
lang: en
date_published: 2012-11-02T01:05:51.000Z
date_updated:   2014-04-14T16:21:19.000Z
tags: Bind, Bind, debian, debian, DNS, DNS, domain, views
Status: draft
---


When you have many servers in your LAN reachable from the Internet (NAT/PAT), it’s important that your DNS server provides the good server IP. If a customer requests your web server IP and your DNS gives its LAN IP back, your customer will be disappointed. You must adapt your response according to the source of the request.

You could use two different DNS server to solve this problem: one for your LAN and another one for requests from the Internet. But this isn’t very practical and better solutions exist.

We are gonna use a system of views, there is one zone file for your LAN and another one for the WAN. That’s two different views, one we’ll call « internal » and the other one « external ». When a local client send a query, the server will give an answer from the internal zone file but when it’s a unknown host which sends the query, the answer will be given from the external zone file. Let’s have a look at the named.conf:

#Define the LAN acl "lan_hosts" {         10.0.0.0/24;         127.0.0.1; }; #Define the WAN acl "wan_hosts" {         any; }; view "internal"{ match-clients{ lan_hosts; }; recursion yes; //Recursion is allowed for LAN host         zone "vsense.fr" {                 type master;                 file "/etc/bind/internal/vsense.fr.zone";         };         zone "10.0.0.in-addr.arpa" {                 type master;                 file "/etc/bind/internal/10.0.0.in-addr.arpa.zone";         }; }; view "external"{ match-clients { wan_hosts; }; allow-recursion {wan_hosts;}; //Recursion is allowed only for some specifics host on the Internet         zone "vsense.fr" {                 type master;                 file "/etc/bind/external/vsense.fr.zone";         }; };

ACLs are a simple way for matching client’s request sent to our server. You can give your private network for example. BE CAREFUL, it’s ACL, the order is important ! It’s the same for the views, you have to declare you’re internal view before your external one. You always go from the more specific to the more general (makes sense as your external view is sort of you default behavior). After creating the ACLs, you’re going to create the views and inside each views we’re gonna put the corresponding ACL.

The « allow-recursion » allows client to use our server as a primary DNS and use it to resolve domain name on which we do not have authority. Of course we allow this only for specific hosts, the others can only resolve the domain name « vsense.fr ».

Now we can use the same DNS server which we’ll give us different answers depending on our location. For example if I’m connected by openVPN and I want to ssh to say my DNS server i’ll have a private IP for answser but if i’m at home without VPN, il’ll have the Firewall or proxy public IP.



