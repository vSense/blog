---
title: Domain name delegation and subdomains
slug: domain-name-delegation-and-subdomains
date_published: 2013-03-04T22:41:03.000Z
date_updated:   2014-04-14T16:20:46.000Z
tags: Bind, Bind, DNS, DNS, subdomain
---


When you own a domain name, you would maybe like to be independent from your registrar and handle your DNS zone by yourself. Lots of them offer a web interface to manage your A or CNAME records but only a few allow you to manage your MX and NS records.

NS records are essentials if you wish to create subdomains from your main domain, those subdomains are often limited by your provider even if it just a few lines more to a config file.

We are going to see how to handle a DNS zone with BIND:

### **named.conf**

This file is quite simple to configure, we just declare the new zone and its location, the « allow-tranfer » are for allowing zone transfer from your primary to your secondary name server if you have one.

zone "france.fr" {         type master;         file "/etc/bind/france.fr.zone";         allow-transfer { 5.6.7.8; }; }; zone "paris.france.fr" {         type master;         file "/etc/bind/paris.france.fr.zone";         allow-transfer { 5.6.7.8; }; };

Here, we delegate those two zones to the same server but we could have put the « Paris » zone onto another server to offload the « France » server for example. It is up to you. Here we are going to assume that we have one primary server which managed the « Paris » and « France » zones and a secondary server where the zones are replicated.

### **france.fr zone**

$TTL    604800 $ORIGIN france.fr. @       IN      SOA     ns1.france.fr. admin.france.fr. (                      2012082300         ; Serial                            3600         ; Refresh                            3000         ; Retry                         4619200         ; Expire                          604800 )       ; Negative Cache TTL ; ; Hosts @               IN      NS      ns1 @               IN      NS      ns2 ns1             IN      A       1.2.3.4 ns1             IN      AAAA    2001::1 ns2             IN      A       5.6.7.8 ns2             IN      AAAA    2001::2 ; Subzones $ORIGIN paris.france.fr. @                           IN      NS      ns1.paris.france.fr. @                           IN      NS      ns2.paris.france.fr. ns1.paris.france.fr.        IN      A       1.2.3.4 ; not necessarily the same as ns1.france.fr ns1.paris.france.fr.        IN      AAAA    2001::1 ns2.paris.france.fr.        IN      A       1.2.3.4 ; same as ns1 ns2.paris.france.fr.        IN      AAAA    2001::2

The part about the « france.fr » hosts has nothing particular. The ORIGIN variable does not need to be declared (though the RFC might say something different ![:)](http://blog.vsense.fr/wp-includes/images/smilies/simple-smile.png) ) but it is still important for the next part.

The subzone part allows us to do the delegation. We redefine the ORIGIN variable with the subdomain name which permits the use of the @ symbol. Then, we make a GLUE record: we define the NS server for the subdomain and we give them an IP address.

Now we have to build the « paris.france.fr » zone in which we simply define the NS for the subdomain.

### **La zone paris.france.fr**

$TTL    604800 $ORIGIN paris.france.fr. @       IN      SOA     ns1.paris.france.fr. admin.paris.france.fr. (                      2012082300         ; Serial                            3600         ; Refresh                            3000         ; Retry                         4619200         ; Expire                          604800 )       ; Negative Cache TTL ; ; Hôtes @               IN      NS      ns1 @               IN      NS ns2 ns1             IN      A      1.2.3.4 ns1         IN      AAAA    2001::1 ns2            IN      A       5.6.7.8 ns2       IN      AAAA    2001::2

After that, you can check your BIND configuration with named-checkconf and named-checkzone and the reload the configuration and voila !



