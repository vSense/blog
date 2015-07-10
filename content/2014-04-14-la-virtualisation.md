---
title: La virtualisation
authors: Kevin Lefevre
about_author: Kevin Lefevre est ingenieur cloud @osones
email: klefevre@vsense.fr
slug: la-virtualisation
date_published: 2014-04-14T17:16:29.000Z
date_updated:   2015-06-28T17:19:51.000Z
tags: hyperviseur, virtualisation
---


Les paragraphes suivant sont extraits d’un [petit rapport écris à l’université](https://drive.google.com/file/d/0B-y_lX94BMsQZ2dIZnJQNUVxcmM/edit?usp=sharing) qui faisait la comparaison de différentes solutions de virtualisation. Cela s’adresse particulièrement au néophytes et permet de visualiser plus simplement les différents aspects de la virtualisation.


## Les différents types de virtualisation

Il existe actuellement différents types de virtualisation et chaque type répond à un besoin, une utilisation particulière et dispose de ses propres contraintes et avantages. Pour aborder la suite, il est important de comprendre le vocabulaire suivant:

- Système hôte: Machine physique (et son système) qui virtualise le système invité.
- Hyperviseur: Logiciel permettant de créer et gérer des machines virtuelles. Il est installé sur la machine hôte.
- Système invité: Machine virtuelle s’exécutant sur un hôte.

### Émulation pure

C’est la forme la de virtualisation la plus basique. L’hyperviseur présente un matériel virtuel complet au système invité qui peut être d’une architecture CPU complètement différente du systèmes hôte. L’hyperviseur convertit ensuite les instructions CPU interceptées de la machine virtuelle en instructions compréhensibles par son CPU. C’est la technique utilisée par les émulateurs de consoles de salons qui disposaient souvent d’une architecture non standardisée. Cette technique offre des performances relativement médiocres dues à la différence d’architecture CPU.

[![emux](http://res.cloudinary.com/vsense/image/upload/v1435508390/emux_tkiyiw.png)](http://res.cloudinary.com/vsense/image/upload/v1435508390/emux_tkiyiw.png)

### Virtualisation complète

La virtualisation complète consiste à présenter au système d’exploitation invité un matériel virtuel complet s’exécutant de la même manière qu’un système physique. Cela permet à un système d’exploitation invité de s’exécuter sans modifications préalables et sans avoir conscience d’être une machine virtuelle. Les système hôtes et invités doivent supporter la même architecture, e.g. un système invité x64 sur un système hôte x64. Cette solution apporte une certaine isolation entre les machines virtualisées et ces machines s’exécutent en parallèle sur un ou plusieurs serveurs. Cela permet de centraliser les coûts et d’exploiter au maximum le matériel. C’est la technologie la plus utilisée dans les environnements complexes puisqu’elle permet de virtualiser différents types de systèmes d’exploitation (Windows, Linux …) sur une même plate-forme et sans modifications.

[![fullvirtx](http://res.cloudinary.com/vsense/image/upload/v1435508389/fullvirtx_xvaoft.png)](http://res.cloudinary.com/vsense/image/upload/v1435508389/fullvirtx_xvaoft.png)

 En complément, certains constructeurs comme Intel ou AMD supportent ce que l’on appelle la virtualisation matérielle assistée et fournissent des jeux d’instructions spécifiques dans leurs processeurs pour supporter et améliorer les performances de la virtualisation. Ces instructions sont devenues relativement standardisées et sont présentes dans la majorité des serveurs ainsi que sur les ordinateurs de bureau et portables grand public.

### Para-virtualisation

La para-virtualisation se situe entre l’exécution sur machine physique et la virtualisation complète. Pour améliorer les performances, l’hyperviseur permet à la machine virtualisée de communiquer avec lui. Il fournit une interfaces de communication à la machine virtuelle ce qui permet d’exécuter des opérations plus rapidement via l’hyperviseur plutôt que de les exécuter en environnement virtuel.

Il existe différents types de para-virtualisation, la plus connue étant la para-virtualisation CPU. Un de ses désavantages est la nécessité de disposer d’un système d’exploitation invité modifié pour utiliser ces interfaces et donc avoir conscience d’être virtualisé. Cela ne pose pas beaucoup de problèmes dans le cas des systèmes d’exploitation open-source comme Linux (le kernel supportant la para-virtualisation est maintenu officiellement depuis 2006) mais dans le cas de systèmes aux sources fermées, comme Windows, cela s’avère plus complexe.

[![paravirtx](http://res.cloudinary.com/vsense/image/upload/v1435508387/paravirtx_gfj2zt.png)](http://res.cloudinary.com/vsense/image/upload/v1435508387/paravirtx_gfj2zt.png)

Il existe d’autres types de para-virtualisation hybride qui ne nécessitent pas de modifications de l’OS comme par exemple la virtualisation de contrôleurs de stockage iSCSI ou de cartes réseaux utilisées par les produits VMware.

### Conteneurs

Les conteneurs ou isolateurs sont également appelés Operating system-level virtualization. Cette technologie est basée sur un kernel supportant la virtualisation de plusieurs instances du kernel en espace utilisateur userland. C’est une évolution du chroot qui consiste à isoler un utilisateur ou un processus dans un système de fichiers particulier. Les performances sont bien meilleurs que la virtualisation complète mais les choix sont limités. Le système virtualisé doit être du même type que l’hôte, majoritairement Linux. De plus, l’isolation n’est pas complète et le kernel étant partagé, la montée en charge d’un conteneur peut fortement impacter les performances des autres conteneurs. Cette technologie est souvent utilisée par les fournisseurs de serveur virtuels tel qu’OVH pour fournir des serveurs à bas prix car cette technologie coûte sensiblement moins chère que la virtualisation complète.

[![contx](http://res.cloudinary.com/vsense/image/upload/v1435508391/contx_nqef7p.png)](http://res.cloudinary.com/vsense/image/upload/v1435508391/contx_nqef7p.png)


## Les hyperviseurs

L’hyperviseur forme la couche logicielle présente entre le matériel et les machines virtuelles. C’est lui qui permet la création et la gestion des machines. Il existe deux types d’hyperviseur. Il est parfois difficile de distinguer ces deux types comme nous le verrons par la suite:

- Type 1: ou « bare metal » s’exécute directement au dessus du matériel et fournit une interface minimale dans la but unique de gérer des machines virtuelles.
- Type 2: s’exécute sur un système d’exploitation classique et fournit en plus de celui-ci la possibilité de gérer des machines virtuelles.
- Conteneur – Isolateur: N’est pas vraiment un hyperviseur puisqu’il repose à la base sur un système d’exploitation. Sans système d’exploitation, le conteneur n’a pas de sens.

Bien que ces trois méthodes de virtualisation soient utilisées en entreprise, celles-ci le sont de manière inégale. En effet, les hyperviseurs de type 1 sont majoritairement utilisés par les grandes entreprises tandis que les isolateurs peuvent être utilisés dans de plus petites structures (PME par exemple). Les hyperviseurs de type 2 sont quant à eux plus utilisés comme solutions de bureau.

SDN: Software defined network

Les SDN ou réseaux définis par logiciels sont une conséquence de la virtualisation massive des serveurs et de la délocalisation des ressources des entreprises dans le Cloud.

Le concept est identique à la virtualisation des serveurs mais s’applique aux équipements réseaux. Un équipement réseau (routeur ou commutateur par exemple) est composé de deux plans:

- Le plan de données ou Data Plane, qui représente la partie matérielle de l’équipement qui effectue les opérations de forwarding de paquets au niveau matériel.
- Le plan de contrôle ou Control Plane, qui représente la partie intelligente de l’équipement réseau, c’est-à-dire qui calcule et crée la table de routage qui est ensuite programmée dans le plan de données. Elle contient également d’autres  fonctionnalités suivant le type d’équipement.

Le principe est de virtualiser la partie plan de contrôle afin de faciliter la gestion des équipements réseaux physiques autour d’un point de contrôle centrale qui va gérer un parc d’équipements physiques.

[![sdnx](http://res.cloudinary.com/vsense/image/upload/v1435508387/sdnx_h9ha78.png)](http://res.cloudinary.com/vsense/image/upload/v1435508387/sdnx_h9ha78.png)


## Les noyaux

Pour les hyperviseurs de type 1, on peut distinguer deux sous-types d’hyperviseur : les hyperviseurs à micro-noyau et les hyperviseurs à noyau monolithique. Chaque type possède ses avantages et ses inconvénients. Les noyaux monolithiques sont composés d’un seul bloc s’exécutant en espace noyau et sont par conséquent plus rapides mais plus sensibles aux problèmes puisque, lors d’un crash noyau, c’est tout le système qui crash. De plus, l’ajout de fonctionnalités au noyau nécessite une compilation. C’est le cas du noyau UNIX par exemple. Le noyau Linux est hybride: il est monolithique mais des modules peuvent venir se charger en espace utilisateur.

[![monokernelx](http://res.cloudinary.com/vsense/image/upload/v1435508388/monokernelx_u2nvhq.png)](http://res.cloudinary.com/vsense/image/upload/v1435508388/monokernelx_u2nvhq.png)

Les micro noyaux sont constitués uniquement d’un noyau cœur qui s’exécute en espace noyau, les autres modules sont chargés séparément en espace utilisateur et communiquent entre eux via des bus de messages. Cela rend le noyau plus lent que les noyaux monolithiques. Les avantages d’une telle architecture sont : la taille du noyau, sa modularité, sa portabilité et sa résistance aux crashes.

[![microkernelx](http://res.cloudinary.com/vsense/image/upload/v1435508389/microkernelx_mjawzt.png)](http://res.cloudinary.com/vsense/image/upload/v1435508389/microkernelx_mjawzt.png)



