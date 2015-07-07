---
title: Reduire un disque avec VMware Converter
authors: Romain Guichard, Kevin Lefevre
slug: reduire-un-disque-avec-vmware-converter
date_published: 2013-04-01T16:23:10.000Z
date_updated:   2015-06-28T17:20:24.000Z
tags: Converter, ESXi, SQL, VMware
---


En pleine migration d’espace de stockage en VMFS5, j’ai retrouvé hier une machine avec 80go d’espace libre et comme chez nous on est un peu radin sur le stockage, je voulais absolument les récupérer. Le disque n’était pas du tout fragmenté mais contenait une application métier ainsi qu’une base SQL associée qui prenait auparavant tout le disque à cause du mode de récupération complet et donc des fichiers de logs énormes. Du coup le disque n’était plus réductible en deçà de 80go, les fichiers $BitMap, repartis un peu partout sur le système de fichier NTFS bloquait le redimensionnement. Ces fichiers signalent les clusters disponibles sur un volume NTFS et ne se bougent apparemment pas si facilement. Je pense qu’il existe pas mal de solutions de défragmentation à froid mais je suis pas trop pour tester cela sur des serveurs en production.

Une solution est de réaliser un clone de la machine virtuelle avec VMware Converter (gratuit sur le site de VMware) et de convertir la machine virtuelle vers le même datacenter: c’est équivalent à créer un clone à chaud avec vSphere mais Converter vous laisse redimensionner les disques et récupérer de l’espace libre.

Je ne vais pas détailler toute la procédure d’utilisation de Converter, la documentation étant très correcte. Avant la fin de l’assistant de conversion, avant le resumé, vous pouvez modifier les options avancées:

![Screenshot converter](http://res.cloudinary.com/vsense/image/upload/h_131,w_300/v1435508424/convert1_yxlxp9.png "VMware Converter")Réduire l’espace disque avec Converter

Une fois la conversion exécutée, vous vous retrouvez avec un clone éteint de votre machine. Vous pouvez utiliser cette nouvelle machine telle qu’elle mais vous risquez de vous retrouver avec des problèmes de SID et de licences suivant les logiciels présents sur votre machine, attention également aux conflits DNS, Netbios et IP. Dans ce cas, utiliser sysprep.

Nous avons l’habitude de séparer le système et les applications sur les serveurs, dans cet exemple, j’utilisais un serveur d’impression Uniflow de Canon, qui supporte mal le clonage (problème de licence dû au changement de SID). L’application ainsi que la base étant sur un disque différent du système, pour plus de transparence, on remonte le nouveau disque sur l’ancienne machine :

- Démonter le disque redimensionné de la machine nouvellement créee.
- Démonter l’ancien disque de l’ancienne machine.
- Monter le nouveau disque sur l’ancienne machine à la place de l’ancien disque.
- Démarrer l’ancienne machine avec le nouveau disque.

L’opération a fonctionnée pour un serveur SQL souvent considéré comme sensible en ce qui concerne les opérations de migration. L’opération devrait également fonctionner dans le cas du disque système mais je n’ai pas eu l’occasion de tester.
