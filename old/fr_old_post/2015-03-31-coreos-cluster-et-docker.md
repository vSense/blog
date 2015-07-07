---
title: CoreOS, cluster et docker
slug: coreos-cluster-et-docker
date_published: 2015-03-31T16:54:10.000Z
date_updated:   2015-04-02T10:10:15.000Z
tags: cloud, cloud-config, cluster, container, coreos, docker, etcd, fleet
---


CoreOS est une distribution Linux minimaliste. Son but est de permettre le déploiement massif de services en intégrant nativement des outils comme fleet pour la gestion des clusters et docker pour la gestion des applications.

CoreOS est une distribution orientée cloud, elle ne fonctionne pas sans Internet car ses mises à jour sont poussées directement dans le système sans action utilisateur. Créer ou rejoindre un cluster avec etcd nécessite aussi un accès Internet. CoreOS se distingue aussi par le fait qu’il ne dispose pas de gestionnaire de paquets, en fait vous ne pouvez rien installer. Toute application doit passer par un container docker dans lequel vous êtes libre de faire ce dont vous avez besoin.

Dernier point qui diffère des Linux actuels, le système d’init utilisé par CoreOS est systemd alors que Debian utilise encore le vieil init de System V. Cela est en train de changer et Debian a officiellement annoncé que systemd serait l’init par défaut de Debian Jessie.  
 Sur le principe, au lieu de faire ceci :

/etc/init.d/monService start

Vous ferez :

systemctl start monService.service

Ces services sont appelés « unit » sous systemd et leur définition dans des fichiers texte est bien plus simples et puissantes que ce que l’on connaissait avec l’init de System V.

Voilà pour l’introduction de CoreOS.

Comme la plupart des OS modernes, CoreOS offre la possibilités d’être configuré au boot par l’intermédiaire d’un fichier cloud-config. Ce fichier au format YAML permet de définir les paramètres de notre système (IP, unit, clé ssh etc).  
 Malheureusement les produits VMware ne permettent pas de passer un fichier cloud-config à une vm. Il faut pour cela le passer via un fichier ISO monté dans le lecteur virtuel.  
 La procédure pour VMware se trouve [ici ](http://www.chrismoos.com/2014/05/28/coreos-with-cloud-config-on-vmware-esxi)

Ne reprenez pas le cloud-config du tuto, nous allons en générer un nouveau.

 

### Etcd

Le premier élément du système de cluster de CoreOS est etcd. Etcd est un système de clé/valeur distribué. Il prend en charge la gestion des noeuds dans le cluster. Etcd est installé sur tous les noeuds d’un cluster et son système distribué lui permet d’être requêté par n’importe quel container du cluster.

### Fleet

Fleet est l’orchestrateur du cluster. Il place les containers, gère les dépendances et les conflits entre les containers. Son rôle est de gérer systemd mais au niveau du cluster.

### Mise en cluster

Pour créer un cluster il nous faut récupérer une clé pour la découverte des noeuds :

curl -w "\n" 'https://discovery.etcd.io/new?size=X'

Avec X le nombre de noeuds initialement présents dans le cluster. On récupère une URL du type https://discovery.etcd.io/3135e6ea19cf3135e6ea19cf.

Pour nous connecter à nos noeuds, une clé ssh serait la bienvenue :

ssh-keygen -b 2048 -f ~/coreosPrivateKey.key

On peut commencer à rédiger notre fichier cloud-config.

Tout d’abord un fichier cloud-config commence toujours par #cloud-config et viennent ensuite différentes sections, chacune configurant une partie du système :

#cloud-config ssh_authorized_keys:   - ssh-rsa VOTRE_CLE_PUBLIQUE core@coreos coreos:   etcd:     discovery: VOTRE_URL         addr: 10.0.0.100:4001     peer-addr: 10.0.0.100:7001     peer-election-timeout: 3000     peer-heartbeat-interval: 600   units:     - name: etcd.service       command: start     - name: fleet.service       command: start     - name: dhcpcd.servic       command: stop     - name: 00-ens192.network       runtime: true       content: |         [Match]         Name=ens192         [Network]         DNS=8.8.8.8         Address=10.0.0.100/24         Gateway=10.0.0.254

Quelques petites explications. Comme VMware n’offre pas les mêmes possibilités qu’un cloud public comme DigitalOcean ou une infra OpenStack, on est obligé de s’adapter. On voit dans mes units que je désactive le dhcp. Par défaut CoreOS utilise bien évidemment son DHCP, mais le problème est que j’ai besoin de connaître cette IP pour la donner à etcd.  
 Dans un cas « normal », il faut laisser le DHCP fonctionner et remplacer votre IP dans « addr » et « peer-addr » par « $private_ip ». Cette variable sera automatiquement remplacé par votre IP, mais pas chez VMware ^^  
 Donc on triche, on enlève le DHCP, on force une IP sur notre interface et on l’annonce dans etcd.

A noter que du fait de l’impossibilité d’utiliser cette variable et de fixer une IP, ce cloud-config n’est pas commun à tous nos noeuds, il faudra en créer un par noeud en changeant l’IP là où c’est nécessaire.

Une fois que les cloud-config sont prêts et placer dans les lecteurs virtuels, on peut démarrer nos VM.  
 Une fois démarré, vous devriez pouvoir accéder au premier noeud sur 10.0.0.100

Si il s’agit du premier noeud à démarrer, la commande « systemctl status etcd -l » devrait vous monter son élection en tant que master :

Mar 27 15:29:40 coreos-node1 etcd[8759]: [etcd] Mar 27 15:29:40.811 INFO      | ccc095d945964a97d95b2f0377a41e: state changed from 'follower' to 'candidate'. Mar 27 15:29:40 coreos-node1 etcd[8759]: [etcd] Mar 27 15:29:40.811 INFO      | ccc095d945964a97d95b2f0377a41e: state changed from 'candidate' to 'leader'. Mar 27 15:29:40 coreos-node1 etcd[8759]: [etcd] Mar 27 15:29:40.811 INFO      | ccc095d945964a97d95b2f0377a41e: leader changed from '' to 'ccc095d945964a97d95b2f0377a41e'.

Et sur le second noeud :

Mar 27 15:30:29 coreos-node2 etcd[9523]: [etcd] Mar 27 15:30:29.001 INFO      | Send Join Request to http://10.0.0.100:7001/join Mar 27 15:30:29 coreos-node2 etcd[9523]: [etcd] Mar 27 15:30:29.026 INFO      | ac2619b7463c4f41bfccd7b49a6aa8 joined the cluster via peer 10.0.0.100:7001 Mar 27 15:30:29 coreos-node2 etcd[9523]: [etcd] Mar 27 15:30:29.028 INFO      | etcd server [name ac2619b7463c4f41bfccd7b49a6aa8, listen on :4001, advertised url http://10.0.0.101:4001] Mar 27 15:30:29 coreos-node2 etcd[9523]: [etcd] Mar 27 15:30:29.028 INFO      | peer server [name ac2619b7463c4f41bfccd7b49a6aa8, listen on :7001, advertised url http://10.0.0.101:7001] Mar 27 15:30:29 coreos-node2 etcd[9523]: [etcd] Mar 27 15:30:29.028 INFO      | ac2619b7463c4f41bfccd7b49a6aa8 starting in peer mode Mar 27 15:30:29 coreos-node2 etcd[9523]: [etcd] Mar 27 15:30:29.029 INFO      | ac2619b7463c4f41bfccd7b49a6aa8: state changed from 'initialized' to 'follower'. Mar 27 15:30:29 coreos-node2 etcd[9523]: [etcd] Mar 27 15:30:29.610 INFO      | ac2619b7463c4f41bfccd7b49a6aa8: state changed from 'follower' to 'snapshotting'. Mar 27 15:30:29 coreos-node2 etcd[9523]: [etcd] Mar 27 15:30:29.648 INFO      | ac2619b7463c4f41bfccd7b49a6aa8: peer added: 'ccc095d945964a97d95b2f0377a41e'

Et sur n’importe quel noeud, on peut voir la liste des machines dans le cluster :

$ fleetctl list-machines MACHINE         IP              METADATA ac2619b7...     10.0.0.101     - ccc095d9...     10.0.0.100     -

Maintenant que notre cluster est up and running, on va pouvoir créer nos units (= nos applications) et les pousser sur le cluster.

On va commencer par un serveur web nginx et on va utiliser l’image nginx du repository vSense (vsense/nginx). Nginx est un serveur de web et il est extrêmement courant d’avoir plusieurs frontaux web, il faut donc prévoir notre fichier d’unit comme un template qui permettra de créer plusieurs instances de notre Nginx.

Un unit file ressemble à ceci :

core@coreos-node1 /etc/systemd/system $ cat nginx@.service [Unit] Description=Nginx-frontend After=docker.service Requires=docker.service [Service] TimeoutStartSec=0 ExecStartPre=-/usr/bin/docker kill nginx ExecStartPre=-/usr/bin/docker rm nginx ExecStartPre=/usr/bin/docker pull vsense/nginx ExecStart=/usr/bin/docker run -rm --name nginx -p 80:80 vsense/nginx ExecStop=/usr/bin/docker stop nginx [X-Fleet] Conflicts=nginx@*.service

Noter bien que par rapport à une commande docker run « classique », le paramètre « -d » n’apparait pas. En effet, en mode détaché, le container n’est pas lancé comme un enfant du processus de l’unit et se coupe après quelques secondes d’exécution.  
 On submit ensuite l’unit à fleet et on la lance :

```
<code class="language-sh" data-lang="sh">fleetctl submit nginx@.service
fleetctl start nginx@1
fleetctl start nginx@2
fleetctl list-units
UNIT                    MACHINE                 ACTIVE  SUB
nginx@1.service        ccc095d9.../10.0.0.100 active  running
nginx@2.service        ac2619b7.../10.0.0.101 active  running

```

Nos deux containers ont bien été lancés sur deux noeuds différent grâce à la directive « conflicts ». Cette directive permet aussi de lier des containers et de toujours les laisser sur le même host ou bien de lancer un container sur un host qui respecte certaines metadata (lieu géographiques, type de plateforme etc) fournies dans un cloud-config.

 

La section X-Fleet de notre unit file accepte plusieurs paramètres pour le placement de nos containers :

- MachineID <host> : Sur l’host identifié par son nom
- MachineOf <unit> : Sur l’host faisant tourner <unit>
- MachineMetadata : Sur le/les host(s) matchant les metadata spécifiées
- Conflicts <unit> : Élimine les hosts faisant tourner <unit>
- Global =true : Fait tourner le container sur tous les hosts du cluster



