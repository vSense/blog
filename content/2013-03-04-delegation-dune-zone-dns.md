---
title: Délégation d'une zone DNS
slug: delegation-dune-zone-dns
authors: Romain Guichard
about_author: Romain Guichard est ingenieur cloud @Osones
email: rguichard@vsense.fr
date_published: 2013-03-04T22:41:03.000Z
date_updated:   2014-09-02T19:05:43.000Z
tags: bind, DNS, zones, delegation, sous-zone
category: Système
---


Lorsque l’on possède un domaine, on aime bien pouvoir être indépendant de son registrar pour gérer sa zone DNS. En effet certains proposent bien une interface web permettant d’ajouter des enregistrements de type A ou CNAME, parfois MX, mais bien peu offrent la possibilité d’ajouter des enregistrements NS.

Or ceux ci sont indispensables si vous souhaitez créer des sous-domaines à partir de votre domaine principal. Et parfois ceux si sont limités en nombre par votre registrar, alors que bon c’est juste quelques lignes en plus dans quelques fichiers…

Nous allons voir ici comment déléguer une sous-zone DNS avec BIND. La délégation peut être attribuée au même serveur NS, ça ne pose pas de problème.
```
### **named.conf**

Ce fichier est le plus simple à configurer, la délégation n’ajoute pas de supplément, vous déclarer juste une nouvelle zone.

zone "france.fr" {        
    type master;        
    file "/etc/bind/france.fr.zone";        
    allow-transfer { 5.6.7.8; };
};

zone "paris.france.fr" {        
    type master;        
    file "/etc/bind/paris.france.fr.zone";        
    allow-transfer { 5.6.7.8; };
};

Voilà, rien de bien particulier. J’ai choisi ici de déléguer la zone paris au même serveur gérant la zone france. Il est intéressant de déléguer votre zone paris à un autre serveur NS car votre serveur gérant la zone france peut ainsi devenir par la même occasion serveur slave du domaine paris. Une pierre deux coups. Bon ici on va supposer qu’il existe un serveur slave qui gère le domaine et le sous-domaine.
```

```
### **La zone france.fr**

$TTL    604800 $ORIGIN france.fr.
@       IN      SOA     ns1.france.fr. admin.france.fr. (                     

    2012082300          ; Serial
    3600                ; Refresh
    3000                ; Retry
    4619200             ; Expire                         
    604800 )            ; Negative Cache TTL

; Hosts
@               IN      NS      ns1
@               IN      NS      ns2
ns1             IN      A       1.2.3.4
ns1             IN      AAAA    2001::1
ns2             IN      A       5.6.7.8
ns2             IN      AAAA    2001::2

; Subzones $ORIGIN paris.france.fr.
@                           IN      NS      ns1.paris.france.fr.
@                           IN      NS      ns2.paris.france.fr.
ns1.paris.france.fr.        IN      A       1.2.3.4 ; Cette IP n'est pas nécessairement la même que ns1.france.fr
ns1.paris.france.fr.        IN      AAAA    2001::1
ns2.paris.france.fr.        IN      A       1.2.3.4 ; Pareil que pour ns1
ns2.paris.france.fr.        IN      AAAA    2001::2
```

Plusieurs choses ici. La partie sur les hosts de france.fr n’a rien de particulier. La variable ORIGIN n’a pas à être nécessairement déclarée (la RFC dit peut être le contraire mais bon…) mais elle reste importante par la suite.

La partie sur les subzones est celle nous permettant d’effectuer cette délégation. Nous redéfinissons dans un premier temps la variable ORIGIN pour le sous-domaine. Cela permet d’utiliser le symbole @. Puis nous effectuons un enregistrement de type GLUE, on défini les serveurs NS du sous-domaine, puis on donne une adresse IP à ces serveurs.

Il nous reste maintenant à construire notre zone paris.france.fr dans lequel on défini simplement les NS du domaine.

```
### **La zone paris.france.fr**

$TTL    604800
$ORIGIN paris.france.fr.
@       IN      SOA     ns1.paris.france.fr. admin.paris.france.fr. (                     
    2012082300          ; Serial                           
    3600                ; Refresh                           
    3000                ; Retry                        
    4619200             ; Expire                         
    604800 )            ; Negative Cache TTL

; Hôtes
@               IN      NS      ns1
@               IN      NS      ns2
ns1             IN      A      1.2.3.4
ns1             IN      AAAA    2001::1
ns2             IN      A       5.6.7.8
ns2             IN      AAAA    2001::2
```

On teste rapidement le fichier named.conf et les fichiers de zone pour voir si on a pas fait de fautes de frappe, on recharge la configuration de BIND, et voilà !
