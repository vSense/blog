---
title: "Vyatta: Routing"
slug: vyatta-routing
date_published: 1970-01-01T00:00:00.000Z
date_updated:   2013-04-06T18:59:59.000Z
tags: VMware, VMware, Vyatta, Vyatta
draft: true
---


It’s been a while since we are talking about Vyatta, it is the router we use for our architecture at OVH and we have used it also for academic purposes.

Vyatta is a Debian based distribution which integrate all the features you can find on professional hardware. Vyatta can be install on any x86 hardware and is administrated via a CLI pretty much like IOS or Juniper. It comes multiples edition, one free and open source and one VSE (Vyatta Subscribe Edition) which give you technical support, web interfaces and other specifics feature such as configuration synchronization. Vyatta also offers physical appliance and play the financial card to challenge its competitors. [Here](http://www.vyatta.com/sites/vyatta.com/files/pdfs/Vyatta_Cisco_Replacement_Guide_0.pdf) is a price comparison between Vyatta and Cisco.

Vyatta is quite complete: ADSL, IPv6, BGP, OSPF (via OpenBGP and OpenOSPF), VRRP, VPN SSL, etc. Routing function come from the Quagga suite.

It is going to be a quite basic article, without vulgarizing too much to explain how to start with Vyatta.


# Installation

We will use the core version of Vyatta

Press « entrer » to boot into Vyatta.  
 You should end up with a login and password request.

**Both are vyatta.**

The prompt shows  : **vyatta@vyatta:~$**  
 La commande pour installer Vyatta en dur sur notre VM est **install-system**  
 The command to install Vyatta into your hard drive (or your virtual machine vdisk) is **install-system**  
 Répondez aux questions qui suivent, attendez la fin de l’installation (~5min) et rebootez.  
 Answer to the following questions and wait for the end of the installation. Then reboot.  
 As Juniper JUNOS, Vyatta has two configuration modes, « normal » (CLI with JUNOS) and « configure » (as well with JUNOS)  
 Vous êtes logués dans le mode « normal », symbolisé par la caractère à la fin de votre prompt **$**  
 Pour passer en mode de « configuration », tapez **configure**.  
 Votre prompt change et le symbole de fin devient : **#**  
**exit** vous fait revenir au mode normal.

<div>Bien que sous UNIX ces symboles permettent de différencier un utilisateur ayant un niveau de privilège normal d’un utilisateur « root », sous Vyatta la différence entre ces deux signes s’arrête au mode de configuration.  
 Vous pouvez essayer de lancer un **apt-get update** en mode configure, ça ne marchera pas. Pour ça, vous devez vous loguer en root avec un **sudo su**.</div>Nous sommes donc en mode de configuration.  
 Vyatta a prévu (à la manière de Cisco et d’autres constructeurs) une aide pour vous assister lors de la configuration de votre routeur. Cette aide se caractérise par une auto-complétion de vos commandes accessibles soit grâce à la touche de tabulation soit par la touche du point d’interrogation. Un appui affiche la liste des mots-clés disponibles, un deuxième appuie, affiche en plus la description de ceux ci.

La plupart des commandes qui vont nous intéresser commence par set. Si vous faites un petit tab derrière, vous vous rendez compte que les choix sont nombreux ensuite.  
 Chez Cisco, la configuration d’un équipement se fait par le passage dans des modes de configuration successifs, ceux ci sont imbriqués.  
 Sur Vyatta, la configuration se fait toujours sur une seule ligne de commande, ce qui induit automatiquement des commandes relativement longues.

Voyons quelques exemples afin de rendre ceux ci plus parlant :

La première chose que nous allons faire est d’activer les connexions SSH sur Vyatta. Il sera en effet bien plus simple de s’y connecter de cette façon et nous retrouverons notre bon vieux clavier azerty.  
 L’opération se déroule en trois étapes : on passe en mode configuration, on exécute la commande appropriée, on applique les changements au système.  
 Code : Console – [Sélectionner](http://www.siteduzero.com/tutoriel-3-614628-1-introduction-a-vyatta.html#)

<div><table><tbody><tr><td><div>vyatta@vyatta:~$ configure [edit] vyatta@vyatta# set service ssh [edit] vyatta@vyatta# commit [ service ssh ] Restarting OpenBSD Secure Shell server: sshd. [edit] vyatta@vyatta#

</div></td></tr></tbody></table></div>Le service SSH est maintenant activé.

Tandis que sous Cisco, une fois la commande exécutée celle ci est automatiquement appliquée, sous Vyatta, il faut « valider » afin que la commande soit appliquée au système.  
 En cas d’erreur de syntaxe, d’incohérence dans la configuration (adresse IP configurée à la fois en statique et en dhcp par exemple), le système vous préviendra de l’erreur au moment du **commit**.  
 La commande **discard** annule les opérations non appliquées.

Les autres commandes indispensables à connaître sont celles vous donnant les informations sur le système. Elles commencent par la commande show.

Voici par exemple l’état de nos interfaces :

<div><table><tbody><tr><td><div>vyatta@vyatta# run show interfaces Codes: S - State, L - Link, u - Up, D - Down, A - Admin Down Interface    IP Address                        S/L  Description ---------    ----------                        ---  ----------- eth0         192.168.1.49/24                   u/u eth1         -                                 u/u lo           127.0.0.1/8                       u/u              ::1/128

</div></td></tr></tbody></table></div>Astuce : pour éviter d’avoir à repasser en mode « normal » avec la commande** exit**, vous pouvez mettre un **run** devant votre commande, elle sera exécutée comme si vous étiez en mode normal.

Voici donc un rapide aperçu de ce qu’est Vyatta. Un tutoriel complet serait inutile puisque cela reviendrait à faire un cours de réseau et à paraphraser la documentation. Celle ci est d’ailleurs extrêmement complète et détaillée, je vous encourage à vous y reporter sans modération.



