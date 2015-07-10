---
title: Fortigate - source routing + WAN failover
authors: Romain Guichard
about_author: Romain Guichard est ingenieur cloud @Osones
email: rguichard@vsense.fr
slug: fortigate-source-routing-wan-failover
date_published: 2015-03-24T11:48:00.000Z
date_updated:   2015-06-28T17:19:21.000Z
tags: failover, fortigate, fortinet, pbr, Routage
---

Quand on dispose d’une petite infrastructure on est parfois limité par notre matériel pour obtenir une résilience suffisante.

Imaginons un Fortigate sur lequel arrive deux accès Internet via deux liaisons DSL, une route par défaut sur chacun d’entre eux. Dans une optique de « QoS » on souhaite dédier une des liaisons DSL (wan2) pour un serveur (172.16.1.152) et laisser le reste du trafic s’écouler par la deuxième liaison (wan1). Dans le cas où une des deux liaisons tomberaient, on veut que le trafic bascule automatiquement sur la liaison en état de marche.

Dans la table de routage du firewall on aura normalement deux routes par défaut comme ceci :

[![route](http://res.cloudinary.com/vsense/image/upload/v1435508358/route1_v4q4ki.png)](http://res.cloudinary.com/vsense/image/upload/v1435508358/route1_v4q4ki.png)

Avec des métriques identiques, le comportement normal sera un load balancing entre wan1 et wan2.

Mais la volonté de « QoS » nous oblige à utiliser du policy-based routing. Problème, une règle de PBR est prioritaire par rapport à une route. Pour cela nous allons créer une règle de PBR sans passerelle, seulement en précisant une interface de sortie.

[![pbr](http://res.cloudinary.com/vsense/image/upload/v1435508361/pbr_vpj9qt.png)](http://res.cloudinary.com/vsense/image/upload/v1435508361/pbr_vpj9qt.png)

La règle doit matcher tout le trafic de 172.16.1.152 (donc destination 0.0.0.0/0).

De cette façon le trafic en provenance de 172.16.1.152 va emprunter la route par défaut associée à l’interface Outgoing de la PBR (wan2), 10.0.200.1 dans notre cas.

Pour obtenir l’effet failover, il faut ensuite créer une deuxième PBR pour le même objet mais en changeant l’interface d’Outgoing. [![pbr2](http://res.cloudinary.com/vsense/image/upload/v1435508357/pbr21_y3bpcl.png)](http://res.cloudinary.com/vsense/image/upload/v1435508357/pbr21_y3bpcl.png)L’ordre est ce qui détermine les priorités, il faut donc faire attention à bien positionner la PBR « vers wan2″ avant celle « vers wan1″.

Ainsi avec deux PBR et deux routes par défaut, le trafic va emprunter en priorité la route par défaut associée à l’interface Outgoing de la première PBR. Si l’interface tombe et que la route par défaut n’est plus présent dans la table de routage, la première PBR ne sera plus matchée et le trafic s’acheminera par la deuxième route par défaut matchant la deuxième PBR.

On a de cette manière réussie à orienter nos flux vers les sorties que l’on voulait et en même temps permis à ces flux de basculer en cas de perte d’un lien.
