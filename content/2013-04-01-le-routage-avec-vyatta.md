---
title: Le routage avec Vyatta
slug: le-routage-avec-vyatta
authors: Romain Guichard
about_author: Romain Guichard est ingenieur cloud @Osones
email: rguichard@vsense.fr
date_published: 2013-04-01T17:32:09.000Z
date_updated:   2014-08-28T23:05:02.000Z
tags: Routage, sdn, tuto, VMware, VMware, Vyatta, Vyatta, vyos
category: Réseau
---


Cela fait quelques articles que nous parlons de Vyatta, il s’agit du routeur logiciel que nous utilisons pour notre architecture chez OVH et que nous avons déjà utilisé pour des projets académiques et/ou associatifs.

Vyatta c’est tout simplement une distribution basée sur une Debian qui intègre tous les outils que peuvent vous proposer des routeurs professionnels. Ce système se place en concurrence direct avec les 1800 series ou les ASA 5500 de chez Cisco.
 Vyatta s’installe sur n’importe quelle archictecture x86 et s’administre via une interface en ligne de commande qui ressemble beaucoup à ce qu’on retrouve sur du matériel Juniper (excepté la gamme SSG et ScreenOS) mais qui ne ne déboussolera pas les habitués de l’IOS de Cisco.
 Vyatta est disponible sous deux versions, une version Core qui ne comprend que le système sans support et une version VSE (Vyatta Subscription Edition) qui donne droit à un support technique (et à une interface web bien moche). Des appliances physiques sont aussi disponibles et c’est à ce niveau que Vyatta joue la carte « financière » pour se démarquer de ses concurrents. Vous pouvez trouver [ici](http://www.vyatta.com/sites/vyatta.com/files/pdfs/Vyatta_Cisco_Replacement_Guide_0.pdf) un petit benchmark financier entre les produits Vyatta et Cisco.

Vyatta est un routeur relativement complet, ADSL, IPv6, BGP, OSPF (via leur implémentation libre OpenBGP et OpenOSPF), VRRP, VPN SSL, OpenVPN, ProxyWeb etc. Les fonctions de routage étant fournies par la suite de logiciels [Quagga](http://www.nongnu.org/quagga/).

Je vais rapidement vous présenter l’utilisation de Vyatta. Sans entrer dans la vulgarisation, cet article sera moins technique que nos précédents, essayant de montrer au mieux comment s’en sortir avec Vyatta pour une première utilisation.


# Installation

Nous on est étudiants, on a pas de sous et même si on aime bien VMware, on aime bien aussi l’esprit communautaire. Donc on utilise la version Core, open source. Placer votre ISO dans votre VM et bootez dessus.

Pressez la touche « enter » pour booter sur Vyatta. Vous finissez si tout se passe bien devant une demande de login et de mot de passe.

Le login et le mot de passe sont **vyatta**.

**Attention, la configuration du clavier par défaut de Vyatta est un qwerty !**

Le prompt indique ensuite : **vyatta@vyatta:~$**. La commande pour installer Vyatta en dur sur notre VM est **install system**. Répondez aux questions qui suivent, attendez la fin de l’installation (~5min) et rebootez. A la manière du système d’exploitation IOS de Cisco, Vyatta dispose de plusieurs modes de configuration, au nombre de deux. Vous êtes logués dans le mode « normal », symbolisé par la caractère à la fin de votre prompt **$**. Pour passer en mode de « configuration », tapez **configure**. Votre prompt change et le symbole de fin devient : **#**. **exit** vous fait revenir au mode normal.

Bien que sous UNIX ces symboles permettent de différencier un utilisateur ayant un niveau de privilège normal d’un utilisateur « root », sous Vyatta la différence entre ces deux signes s’arrête au mode de configuration. Vous pouvez essayer de lancer un **apt-get update** en mode configure, ça ne marchera pas. Pour ça, vous devez vous loguer en root avec un **sudo su**. Nous sommes donc en mode de configuration. Vyatta a prévu (à la manière de Cisco et d’autres constructeurs) une aide pour vous assister lors de la configuration de votre routeur. Cette aide se caractérise par une auto-complétion de vos commandes accessibles soit grâce à **la touche de tabulation** soit par** la touche du point d’interrogation**. Un appui affiche la liste des mots-clés disponibles, un deuxième appuie, affiche en plus la description de ceux ci.

La plupart des commandes qui vont nous intéresser commence par set. Si vous faites un petit tab derrière, vous vous rendez compte que les choix sont nombreux ensuite. Chez Cisco, la configuration d’un équipement se fait par le passage dans des modes de configuration successifs, ceux ci sont imbriqués. Sur Vyatta, la configuration se fait toujours sur une seule ligne de commande, ce qui induit automatiquement des commandes relativement longues.

Voyons quelques exemples afin de rendre ceux ci plus parlant :

Déjà travailler en qwerty c’est pas drôle. Donc on va passer tout ça en azerty :

`set console keymap`

Plusieurs choix vont vous êtes proposés, prenez le clavier générique en français, ça fonctionnera très bien.

Nous allons commencer par activer les connexions SSH sur Vyatta. Il sera en effet bien plus simple d’y travailler de cette façon. L’opération se déroule en trois étapes : on passe en mode configuration, on exécute la commande appropriée, on applique les changements au système.

```
vyatta@vyatta:~$ configure
vyatta@vyatta# set service ssh
vyatta@vyatta# commit
[ service ssh ] Restarting OpenBSD Secure Shell server: sshd.
vyatta@vyatta#
```
Le service SSH est maintenant activé.

Tandis que sous Cisco (et ScreenOS), une fois la commande exécutée celle ci est automatiquement appliquée, sous Vyatta, il faut « valider » afin que la commande soit appliquée au système, comme sous JUNOS. En cas d’erreur de syntaxe, d’incohérence dans la configuration (adresse IP configurée à la fois en statique et en dhcp par exemple), le système vous préviendra de l’erreur au moment du **commit**. La commande **discard** annule les opérations non appliquées. **Rollback** permet de la même manière que sous JUNOS de revenir à une configuration précédente. Mais contrairement au système de Juniper, un reboot est requis.

On va au moins configurer une interface, que SSH puisse écouter quelque part.

```
vyatta@vyatta# set interfaces ethernet eth0 address 192.168.25.25/24
vyatta@vyatta# set interface ethernet eth0 description WAN
```

On oublie pas de commit à la fin.

Les autres commandes indispensables à connaître sont celles vous donnant les informations sur le système. Elles commencent par l’originale commande *show*.

Voici par exemple l’état de nos interfaces :

```
vyatta@vyatta# run show interfaces
Codes: S - State, L - Link, u - Up, D - Down, A - Admin Down
Interface    IP Address                        S/L  Description
---------    ----------                        ---  -----------
eth0         192.168.25.25/24                  u/u
eth1         -                                 u/u
lo           127.0.0.1/8                       u/u              ::1/128
```

Astuce : pour éviter d’avoir à repasser en mode « normal » avec la commande** exit**, vous pouvez mettre un **run** devant votre commande, elle sera exécutée comme si vous étiez en mode normal (comme sous JUNOS ou comme **do** chez Cisco).

Allez une petite translation NAT source pour finir.

On configure notre deuxième interface (la première fera office de patte WAN) et on va mettre un DHCP pour notre LAN, histoire d’être sympa.

```
vyatta@vyatta# set interfaces ethernet eth1 address '10.0.10.254/24'
vyatta@vyatta# set interfaces ethernet eth1 description LAN
vyatta@vyatta# set nat source rule 10 description NAT-LAN-TO-WAN
vyatta@vyatta# set nat source rule 10 outbound-interface eth0
vyatta@vyatta# set nat source rule 10 source address 10.0.10.0/24
vyatta@vyatta# set nat source rule 10 translation address masquerade
vyatta@vyatta# set service dhcp-server shared-network-name LAN subnet 10.0.10.0/24 default-router '10.0.10.254'
vyatta@vyatta# set service dhcp-server shared-network-name LAN subnet 10.0.10.0/24 dns-server '10.0.10.100'
vyatta@vyatta# set service dhcp-server shared-network-name LAN subnet 10.0.10.0/24 domain-name 'vsense.fr'
vyatta@vyatta# set service dhcp-server shared-network-name LAN subnet 10.0.10.0/24 lease '86400' vyatta@vyatta# set service dhcp-server shared-network-name LAN subnet 10.0.10.0/24 start 10.0.10.200 stop '10.0.10.210'
```

Voici donc un rapide aperçu de ce qu’est Vyatta. Un tutoriel complet serait inutile puisque cela reviendrait à faire un cours de réseau et à paraphraser la documentation. Celle ci est d’ailleurs extrêmement complète et détaillée, je vous encourage à vous y reporter sans modération.
