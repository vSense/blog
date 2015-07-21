---
title: "FreeRADIUS OpenLDAP authentification : customs vendor-attributes, Brocade FabricOS - Cisco NX-OS - IOS"
authors: Kevin Lefevre
about_author: Kevin Lefevre est ingenieur cloud @Osones
email: klefevre@vsense.fr
slug: freeradius-openldap
date_published: 2013-06-18T11:19:51.000Z
date_updated:   2015-06-28T17:19:59.000Z
tags: AAA, Brocade, Cisco, FreeRADIUS, openLDAP, RADIUS, ldap, annuaire, authentification
category: Système
---


Après des jours de recherche sur comment intégrer FreeRADIUS à un annuaire LDAP, j’ai enfin trouvé quelques solutions pour faire ce que je recherchais. Je vais détailler ici les étapes à suivre pour avoir une configuration fonctionnelle. L’objectif est de réaliser une authentification FreeRADIUS sur différents types d’équipements, dans le but d’obtenir un accès (CLI ou GUI) avec un niveau de privilèges prédéfini. Par soucis d’intégration, nous souhaitions réaliser cette authentification sur le LDAP déjà en place.  Par la suite, l’objectif est d’utiliser les VSA (Vendor Specific Attribute) pour donner à un certain groupe d’utilisateurs des privilèges d’administrateur ou d’opérateur. Si vous ne connaissez pas trop RADIUS, je vais le détailler par la suite.


# Préparation d’OpenLDAP

Nous allons implémenter la structure LDAP suivante:

![openLDAP-lab](http://res.cloudinary.com/vsense/image/upload/h_146,w_300/v1435508398/openLDAP-lab1_fnm18m.png)

Les utilisateurs admin et ops sont nos utilisateurs de test qui auront pour chacun un profil RADIUS différent. Les groupes swadmin et swoperator représentent les profils RADIUS et contiendront tous les attributs. Le LAB a été réalisé sur CentOS mais est facilement dérivable sur d’autres distributions, nous avons utilisé une des dernières version d’OpenLDAP qui ne s’appuie pas sur slapd.conf. La procédure si dessous est inspirée de [l’article de 404blog](http://www.404blog.net/?p=253). Je vous recommande de suivre [l’article](http://www.404blog.net/?p=253) en vous arrêtant avant l’ajout de schéma afin d’avoir une configuration LDAP fonctionnelle qui recoupe notre exemple ainsi que la configuration souhaitée de votre coté. Nous reviendrons à la fin sur la configuration des groupes et utilisateurs de notre LDAP mais tout d’abord nous devons configurer le serveur FreeRADIUS.


# FreeRADIUS

### Qu’est ce que RADIUS ?

RADIUS permet le plus souvent l’authentification d’équipement de façon centralisée. Il peut y avoir plusieurs contextes à l’utilisation d’un serveur RADIUS notamment:

- Authentification et contrôle d’accès au réseau via le protocole 802.1x (Filtrage MAC, Couple login/password).
- Contrôle d’accès à l’équipement en lui même (accès CLI d’un switch par exemple).

C’est cette deuxième fonction qui va nous intéresser puisqu’elle va nous permettre via l’utilisation du AAA (Authentication, Authorization, Accounting) de :

- Authentication: vérifier que l’utilisateur peut se connecter à l’équipement.
- Authorization: Avec quel niveau de privilège.
- Accounting: Ce qu’il fait sur l’équipement.

FreeRADIUS peut fonctionner de plusieurs façons, seul, avec un ficher texte regroupant les différents utilisateurs et attributs, via une base SQL ou un annuaire LDAP et bien d’autres. C’est cette dernière méthode que nous allons utiliser car souvent un annuaire LDAP est déjà présent en entreprise, du coup autant l’utiliser pour garder une certaine centralisation des utilisateurs et ainsi éviter les désynchronisations entre les différentes bases d’utilisateurs à maintenir.

### Installation de FreeRADIUS

`[root@labfreeradius ~]# yum install freeradius freeradius-utils freeradius-ldap`

Une fois l’installation effectuée, les fichiers de configuration sont présents dans /etc/raddb.

### Chiffrement

FreeRADIUS peut utiliser différents types de chiffrement afin de sécuriser les différents échanges. La méthode choisie diffère selon le type d’architecture, une matrice de compatibilité est présente [ici](http://deployingradius.com/documents/protocols/compatibility.html). Dans notre cas, nous souhaitons authentifier nos utilisateurs via un annuaire LDAP qui stocke les mots de passe utilisateurs hashés en SSHA, nous allons donc utiliser PAP pour les communications entre le serveur RADIUS et le client (les switchs par exemple). L’échange d’informations sera sécurisé via une clé partagée entre le serveur et le client comme nous le verrons par la suite.

### Radiusd.conf

C’est le fichier de configuration principal, n’y touchez pas pour le moment.

### Client.conf

C’est le fichier qui contiendra les informations relatives aux clients RADIUS. Vous pouvez déclarer les clients de différentes façons.

Individuellement:

client 192.168.51.29 { secret = testing sortname = lab nastype = cisco }

Par réseaux:

client 192.168.51.0/24 { secret = testing sortname = labi nastype = cisco }

C’est dans les clients que vous déclarez la clé partagée pour fournir le chiffrement pendant l’authentification. Le nastype doit être configuré suivant les attributs disponibles dans le fichier client.conf:

- cisco
- computone
- livingston
- max40xx
- multitech
- netserver
- pathras
- patton
- portslavetc
- usrhiper
- other

### module/pap

Ce module permet de détecter automatiquement le hash utilisé par un mot de passe donné. Dans notre LDAP, les mots de passe sont stockés de la façon suivante: {SSHA} <hashed-passwd>. Le module permet de détecter le {SSHA}  pour utiliser le bon hachage.

### module/ldap

C’est ici que l’on déclare les paramètres LDAP, vous devez déclarer un utilisateur qui peut s’authentifier sur le LDAP, dans ce lab nous avons utilisé admin mais je vous recommande de créer un utilisateur avec des droits restreints à la lecture des utilisateurs et groupes dont vous avez besoin:

```
server = "ldap.lab" identity = "cn=admin,dc=lab" //admin credentials password = *************
basedn = "ou=users,dc=lab" // La branche où se trouve les utilisateurs
filter = "(uid=%{%{Stripped-User-Name}:-%{User-Name}})" // Permet de parser le username
profile_attribute = "radiusProfileDN" // Nommer un attribut spécial qui renverra vers un profil particulier.
```

L’intérêt d’utiliser le profile_attribute est de ne pas avoir à déclarer les attributs dans tous les utilisateurs mais de créer des groupes qui servirons de profils génériques associés à chaque utilisateur. Le radiusProfileDN pointera sur le profil lié à l’utilisateur.

### site-enabled/default et site-enabled/inner-tunnel

Dans ces fichiers, vous devez décommenter « LDAP » dans les paramètres d’authentification et d’authorization, je vous recommande de rechercher « LDAP » dans ces fichiers et de lire les commentaires associés pour bien comprendre ce que vous faîtes et si cela correspond à vos besoins.

### Logs Accounting

Les logs d’accounting sont présents dans `/var/log/radius/radacct`.

### Debug

Pour lancer RADIUS en mode debug (ce que je vous recommande de faire pour chaque étape de test), tout d’abord assurez vous que le service est bien arrêté:

`service radiusd stop`

Puis lancer RADIUS en mode debug:

`radiusd -X`


# Les attributs RADIUS

Radius utilise une liste d’attributs pour échanger des informations à propos du type d’authentification, la méthode utilisée etc. Dans notre cas, nous utiliserons principalement l’attribut « service-type=NAS-prompt-access » qui signifie que nous souhaitons nous authentifier sur l’équipement et obtenir un accès (CLI ou GUI). Une liste des différents attributs est disponible [ici](http://freeradius.org/rfc/attributes.html).

### Les VSA (Vendors Specifics Attributs)

De base, RADIUS cherche un utilisateur et un mot de passe puis envoi un paquet access-accept pour donner un accès à l’utilisateur. Il existe d’autres attributs interprétables par FreeRADIUS, il s’agit des attributs personnalisés des différents fournisseurs. Par exemple, nous souhaitons diviser nos utilisateurs en 2 groupes:

- Contrôle total (Admin)
- Lecture seule (Operator)

Chaque fournisseur prévoit (plus ou moins) des attributs spécifiques de la forme « {vendor}AVpair={reply attribute} ». Je vais développer par la suite dans le cadre de 2 constructeurs: Cisco et Brocade. Il est possible de répondre autant d’attributs qu’on le souhaite via différents opérateurs:

- « = » : envoie l’attribut.
- « += » : envoie l’attribut en plus du précédent.

FreeRADIUS contient des dictionnaires intégrés de plusieurs constructeurs qui se trouvent dans /usr/share/freeradius.

### Cisco IOS

Pour IOS, nous allons envoyer 2 niveaux de privilèges: 1 pour operator et 15 pour admin. Les attributs sont:

```
Cisco-AVPair+= "shell:priv-lvl=15"
Cisco-AVPair+= "shell:priv-lvl=1"
```

### Cisco NX-OS

Dans le cadre des Cisco Nexus, ce ne sont plus des niveaux de privilège mais des rôles attribués aux utilisateurs. Chaque utilisateur aura 2 rôles:

- network-admin et vdc-admin pour l’admin
- network-operator et vdc-operator pour l’operator

Les attributs sont les suivants:

```
Cisco-AVPair+= "shell:roles= network-admin vdc-admin"
Cisco-AVPair+= "shell:roles= network-operator vdc-operator"
```

### Brocade SAN Switch (Fabric OS)

Dans le cadre de Brocade, FreeRADIUS ne contient pas de dictionnaire, nous devons en créer un manuellement, dans /usr/share/freeradius, créer un fichier « dictionnary.brocade »:

```
# dictionary.brocade
VENDOR          Brocade         1588

BEGIN-VENDOR    Brocade

ATTRIBUTE       Brocade-Auth-Role           1   string
ATTRIBUTE       Brocade-AVPairs1            2   string
ATTRIBUTE       Brocade-AVPairs2            3   string
ATTRIBUTE       Brocade-AVPairs3            4   string
ATTRIBUTE       Brocade-AVPairs4            5   string
ATTRIBUTE       Brocade-Passwd-ExpiryDate   6   string
ATTRIBUTE       Brocade-Passwd-WarnPeriod   7   string
```

Ensuite, éditer le fichier « dictionnary » et ajouter:

`$INCLUDE dictionary.brocade`

Maintenant FreeRADIUS pourra interpréter les attributs Brocade. Le management des utilisateurs sur Fabric OS est un peu complexe car il y a beaucoup de rôles différents.

Pour un utilisateur entièrement administrateur les attributs sont:

```
Brocade-Auth-Role+= "admin" // Role de l'utilisateur
Brocade-AVPairs1+= "HomeLF=128" // Principale logical fabric
Brocade-AVPairs2+= "LFRoleList=admin:1-128"// L'utilisateur peut administrer toutes les fabric
Brocade-AVPairs3+= "ChassisRole=admin" // Le rôle châssis admin permet d’être administrateur partout sur le switch
```

Pour un utilisateur en lecture seule, c’est plus simple:

`Brocade-Auth-Role+= "user"`


# Configuration d’openLDAP

## Importation du schéma

Nous avons besoin d’importer le schema LDAP de FreeRADIUS avant de commencer. Le schéma LDAP se trouve dans /usr/share/freeradius-« version »/example/openldap.schema/.

`cp /usr/share/doc/freeradius-2.1.12/examples/openldap.schema /etc/openldap/schema/radius.schema cd /tmp mkdir converted_schema`

Créer un fichier intitulé par exemple « schema-to-convert » qui contient:

`include /etc/openldap/radius.schema`

Ensuite faites:

`slaptest -f /tmp/schema_to_convert -F /tmp/converted_schema`

La sortie est un fichier LDIF que nous avons besoin de modifier avant d’importer. Modifier le DN et CN pour ressembler à:

`dn: cn=radius,cn=schema,cn=config cn: radius`

Ensuite supprimer les 7 dernières lignes du fichier puis l’importer:

`ldapadd -Y EXTERNAL -H ldapi:// -f /tmp/converted_schema/cn=config/cn=schema/cn={0}radius.ldif`

## Création des utilisateurs et groupes

La création des utilisateurs se fait via des fichiers LDIF, chaque fichier représente un objet LDAP, comme sur le schéma présenté au début de l’article, nous aurons 2 groupes et 2 utilisateurs dans lesquels nous retrouvons les attributs vus précédemment . Il existe différentes façons d’utiliser les attributs, une solution est de le mettre directement dans l’annuaire LDAP:

### swadmin.groups.lab.ldif

```
dn: cn=swadmin,ou=groups,dc=lab
objectClass: groupOfNames
objectClass: radiusprofile // que nous venons d'importer dans le LDAP
cn: swadmin
radiusReplyItem: Cisco-AVPair+= "shell:priv-lvl*15"
radiusReplyItem: Cisco-AVPair+= "shell:roles* network-admin vdc-admin"
radiusReplyItem: Brocade-Auth-Role+= "admin"
radiusReplyItem: Brocade-AVPairs1+= "HomeLF=128"
radiusReplyItem: Brocade-AVPairs2+= "LFRoleList=admin:1-128"
radiusReplyItem: Brocade-AVPairs3+= "ChassisRole=admin"
radiusServiceType: NAS-Prompt-User // le service type vu précédemment
member:
```

###  swoperator.groups.lab.ldif

```
dn: cn=swoperator,ou=groups,dc=lab
objectClass: groupOfNames
objectClass: radiusprofile cn: swoperator
radiusReplyItem: Cisco-AVPair+= "shell:priv-lvl*1"
radiusReplyItem: Cisco-AVPair+= "shell:roles* network-operator vdc-operator"
radiusReplyItem: Brocade-Auth-Role+= "user"
radiusServiceType: NAS-Prompt-User // le service type vu précédemment member:
```

### admin.users.lab.ldif

```
dn: uid=admin,ou=users,dc=labi
uid: admin
sn: admin
cn: admin
objectClass: inetOrgPerson
objectClass: radiusprofile // Importé précédemment
radiusprofileDN: cn=swadmin,ou=groups,dc=lab // L'objet qui contient les attributs de l'utilisateur
UserPassword: {SSHA}fd1hzvaHwNQLBTU7E6qJOSV54CQJQOar // Le password hashé de l'utilisateur
```

### ops.users.lab.ldif

```
dn: uid=ops,ou=users,dc=lab
uid: ops
sn: ops
cn: ops
objectClass: inetOrgPerson
objectClass: radiusprofile
radiusprofileDN: cn=swoperator,ou=groups,dc=labingenico
UserPassword: {SSHA}fd1hzvaHwNQLBTU7E6qJOSV54CQJQOar
```
Comme vous pouvez le voir, nous utilisons l’attribut radiusProfileDN que nous avons défini dans le module LDAP de FreeRADIUS, pour donner un lien vers le profil de l’utilisateur.

Une autre solution consiste à utiliser le fichier /etc/raddb/users pour renvoyer les attributs, les group swadmin et swops ne contiendront pas de radiusReplyItem. Cela permet de bien separer le LDAP et de modifier plus facilement les attributs sans toucher au LDAP par la suite:

### /etc/raddb/users

```
DEFAULT LDAP-Group == "swadmin"
Filter-Id = "group_name=admin,shell-login-profile,user;",
cisco-avpair += "shell:priv-lvl*15",
cisco-avpair += "shell:roles* network-admin vdc-admin",
Brocade-Auth-role += "admin", Brocade-AVPairs1 += "HomeLF=128",
Brocade-AVPairs2 += "LFRoleList=admin:1-128",
Brocade-AVPairs3 += "ChassisRole=admin",
APC-Service-Type += 1,
Auth-Type := LDAP

DEFAULT LDAP-Group == "swoperator"
cisco-avpair += "shell:priv-lvl*1",
cisco-avpair += "shell:roles* network-operator vdc-operator",
Brocade-Auth-role += "user",
Auth-Type := LDAP

DEFAULT Auth-Type := Reject
```

## Importation des utilisateurs et groupes

Pour importer les fichier LDFI créés précédemment, utilisez slapadd:

`[root@labfreeradius ~]# ldapadd -D "cn=admin,dc=lab" -H ldapi:// -f /etc/openldap/ldif/ops.users.lab.ldif -W`

Nous utilisons le compte admin pour nous authentifier sur le LDAP.


# Activer RADIUS sur les équipements

Cette étape est relativement simple si vous êtes familiés avec vos équipements mais je vais résumer brièvement les étapes d’activation sur Cisco et Brocade.

### Cisco IOS

Vous devez déclarer un aaa new-model ainsi qu’un groupe de serveurs RADIUS:

```
aaa new-model
aaa group server radius RADIGROUP server-private 192.168.51.26 auth-port 1812 acct-port 1813 key <la clé définie dans le fichier client.conf>
ip radius source-interface FastEthernet0
```

Ensuite nous devons définir la politique d’authentification:

```
aaa authentication login default group RADGROUP local
aaa authorization console
aaa authorization exec default group RADGROUP local
aaa accounting exec default start-stop group RADGROUP
```

Cela permet l’authentification RADIUS et le fallback vers l’authentification locale si le serveur n’est pas accessible.

### Cisco Nexus NX-OS

Presque la même chose que pour IOS, aaa et politique de securité:

```
radius-server host 192.168.51.26 key <la clé définie dans le fichier client.conf> authentication accounting
aaa authentication login default group radius local
aaa accounting default group radius local
no aaa user default-role // desactive le role par defaut
aaa authentication login error-enable // log les erreurs
```

### Cisco debugging

Pour debugger RADIUS et le AAA:

`debug aaa all debuag radius all`

### Brocade SAN FC Switch

La configuration se fait facilement via l’interface graphique en tant qu’administrateur (j’ai la flemme de faire des capture d’ecran).

J’espère que cet article répondra à un bon nombre d’interrogations sur l’authentification RADIUS, je n’ai pas trouvé d’articles consistent sur ce sujet en particulier, donc j’espère que ce concentré d’informations pourra aider certaines personnes et leur éviter une journée de recherches ![:)](http://blog.vsense.fr/wp-includes/images/smilies/simple-smile.png) N’hésitez pas à me contacter par mail ou commentaires.
