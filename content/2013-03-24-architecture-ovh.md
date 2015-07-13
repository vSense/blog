---
title: Architecture OVH
authors: Romain Guichard, Kevin Lefevre
about_author: Romain et Kevin sont ingenieurs cloud @Osones
email: rguichard@vsense.fr - klefevre@vsense.fr
slug: architecture-ovh
date_published: 2013-03-24T18:18:12.000Z
date_updated:   2014-08-29T17:09:04.000Z
tags: ESXi, Kimsufi, OVH, VMware, Vyatta
category: Réseau
---


Pour ce tout premier billet, nous allons parler un peu de notre première et nouvelle architecture. Nous avons fait l’acquisition d’un Kimsufi 16G chez OVH. Nous comptons à la fois utiliser ce serveur pour accueillir nos applis persos (Minecraft, Subsonic, blog, seedbox…) ainsi que pour mettre à disposition de nos amis des VPS. Pour cela nous avons installé un ESXi5. Pourquoi un ESXi ? Parce que VMware ça marche bien, c’est possiblement gratuit et quoi qu’en disent nos copains libristes, ça tourne aussi bien, voir mieux qu’un Xen ou KVM et c’est plus compartimenté qu’un OpenVZ.

ESXi 5 n’est pas proposé par OVH lorsque vous achetez votre serveur. Il faut pour cela commander la version 4 et demander un changement d’OS dans le manager du dédié. La réinstallation prend environ 20 minutes.

## Gérer l’ESXi:

Après l’installation, il faut se connecter sur l’IP publique ou sur le site de VMware, pour télécharger le vSphere client qui permet de manager l’ESXi. La prise en main du client est simple et on comprend rapidement comment configurer l’ESXi et déployer des machines virtuelles.

Dans un premier temps, il faut une licence, celle-ci est distribuée gratuitement dans sa version standard sur le site de VMware ce qui devrait largement suffire.

Ensuite, il va falloir gérer le réseau à l’intérieur de l’ESXi, c’est ce point que nous allons détailler par la suite


## Management des machines virtuelles:

Vocabulaire:

- pNIC: Carte reseau physique
- VM: Virtual Machine
- vNIC: Carte reseau virtuelle associée à une machine virtuelle
- vSwitch: Switch virtuel sur lesquels seront connectés les vNIC des VMs
- Port group: Sous ensemble d’un vSwitch, peu s’apparenter à un VLAN et permet de compartimenter les VMs sur un vSwitch.

Nous avons segmenté le réseau en deux parties (LAN et WAN). Vyatta effectue le routage entre les deux.

Nous avons placé dans le LAN les services perso ne nécessitant pas vraiment de connectivité directe sur le WAN (on y accède par PAT) et sur le WAN uniquement les serveurs Web hébergés à cause notamment des problème de proxy.


# Gérer les IPs publiques:

Un des désavantages de VMware, comparé à d’autres hyperviseurs, c’est qu’avec une seule IP publique, on ne peut pas faire grand chose… Et nous n’avons pas de Nexus pour effectuer le routage « à notre place » *sigh*

Le routage est assuré par une distribution Vyatta. C’est un OS basé sur Debian qui assure toutes les fonctionnalités que vous retrouverez sur des équipements Cisco ou Juniper. Sa syntaxe est proche de celle de JUNOS. Vyatta est placé en bridge et nécessite donc une adresse IP publique, une première IP failover est commandée.

L’avantage d’un ESX est de ne pas être limité en nombre de machines, il est intéressant de pouvoir avoir une machine pour chaque service, la quantité de RAM disponible étant la seule contrainte. Mais donner une IP publique à chaque machine pose plusieurs problèmes. Tout d’abord les IPv4 étant un peu chères, nous souhaitions placer dans un LAN les machines qui pourraient se contenter d’un NAT/PAT sur un ou deux ports, renforcant ainsi leur sécurité. Nous prévoyons de mettre en place un reverse proxy de façon à garantir aux machines du LAN une écoute sur le port 80 par exemple et nous étudions un moyen de fournir un proxy SSH. Les autres machines disposeraient d’une IPv4 failover. Enfin toutes les machines disposeront d’une adresse IPv6, malheureusement IPv6 n’est pas encore suffisamment présent pour pouvoir s’en contenter.

La configuration d’une machine en bridge est détaillée dans [les guides OVH](http://guide.ovh.com/BridgeClient).

Dans les grandes lignes, il faut dans un premier temps associer, dans le manager OVH, une IP failover à une adresse MAC virtuelle qui sera utilisée par votre machine bridgée. Éditez ensuite la MAC de votre VM avec vSphere, votre VM doit être éteindre pour pouvoir modifier la MAC.
 La configuration réseau de la machine revient à donner l’IP failover en statique (avec un masque en /32) et à lui donner comme passerelle par défaut, la passerelle de votre serveur ESX. D’après OVH tous les dédiés ont l’air d’être dans des /24, les passerelles sont les dernières machines du réseau (.254). Le problème est que la passerelle ne se trouve pas sur le même subnet que notre VM bridgée, il faut donc préciser à votre machine sur quel port sortir pour atteindre la passerelle. A partir de là vous devriez avoir accès au net avec votre machine bridgée.

Les guides ne spécifient pas de méthode particulière pour Vyatta mais il nous suffit d’adapter les commandes. Voici la configuration (épurée) pour Vyatta :

```
interfaces {    
    ethernet eth1 {       
        address 10.0.10.254/24       
        description LAN       
        duplex auto   
    }    
    ethernet eth2 {       
        address 46.x.x.123/32       
        description WAN       
        duplex auto    
    }
}
protocols {    
    static {       
        interface-route 91.y.y.254/32 {          
            next-hop-interface eth2 {          
            }       
        }    
    }
}
system {    
    gateway-address 91.y.y.254
}
```

Cela fonctionnait bien. Mais nous avons reçu un mail d’OVH le lendemain nous informant que notre machine effectuait un nombre impressionnant de requêtes ARP. Une requête était en effet effectuée sur chaque IP que Vyatta contactait.

```
Wed Jun 20 22:21:45 2012 : arp who-has 46.102.50.20 tell 46.x.x.123
Wed Jun 20 22:27:08 2012 : arp who-has 212.194.27.120 tell 46.x.x.123
Wed Jun 20 22:27:27 2012 : arp who-has 159.253.152.251 tell 46.x.x.123
Wed Jun 20 22:34:10 2012 : arp who-has 83.152.137.175 tell 46.x.x.123
Wed Jun 20 22:55:47 2012 : arp who-has 8.8.8.8 tell 46.x.x.123
Wed Jun 20 22:56:23 2012 : arp who-has 178.162.149.42 tell 46.x.x.123
Wed Jun 20 22:56:29 2012 : arp who-has 173.194.35.191 tell 46.x.x.123
Wed Jun 20 22:56:32 2012 : arp who-has 50.22.155.163 tell 46.x.x.123
Wed Jun 20 22:56:33 2012 : arp who-has 98.111.131.98 tell 46.x.x.123
Wed Jun 20 22:56:33 2012 : arp who-has 66.241.101.63 tell 46.x.x.123
```

Hors du fait que ce comportement n’était absolument pas normal, Vyatta possédait dans sa table ARP une entrée pour chaque IP contactée, toutes associées à l’adresse MAC de sa passerelle. En revanche aucune trace de l’IP de la passerelle… Même en rentrant celle ci manuellement dans la table ARP, Vyatta persistait à vouloir requêter tous ses destinataires…

Ce bug est provoqué par cette partie de la configuration :
```
protocols {    
    static {       
        interface-route 91.y.y.254/32 {          
            next-hop-interface eth2 {          
            }       
        }    
    }  
}
```

Il s’est avéré que [ce bug était connu](https://bugzilla.vyatta.com/show_bug.cgi?id=6974) de la communauté Vyatta, du à l’utilisation de la suite de logiciels Quagga. Une solution temporaire proposée par un membre du staff était d’annuler les commandes Vyatta et de revenir aux commandes classiques d’une Debian (route, ifconfig etc).

Cela nous semblait un peu “sale” mais aucune solution pérenne n’avait encore été apportée au projet.

Commençons par enlever la partie de la configuration faisant bugger notre architecture.

`vyatta@vyatta# delete protocoles interface-route 91.y.y.254/32`

Maintenant on va refaire la même chose, mais avec les commandes Debian. Elles sont toujours accessibles sous Vyatta. En revanche vous allez devoir vous loguer en root (su -). Les commandes sont les mêmes entre les deux users, mais celles de Vyatta ne sont accessibles que depuis l’user « vyatta », sous « root » on ne sera pas gêné au moins.

`route add **gateway_du_dédié** dev eth2 route add default gw **gateway_du_dédié**`

Le principe reste le même, on précise comment atteindre l’IP de la gateway de l’ESX et ensuite on annonce que cette IP est la passerelle de la VM bridgée. Voici la table de routage obtenue après modifications :

`vyatta@vyatta:~$ ip route default via 94.23.6.254 dev eth2 94.23.6.254 dev eth2  scope link`

Evidemment c’est une conf qui va sauter au prochain redémarrage. Il faut appliquer ces modifications juste après le chargement de la configuration de Vyatta.

Dans la version 6.5, il y’a un fichier  */config/scripts/vyatta-postconfig-bootup.script* qui est comme son nom l’indique exécuté juste après le chargement de la configuration. Placez les deux commandes *route* dans ce script. Rebooter et vérifier que votre table arp ne se rempli pas constamment (arp -a)
 Les problèmes de flood ARP ont bien été résolus une fois ces manipulations effectuées. Dommage que Vyatta ne propose rien actuellement pour régler ce problème.


## NAT Masquerade Vyatta:

Pour router le trafic LAN sur le WAN, entrer les commandes suivantes en mode configure:

```
source {
    rule 10 {
        description NAT-LAN-TO-WAN
        outbound-interface eth2
        source {
            address 10.0.10.0/24
        }
        translation {
            address masquerade
        }
    }
```

Merci de votre attention pour ce premier billet. Si vous souhaitez plus de détails ou autre, n’hésitez pas.
