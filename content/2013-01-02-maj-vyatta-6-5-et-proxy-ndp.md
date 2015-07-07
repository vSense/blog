---
title: MAJ Vyatta 6.5 et Proxy NDP
authors: Romain Guichard, Kevin Lefevre
slug: maj-vyatta-6-5-et-proxy-ndp
date_published: 2013-01-01T23:22:49.000Z
date_updated:   2014-09-02T19:07:39.000Z
tags: IPv6, NDP, ndppd, OVH, Vyatta
---


**Update :** Lundi 4 Mars 2013: L’installation de paquets manuellement du repo Goretsoft casse le chargement de la configuration Vyatta au demarrage. Pour résoudre le problème, utiliser la nouvelle methode suivante.

Avec la sortie de Vyatta 6.5, je me suis penché sur les différentes améliorations apportées en matière d’IPv6 et… toujours pas de Proxy NDP mais je suis tombé sur le repo [Goretsoft](ftp://213.41.245.21/vyatta/dists/pacifica/main/index.html "Goretsoft Repo") qui proposent plusieurs packages adaptés à Vyatta 6.5 Pacifica. Petit rappel, si vous avez lu [l’article précédent sur le proxy NDP](http://blog.vsense.fr/configuration-et-routage-son-score-ipv6-ovh-avec-vyatta/ "Configuration et routage de son scope IPv6 avec Vyatta"), on voit que la solution proposée est vite lourde lorsque l’on commence à avoir beaucoup d’adresses IP à inscrire statiquement. Si vous ne l’avez pas lu, je vous invite à le lire quand même pour comprendre un peu la nécessité du proxy NDP dans le cadre d’un réseau IPv6 par exemple chez OVH ou chez Free.

Si vous n’avez toujours pas envie de le lire je vais résumer : OVH distribue un /64 pour les serveurs dédiés. Un des problèmes rencontré est que OVH veut voir ce /64 à plat, c’est à dire que vous êtes obligés de bridger vos VMs directement sur le réseau d’OVH, vous ne pouvez pas le router en théorie et donc créer plusieurs sous-réseaux IPv6. Une solution est d’utiliser un proxy NDP (Neighbor Discovery Protocol) qui peut être considéré comme un équivalent à l’ARP mais pour IPv6.

Nous voulons justement splitter ce /64 en un ou plusieurs /80 comme sur ce schéma de [linux-attitude ](http://linux-attitude.fr/ "LA") qui discutaient également du proxy NDP dans [cet article](http://linux-attitude.fr/post/proxy-ndp-ipv6).
```
.----------. 2001:2:3:4500::/64   .---------------.
| routeur  |______________________|    serveur    |
|   IPv6   |                  eth0|     dédié     |
*----------*                      *---------------*
                                veth1 |        | veth2
                                      |        |
                   2001:2:3:4500:1000:/80 |        | 2001:2:3:4500:1:/80
                                      |        |
                                 eth0 |        | eth0
                                    [VM 1]   [VM 2]
```

Comme je le disais la solution proposée dans le précédent article était centralisée (pas besoin d’annoncer les neighbors sur chaque machine) mais nous devions tout de même rentrer les IP manuellement sur le Vyatta. C’est la que [ndppd](http://priv.nu/projects/ndppd/ "ndppd") entre en jeu, je vous invite à lire la description du projet mais pour résumer, cela permet d’annoncer un subnet, dans notre cas notre scope /80 pris dans notre /64 alloué par OVH, au lieu de devoir entrer manuellement les IP.

Ajout du repository Goretsoft et Debian:

```
set system package repository debian components main contrib set system package repository debian distribution squeeze set system package repository debian url [http://mirrors.kernel.org/debian ](http://mirrors.kernel.org/debian)set system package repository debian components main set system package repository debian distribution pacifica set system package repository debian url ftp://ftp.goretsoft.net/vyatta commit save
```
Et maintenant en root:

`apt-get update && apt-get install vyatta-cfg-quagga vyatta-cfg-op-pptp-client ndppd`

L’installation du client pptp est necessaire pour ne pas casser le chargement de la configuration au reboot de Vyatta car le package vyatta-cfg-quagga modifie les node.def pour prendre en compte le proxy ndp ainsi que le client pptp. Si le paquet pptp n’est pas installé, le chargement de la configuration échoue au demarrage et on se retrouve avec une config vide.

Une fois ces étapes effectuées on accède au menu x-proxyndp. On va annoncer sur l’interface eth1 (qui correspond au LAN dans notre cas) que la passerelle est par ici :

`set protocol static x-proxyndp static 2001:41d0:2:7FF:FF:FF:FF:FF eth1 (Interface LAN)`

Jusque ici la déclaration est toujours statique. Ensuite, nous allons déclarer le subnet qui correspond à notre réseau IPv6 interne en /64 sur l’interface WAN:

`set protocols static x-proxyndp daemon proxy eth2 rule 2001:41d0:2:701:XXXX::/80 method auto commit`

C’est tout, avec ces 2 lignes,vous avez votre proxy NDP fonctionnel, vous pouvez maintenant mettre vos 1,84467440737096E19 IPs sur des machines sans vous souciez de les rentrer manuellement dans le proxy NDP.
