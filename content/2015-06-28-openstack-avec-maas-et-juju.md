---
title: OpenStack avec MAAS et JuJu
authors: Romain Guichard
slug: openstack-avec-maas-et-juju
date_published: 2015-06-28T17:19:42.000Z
date_updated:   2015-06-28T17:19:42.000Z
tags: cloud, déploiement, juju, maas, openstack, sdn, ubuntu
---


Tous ceux qui ont tenté l’aventure OpenStack ont rencontré les mêmes problèmes. Bien que la doc soit très complète et plutôt bien foutue, on se rend vite compte que déployer une infrastructure OpenStack fonctionnelle est très long. Ajouter à ça votre condition humaine qui vous fera oublier un « ; » dans un fichier de conf ou qui inversera deux octets dans une adresse IP et vous êtes partis pour débugger pendant un petit moment…

Pour adresser ce problème, plusieurs projets sont nés afin de rendre le déploiement d’OpenStack plus rapide, plus sûr et nous permettre de nous consacrer sur de vrais problèmes d’architecture.

On peut citer Suse OpenStack Cloud de SUSE, Helion d'HP, Mirantis OpenStacke Software de Mirantis, RDO de RedHat et le combo MAAS/JuJu de Cannonical. Tous ces outils utilisent pour la plupart une philosophie commune : celle de transformer rapidement n’importe quel serveur baremetal (MAAS est l’acronyme de Metal as a Service) en un nœud  disponible pour des services OpenStack.

Le but avoué est de pouvoir scaler, provisionner et automatiser toute la configuration des services d’OpenStack.

MAAS/Juju comme SUSE Cloud se servent de deux types outils pré-existant pour fonctionner : le boot PXE et les gestionnaires de configuration Puppet/Chef/Salt. Avec cela, nous sommes en mesure de lancer une installation automatiquement et de pousser les configurations nécessaires. Une fois qu’un nœud a booté en PXE et est reconnu par le serveur d’admin, ces nœuds sont mis à disposition d’un second système (*Juju* dans un cas, *Crowbar* dans l’autre) pour installer les logiciels (des *charms* avec Juju, des *barclamps* avec Crowbar) dont on a besoin.

MAAS sont des produits gratuits alors que SUSE Cloud est lui payant, je vais donc présenter MAAS ici.

### Préparation de l’environnement

Comme je l’ai dit, un des outils fondamentales de MAAS est le boot PXE. Le boot PXE nécessite un serveur DHCP configurable (isc-dhcp par exemple) et va nous obliger à travailler dans un environnement que l’on maitrise.

J’utilise un minimum de 4 machines virtuelles pour cet environnement.

- Le serveur MAAS sous Ubuntu 14.04
- Un routeur virtuel sous VyOS
- Un nœud qui accueillera JuJu et le services « controller » OpenStack
- Un ou plusieurs nœuds « compute » OpenStack

Le routeur virtuel possède deux interfaces comme MAAS et effectue du NAT source pour permettre au réseau « MAAS » de sortir sur Internet.
 MAAS possède une interface dans un réseau « MAAS ».
 Les autres machines ne possèdent qu’une seule interface dans le réseau « MAAS ».
 Dans le réseau « MAAS », seul le serveur MAAS doit répondre aux requêtes DHCP. Dans le cas contraire, les boot pxe échoueront.

Ce qui donne cette architecture :

[![maas-1](http://res.cloudinary.com/vsense/image/upload/h_300,w_300/v1435508382/maas-11_q8oh5p.jpg)](http://res.cloudinary.com/vsense/image/upload/v1435508382/maas-11_q8oh5p.jpg)

###  Installation MAAS-Server

On commence par installer le serveur MAAS. Peu importe les ressources, le mien possède 2Go de RAM et 2 vCPU.

Je vous conseille la dernière version LTS 14.04 Ubuntu Trusty car contrairement à la 12.04 elle intègre nativement les fonctionnalités « cloud » dont nous avons besoin.
 Au démarrage de votre install, il faut choisir « Multiple server install with MAAS ». Il est tout à fait possible d’installer MAAS après l’installation du système, mais autant commencer dès maintenant.

[![install_02](http://res.cloudinary.com/vsense/image/upload/h_227,w_300/v1435508381/install_024_nywevs.png)](http://res.cloudinary.com/vsense/image/upload/v1435508381/install_024_nywevs.png)

L’installation se déroule normalement jusqu’à ce que vous devez choisir si vous voulez créer un nouvel environnement MAAS sur ce serveur ou en rejoindre un. On choisi évidemment d’en créer un.

[![install_05](http://res.cloudinary.com/vsense/image/upload/h_222,w_300/v1435508381/install_05_qsr61n.png)](http://res.cloudinary.com/vsense/image/upload/v1435508381/install_05_qsr61n.png)

L’installation continue normalement et en fonction de la version de MAAS fournie avec votre Ubuntu, l’installation vous donnera (ou pas) l’adresse sur laquelle vous connecter pour accéder à MAAS.

Une fois celle ci terminée, on peut se connecter à **http://IPserveurMAAS/MAAS**

La première info à l’écran vous demander de créer un user pour MAAS. On s’exécute et on se connecte avec.

Nous allons commencer par modifier la carte réseau de MAAS en éditant le seul nœud de notre cluster.

[![import-images](http://res.cloudinary.com/vsense/image/upload/h_150,w_300/v1435508380/import-images_ivkyb6.png)](http://res.cloudinary.com/vsense/image/upload/v1435508380/import-images_ivkyb6.png)

Éditez sa seule carte réseau et ajoutez « managed DHCP » dans la section management. Cela permettra à MAAS d’écouter sur cette interface. Vous pouvez aussi rajouter les paramètres fournis par le DHCP notamment la gateway de votre réseau (mon VyOS chez moi). Le range d’IP sera utilisé pour allouer des IP aux nœuds.

Revenez à l’écran du screenshot et vous constater que MAAS vous demande de charger des boot images. Ce sont les iso qui seront fournis aux nœuds lors du boot pxe.
 Cliquez sur « import boot images » pour lancer le téléchargement depuis les dépôts Canonical. Ça prend du temps, ne soyez pas trop impatient et ne cliquez pas une seconde fois !

C’en est fini pour le serveur MAAS !

### Boot des nœuds en PXE

On peut maintenant commencer à booter nos nœuds en PXE.

Si votre VM est vierge, cela devrait se faire naturellement puisque le disque dur est vide et que vous n’avez pas chargé d’iso dans votre lecteur cd. Votre nœud devrait être capable de récupérer un bail DHCP puis de recevoir les bons fichiers envoyés par le PXE. Si les requêtes DHCP échouent, vérifier vos configuration réseau. Votre serveur MAAS et votre nœud doivent se trouver dans le même réseau. L’interface correspondante sur le serveur MAAS doit aussi être configuré pour manager le DHCP et le DNS comme vu dans la partie précédente.

La reconnaissance du nœud par le serveur MAAS se fait en plusieurs étapes. Le premier boot va vous faire déboucher sur un mode « maas-enlisting-node ». Laissez tourner et votre serveur va s’éteindre de lui même.
 Une fois cette étape passée, vous pouvez vérifier dans la section « nodes » de MAAS que votre nœud est bien reconnu. Il apparait en gris. Son nom est un peu barbare aussi, mais c’est pas grave.

Par défaut, MAAS accepte tous les nœuds mais maintenant qu’il est accepté, il faut le rendre disponible pour un déploiement, plus quelques modifications mineurs.
 Dans un cas « normal », votre serveur MAAS se charge de faire booter vos machines via du Wake On Lan ou un système proprio. Comme j’utilise des VM, ça ne marche pas super bien et on devrait normalement utiliser virsh à la place du WOL. J’ai personnellement fait le choix de booter mes machines à la main au bon moment. Néanmoins, on va quand même éditer chacun de nos nœuds pour leur spécifier un type « Wake On Lan » et son adresse MAC associée.
 Retourner ensuite dans la vue générale des nœuds, sélectionnez les tous en grâce au menu déroulant, passez les en « commissioning » et en « fast installer ».

Vous pouvez booter vos nœuds une deuxième fois. Une fois le boot effectué, ceux ci devraient apparaitre en vert (« ready »)dans la section « node ».

###  Juju

On est maintenant prêt pour installer Juju et commencer les déploiement.

Sur le serveur MAAS, on va installer juju, l’initialiser et copier la clé privée générée à la place de votre clé privée par défaut.

```
apt-get install juju-core
juju init
cp ~/.juju/ssh/juju_id_rsa ~/.ssh/id_rsa`
```

En prévention du déploiement de Juju, on va renseigner en dur les IP de nos deux nœuds.

Editez le fichier /etc/hosts du serveur MAAS et ajoutez y la relation :

Exemple chez moi :

```
10.200.80.101 akegt.local akegt
10.200.80.102 x4ky7.local x4ky7
```

La configuration de Juju se trouve dans ~/.juju/environments.yaml. Supprimez tout ce qui s’y trouve et ajoutez ceci :

```
environments:
    maas-vsense:
        type: maas
        maas-server: http://IP-serveur-maas/MAAS
        maas-oauth: "MAAS-KEY"
        admin-secret: password-web-gui-juju
        default-series: trusty
```

Vous trouvez votre clé MAAS ici :
[![pref_maas-key](http://res.cloudinary.com/vsense/image/upload/v1435508379/pref_maas-key_fq9ab8.png)](http://res.cloudinary.com/vsense/image/upload/v1435508379/pref_maas-key_fq9ab8.png)

On peut maintenant boostraper Juju. Chez moi le boot pxe ne fonctionne pas, je dois donc démarrer « à la main » mes noeuds.

Sur votre serveur MAAS, lancez :

`juju bootstrap`

Juju va tenter de s’installer sur un de vos nœuds, au hasard, avec un message de ce type :

```
root@maas-server:~# juju bootstrap
Launching instance
WARNING picked arbitrary tools &{"1.18.4-trusty-amd64" "https://streams.canonical.com/juju/tools/releases/juju-1.18.4-trusty-amd64.tgz" "992e4244874ffec4af083cdeb58040420320f63ac6a3f7526c81d963fa4e53d6" %!q(int64=7389403)} - /MAAS/api/1.0/nodes/node-ea8ffe98-2d17-11e4-8a96-000c29f67438/ Waiting for address Attempting to connect to akegt.local:22 Attempting to connect to 10.200.80.101:22
```
Dans ce  cas, on boot le nœud correspondant à 10.200.80.101. Si vous ne savez pas lequel c’est, allumez les deux, le bon nœud bootera correctement en PXE, l’autre sera bloqué quasiment dès le début.

Le fast-installer devrait installer votre nœud rapidement. Une fois installé et le service ssh activé, vous devriez voir des « apt-get update/upgrade » apparaître sur votre serveur MAAS.

Si tout se passe bien, vous aurez ce message en fin de bootstrap et un nœud apparaîtra comme « allocated » (et en bleu) dans MAAS.

```
Bootstrapping Juju machine agent
Starting Juju machine agent (jujud-machine-0)
```

Il est possible que le bootstrap échoue pour un problème de résolution DNS. En effet, votre serveur DHCP a poussé l’IP du serveur MAAS comme DNS aux nœuds. Or notre serveur ne fait pas DNS. C’est un comportement qui doit pouvoir se modifier mais je n’ai pas trouvé comment. L’astuce est d’installé BIND sur votre serveur MAAS, d’éditer /etc/bind/named.conf.options et d’y ajouter un forwarder vers un DNS (8.8.8.8 par exemple)

```
forwarders {8.8.8.8;};
service bind9 restart
```

Vous pouvez relancer votre bootstrap après ça.

### Services OpenStack

On peut maintenant commencer à déployer des services OpenStack.

La commande à utiliser est « juju deploy ». Cette commande va à chaque fois provisionner un nouveau nœud. Or nous on en a que deux, on aimerait bien mutualiser un peu les ressources. Le but étant d’avoir un nœud « controller » et un nœud « compute ».
 La commande deploy peut prendre « –to machine » comme argument pour spécifier où installer le service. Cette commande est dangereuse car les services n’auront pas conscience de cohabiter, il ne faut utiliser le « –to » quand dans le cas où on est absolument sûr que les services ne se télescopent pas. Pour éviter tout problème, on va enfermer chaque service dans un container LXC. Léger et pratique. Chaque service aura son IP et ça simplifiera la création des relations ensuite.
 Lancez les commandes suivantes une par une et attendez que le service en question apparait comme « started » avec un « juju status votreService ». Vous pouvez tout lancer en même temps, mais la charge de votre nœud « controller » risque de monter en flèche.

```
juju deploy --to lxc:0 mysql
juju deploy --to lxc:0 keystone
juju deploy --to lxc:0 nova-cloud-controller
juju deploy --to lxc:0 glance
juju deploy --to lxc:0 rabbitmq-server
juju deploy --to lxc:0 openstack-dashboard
juju deploy --to lxc:0 cinder
```

Vous reconnaissez ici les services OpenStack traditionnellement installés sur un controlleur.

On va maintenant ce servir du deuxième nœud pour installer nova.

`juju deploy nova-compute`

Juju va souhaiter installer nova sur un deuxième nœud. Ça tombe bien on en a un. Si la partie LXC n’est plus présente ici, c’est bien évidemment parce que faire du KVM par dessus du LXC ça parait complètement absurde.

Un « juju status nova-compute » vous montre le service en pending et un « juju status 1″ vous montre qu’une deuxième machine est en « pending » et attend que vous bootiez votre deuxième nœud. Ce que vous pouvez dès maintenant effectuer.

Une fois que nova-compute est bien passé en « started », on va pouvoir ajouter des relations entre les services.

```
juju add-relation mysql keystone
juju add-relation nova-cloud-controller mysql
juju add-relation nova-cloud-controller rabbitmq-server
juju add-relation nova-cloud-controller glance
juju add-relation nova-cloud-controller keystone
juju add-relation nova-compute nova-cloud-controller
juju add-relation nova-compute mysql
juju add-relation nova-compute rabbitmq-server:amqp
juju add-relation nova-compute glance juju add-relation glance mysql
juju add-relation glance keystone
juju add-relation glance cinder
juju add-relation mysql cinder
juju add-relation cinder rabbitmq-server
juju add-relation cinder nova-cloud-controller
juju add-relation cinder keystone
juju add-relation openstack-dashboard keystone
```

Et c’est fini ! Pour le plaisir, on va installer l’interface web de Juju

`juju deploy --to lxc:0 juju-gui juju expose juju-gui`

Récupérer l’IP de votre juju-gui et on s’y connecte :

`juju status juju-gui`

Le mot de passe est celui défini dans le fichier ~/.juju/environments.yaml à la ligne *admin-secret*

Vous devriez arriver sur quelque chose comme ceci et vous pouvez voir que vos services sont UP ainsi que leurs relations.

[![relation](http://res.cloudinary.com/vsense/image/upload/h_235,w_300/v1435508377/relation_s8bwqn.png)](http://res.cloudinary.com/vsense/image/upload/v1435508377/relation_s8bwqn.png)

On va créer un mot de passe pour l’accès au dashboard Horizon

`juju set keystone admin-password="vsense"`

Vous pouvez maintenant accéder au dashboard Horizon en récupérant l’IP de votre dashboard

`juju status openstack-dashboard`

et en vous connectant en web sur http://IPdashboard/horizon/ et vous amuser avec OpenStack.

Enjoy ~.°
