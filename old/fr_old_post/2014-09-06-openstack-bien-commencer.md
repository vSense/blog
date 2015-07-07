---
title: OpenStack, bien commencer
slug: openstack-bien-commencer
date_published: 2014-09-06T16:30:34.000Z
date_updated:   2014-08-29T16:54:19.000Z
tags: cloud, glance, instance, keystone, neutron, nova, openstack, start, swift, tuto, virtualisation
---


La grande famille des solutions de virtualisation est composée de produits propriétaires (Hyper-V de Microsoft, vSphere de VMware) et de produits libres et/ou open source (KVM, Proxmox, OpenVZ, QEMU etc). Des produits open source il y en a beaucoup mais un sort particulièrement du lot : OpenStack.

En fait, il est faux de parler d’OpenStack comme un logiciel de virtualisation. OpenStack c’est un projet (lancé par la NASA et Rackspace) composés d’autres projets dont l’un d’entre eux (Nova) permet de faire tourner des machines virtuelles.

OpenStack n’est donc pas un logiciel de virtualisation et ce n’est pas non plus un hyperviseur.

OpenStack est composé de briques, chacune a un rôle précis et c’est à vous de choisir celles dont vous avez besoin pour construire votre architecture. En voici quelques unes :

- Nova : Gestion des instances (= vm), les lancer, les arrêter, les snapshoter, les supprimer etc.
- Keystone : Gestion de l’identité. Comme son nom l’indique c’est la clé de voute du système, il gère l’authentification des services les uns par rapport aux autres, les droits utilisateurs, les projets, les groupes etc
- Swift : Gestion du stockage objet. Peut être utilisé complètement indépendamment du reste des « briques »
- Cinder : Gestion du stockage en volume, présentation des volumes aux instances
- Neutron : Gestion du réseau (SDN). Anciennement Quantum. Provisionnement du réseau, VLAN, subnets, firewall, VPN, LB, etc à la demande. Fourni la connectivité L2 et L3.
- Glance : Gestion des images
- Horizon : Interface web de management

### Instances vs VM

Pour Nova, j’ai parlé d’instances et non pas de VM. Il y a une raison à cela. Bien qu’il s’agisse techniquement du même type d’objet, ils n’ont pas le même but « philosophique ».

Une VM est uniquement un serveur virtuel, son but est de tourner en 24/7 avec une disponibilité proche de 100%.  
 Une instance a par principe une durée de vie limitée. Elle naît puis meurt.

Mais pourquoi éteindre une instance ? Et bien parce que la haute disponibilité et la scalabilité, les deux arguments historiques de la virtualisation, ne sont pas assurés par l’instance mais par un groupe d’instances. Il ne s’agit plus ici de modifier le CPU ou la RAM d’une instance à chaud mais tout simplement de créer (« launch ») une nouvelle instance préconfigurée qui s’ajoutera au cluster existant.  
 La pratique a montré que l’on préfère d’ailleurs repartir sur une instance vierge et la configurer en post-install à l’aide de Chef/Puppet/Salt.

Les données n’étant pas liées au instances (ce ne sont que des unités de traitement), on peut les supprimer (« terminate ») sans risque. On supporte ainsi beaucoup plus facilement les montées et baisses de charge d’une application.

D’un point de vue technique, il y a une légère différence cependant. Une instance est créée à partir d’un gabarit (« AMI » chez AWS, « flavor » chez OpenStack) . Bien que l’on puisse aussi créer des VM à partir de templates chez VMware, une instance est toujours créée à partir d’un existant chez OpenStack, un gabarit, un snapshot, un  volume etc.

### Comparaisons avec VMware

Les articles de virtu de ce blog traitaient jusqu’à présent exclusivement de vSphere de VMware. Afin de ne pas être perdu avec OpenStack, je fais faire quelques parallèles (quand ce sera possible) qui permettront de mieux se repérer.

**OpenStack = ESXi ?**  
 Non, OpenStack est un ensemble de logiciels, ESXi est un hyperviseur.  
**OpenStack  = vCenter ?**  
 Non, Openstack ne crée pas de fonctions de clustering, ne fourni pas de répartition de charge etc comme le fait vCenter  
**OpenStack  = vCloudDirector ?**  
 Oui c’est sûrement le meilleur parallèle que l’on puisse faire. Et encore…  
** Nova = ESXi ?**  
 Non, Nova n’est pas un hyperviseur, c’est lui qui gère l’hyperviseur mais celui ci peut être n’importe quoi.  Couramment on trouvera KVM, mais on peut trouver ESXi grâce aux drivers fournis par VMware ou Hyper-V.

vSphere étant une grosse boite plus ou moins noir, il n’est pas possible de faire de lien entre les autres services OpenStack avec vSphere. Sachez cependant que si on trouvait le même type d’architecture chez VMware :

- Cinder serait le service gérant les VMDK
- Neutron gérerait les vSwitch et les DvS
- Keystone serait à mi chemin entre un AD et SSO
- Horizon serait le vSphere Web Client.
- Swift n’a vraiment aucun équivalent chez VMware, c’est une solution de stockage en mode bloc qui défini donc une manière d’organiser les données sur une baie SAN plutôt qu’une véritable brique de virtualisation.

### Ce qui est nécessaire de ce qui ne l’est pas

La première chose dont on se rend compte avec OpenStack, c’est qu’il y a beaucoup de choses à installer, trop peut être. Néanmoins, chaque brique à sa fonction clairement définie et finalement la seule chose à savoir c’est « de quoi j’ai besoin » et « de quoi je peux me passer ».

Dans la liste des services indispensables :

- Une base de données (MySQL, Postgre et SQLite sont supportés) est la première chose qu’il vous faut bien que ce ne soit pas un service OpenStack
- Keystone va ensuite servir de liant à tous vos services. Ceux ci communiquent via API et Keystone fourni les endpoints pour interconnecter tout ce petit monde
- Nova est indispensable dans son rôle de gestion des instances

Et c’est tout. Avec ça, OpenStack pourra lancer des instances et les faire fonctionner. On aura même du réseau, super light mais ça marchera  (fourni par Nova).

Maintenant on peut ajouter quelques services.

- Glance pour fournir des ISO sur lesquels booter
- Neutron pour avoir un peu de cloisonnement réseau au lieu d’un flat network
- Cinder pour avoir des volumes persistants au lieu d’un stockage éphémère.
- Horizon pour une belle interface web au lieu de la CLI

Swift est en revanche totalement optionnel, votre stockage peut reposer sur un système de fichiers classiques ou dans une baie SAN traditionnelle. Heat et Ceilometer apportent du confort, mais rien d’indispensable pour démarrer.

#### A propos du stockage

Une instance vient par défaut avec du stockage. Ce stockage est qualifié « d’éphémère ». Ce stockage est lié à l’instance et est généralement pris directement dans le stockage de l’hyperviseur sur lequel tourne l’instance. Si vous supprimez votre instance, le stockage sera supprimé aussi. Ce stockage n’étant par définition par partagé, il ne permettra pas non plus de migration d’instance entre hyperviseurs.  
 L’autre type de stockage est appelé « persistant ». Il est fourni par Cinder et s’apparente tout simplement à un disque que vous attachez à votre instance comme vous avez l’habitude de le faire avec VMware et les VMDK.

### Où commencer !

Pour vous lancer dans l’aventure, rien ne vaut la doc officielle pour Ubuntu ou Debian. Faîtes attention, celle ci est mise à jour plusieurs fois par semaine 😉

A l’heure où j’écris, la version la plus récente pour Icehouse stable sur Debian est [celle ci](http://docs.openstack.org/icehouse/install-guide/install/apt-debian/openstack-install-guide-apt-debian-icehouse.pdf) :

 

 



