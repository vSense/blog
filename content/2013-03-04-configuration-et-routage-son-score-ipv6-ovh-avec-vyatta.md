---
title: Configuration et routage de son scope IPv6 avec Vyatta
authors: Romain Guichard, Kevin Lefevre
slug: configuration-et-routage-son-score-ipv6-ovh-avec-vyatta
date_published: 2013-03-04T22:09:24.000Z
date_updated:   2014-08-31T12:17:04.000Z
tags: IPv6, NDP, ndppd, OVH, Proxy, Vyatta
---


Attention, cet article est obsolète, ayant discuté avec OVH, il semblerait que même si l’on peut utiliser le /56. C’est bien seulement un /64 qui est officiellement délégué par serveur dédié. Si l’on veut par exemple administrer sa propre zone DNS inverse IPv6, il faut redécouper ses IPs à partir du /64 fourni par OVH.  En ce qui concerne le proxyNDP, nouvelle methode plus propre et plus à jour, c’est disponible [ici](http://blog.vsense.fr/maj-vyatta-6-5-et-proxy-ndp/ "MAJ Vyatta 6.5 et Proxy NDP").

Nous utilisons Vyatta pour gérer les VM sur notre Kimsufi chez OVH, Romain à présenté Vyatta dans un billet précèdent. Je vais vous parler un peu de l’IPv6, [la documentation](http://guides.ovh.com/Ipv4Ipv6) d’OVH sur le sujet est pauvre et comment dire… relativement erronée. OVH distribue un /64, un des problèmes rencontré est que OVH veut voir ce /64 à plat, c’est à dire que vous êtes obligés de bridger vos VM directement sur le réseau d’OVH, vous ne pouvez pas le router en théorie et donc créer plusieurs sous-réseaux IPv6. Une solution est d’utiliser un proxy NDP (Neighbor Discovery Protocol) qui peut être considéré comme un équivalent à l’ARP mais pour IPv6.

Nous avons par exemple le scope suivant: 2001:X:X:700::/64

La passerelle OVH est : `2001:X:X:7ff:ff:ff:ff:ff`

Les interfaces sur le Vyatta son configurées de la façon suivante:

```
Interface IP Address S/L Description
--------- ---------- --- -----------
eth1 X.X.X.254/24 u/u LAN
2001:X:X:701:1000:1/80
eth2 X.X.X.X/32 u/u WAN
2001:X:X:700::2/56
```

On configure la route par défaut IPv6:

`configure set protocol static route6 ::/0 next-hop next-hop 2001:X:X:07ff:ff:ff:ff:ff commit`

Le proxy NDP n’est pas officiellement implémenté dans Vyatta, contrairement à d’autres distributions Linux mais un [patch](http://intarweb.goretsoft.net/tmp/proxyndp.patch) est disponible sur le [forum](http://www.vyatta.org/forum/viewtopic.php?t=6061&sid=86907912bc79caac0a22f9e676b76a71) Vyatta. Pour appliquer le patch:

`diff -p1 < proxyndp.patch`

Il faut ensuite annoncer sur l’interface LAN: on va indiquer que la passerelle IPv6 est ici :

`set protocol static x-proxyndp 2001:X:X:7FF:FF:FF:FF:FF eth1 (Interface LAN)`

L’inconvénient est qu’il faut déclarer toutes les IPv6 du LAN également mais cette fois ci sur l’interface WAN:

`set protocol static x-proxyndp 2001:X:X:701::01 eth2 (Interface WAN) set protocol static x-proxyndp 2001:X:X:701::02 eth2 (Interface WAN) etc....`

Vous avez compris le principe ? Si vous avez beaucoup de machines, cette méthode peut vite devenir épuisante, il est surement possible de réaliser un script en liaison avec soit un dhcpv6 soit radvd, à voir….

Pour les machines configurées en IPv6, l’adresse de passerelle ne correspond pas à l’adresse IPv6 configurée sur l’interface du Vyatta mais bien à celle de la passerelle d’OVH. Le proxy NDP fait croire au routeur que les machines sont présentes sur le même lien. C’est une solution temporaire en attendant qu’OVH propose une solution ou rétablisse l’OSPF qui a disparu pour raison inconnue...
