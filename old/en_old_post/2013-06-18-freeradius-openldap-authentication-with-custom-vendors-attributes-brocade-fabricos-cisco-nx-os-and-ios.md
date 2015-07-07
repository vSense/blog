---
title: "FreeRADIUS: OpenLDAP authentication with custom vendors attributes (Brocade FabricOS, Cisco NX-OS and IOS)"
slug: freeradius-openldap-authentication-with-custom-vendors-attributes-brocade-fabricos-cisco-nx-os-and-ios
date_published: 2013-06-18T11:19:51.000Z
date_updated:   2015-06-28T17:19:59.000Z
tags: Brocade, Brocade, Cisco, Cisco, FreeRADIUS, FreeRADIUS, openLDAP, openLDAP, privileges, RADIUS, RADIUS, role, role, AAA, AAA
---


After days of research about how to integrate FreeRADIUS to an LDAP, I finally found several solutions to do what I wanted to. I am going to detail here the steps to follow in order to get a working configuration. The aim is to put in place a RADIUS authentication on several types of equipment, with different privileges levels. To keep the consistency, it’s better to integrate RADIUS with an existing user database, LDAP for example. Next, we need to give our users some rights, that’s where the VSA (Vendor Specific Attribute) are useful. If you are not familiar with RADIUS, I’ll explain more about it further on. But for now let’s talk about the LDAP.


# OpenLDAP

Our LDAP structure is the following:

![openLDAP-lab](http://res.cloudinary.com/vsense/image/upload/h_146,w_300/v1435508398/openLDAP-lab1_fnm18m.png)

OPS and ADMIN users are our test users, each will have a specific RADIUS profil. SWADMIN and SWOPERATOR are the LDAP groups and represents the RADIUS profiles, the attributes will be declared in those profiles. Our LAB was on CentOS 6 but it is easily usable for other distribution as well. We used one of the lastest version of LDAP which is not based on slapd.conf. I am not gonna explain how to build an LDAP from the beginning, there is a lot of pretty good tutorial out there. We will get back to LDAP post configuration after the RADIUS server configuration.


# FreeRADIUS

### What is RADIUS ?

RADIUS mainly allows centralized authentication. There can be multiple applications:

- Authentication et network access control via 802.1x (Login/Password, MAC filtering…)
- Access control to the hardware itself ( eg: for accessing CLI of a switch).

Thos is the last function we’re going to implement, it will allow us via the use of AAA (Authentication, Authoriation, Accounting) to:

- Authentication: If the user can access the equipment.
- Authorization: Level of access to the equipment.
- Accounting: What the user is doing

FreeRADIUS can work with several ways of authenticate the user: in standalone, with a text file containing the differents users and attributes, via an SQL database, an LDAP, PAM and others. Here we are going to use LDAP which is often available in most company and permits to keep a certain consistency with the users and avoid asynchronous users databases.

### FreeRADIUS Installation

[root@labfreeradius ~]# yum install freeradius freeradius-utils freeradius-ldap

Once the installation completed, configuration files are available in /etc/raddb.

### Encryption

FreeRADIUS can use different types of encryption which depend of the authentication architecture in place, you can check the compatibility matrix [here](http://deployingradius.com/documents/protocols/compatibility.html). Our password are stocked in an openLDAP and are hashed with salted SHA so we are going to use PAP to secure communication between the RADIUS Server and Client. PAP is based on a pre-shared key between client and server.

### Radiusd.conf

This is the main configuration file, no need to touch it for now.

### Client.conf

This file contains information about the RADIUS client and can be use to filtered which equipment can use the RADIUS server. There are 2 ways to declare clients:  
 Individually:

client 192.168.51.29 { secret = testing sortname = lab nastype = cisco }

Network:

client 192.168.51.0/24 { secret = testing sortname = labi nastype = cisco }

It is also in this file that we configure the pre-shared key. The nastype attribute must be chosen from the following according to hardware type:

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

This module can detect the hash used by a password, in openLDAP, passwd are stocked like: {SSHA} <hashed-passwd>. This module detect the hash to use the right one.

### module/ldap

This is where the LDAP parameters are stocked, you should create a user which can bind to the LDAP, for this LAB, we used an admin user but obvioulsy you want to use a specific user with less rights.

server = "ldap.lab" identity = "cn=admin,dc=lab" //admin credentials password = ************* basedn = "ou=users,dc=lab" // The leaf where users are filter = "(uid=%{%{Stripped-User-Name}:-%{User-Name}})" // Username parsing profile_attribute = "radiusProfileDN" // Special attribute which will point to a specific profil.

The purpose of « profile_attribute » is not to have to declare each attributes in each user. The attributes will be declare in generic profils which will then be associated to a user.

### site-enabled/default et site-enabled/inner-tunnel

In those file, we need to uncomment the LDAP in authentication and authorization parameters, I recommend you read the comments before doing anything to understand what it does and if you really need it.

### Accounting logs

Accounting logs are in /var/log/radius/radacct.

### Debug

To launch RADIUS in debug mode (you should do it whenever you change something), first make sure the service is stopped

service radiusd stop

Then launch it in debug mode:

radiusd -X


# RADIUS Attributes

RADIUS uses a list of attribute to exchange information about authentication type, which method to use… In our case, we will use mostly « service-type=NAS-prompt-access » because we want to login in to an equipment to get a prompt (CLI or Web Interface). Full attributes list is available [here](http://freeradius.org/rfc/attributes.html).

### VSA (Vendors Specifics Attributs)

RADIUS base attributes are often not enough to provide granular access to a specific device. More attributes exists and are called VSA (Vendor specific attributes). We want to split access in two profiles:

- <span style="line-height: 13px;">Full Access (Admin)</span>
- Read Only (Operator)

Each constructor plan, more or less specific attributes in the form of « {vendor}AVpair={reply attribute} ». In the following, we will see specifically Brocade and Cisco but you cna find more out there. Depending on your equipments, it is possible to reply more than one attribute by using operators:

- <span style="line-height: 13px;">« = » : send the first attribute.</span>
- « += » : send the attributes after the previous one.

FreeRADIUS comes with a list of predefined VSA in dictionaries located in /usr/share/freeradius.

### Cisco IOS

For IOS we are going to send 2 levels of privileges: 1 for operator and 15 for admin. The corresponding attributes are:

Cisco-AVPair+= "shell:priv-lvl=15" Cisco-AVPair+= "shell:priv-lvl=1"

### Cisco NX-OS

Cisco Nexus implement roles in complement of privilege levels like IOS:

- <span style="line-height: 13px;">network-admin and vdc-admin for admin account</span>
- network-operator and vdc-operator for operator account

The attributes are the following:

Cisco-AVPair+= "shell:roles= network-admin vdc-admin" Cisco-AVPair+= "shell:roles= network-operator vdc-operator"

### Brocade SAN Switch (Fabric OS)

For Brocade, FreeRADIUS does not have a dictionary, we need to create it manually, in /usr/share/freeradius, create the file « dictionary.brocade

# dictionary.brocade VENDOR Brocade 1588 BEGIN-VENDOR Brocade ATTRIBUTE Brocade-Auth-Role 1 string ATTRIBUTE Brocade-AVPairs1 2 string ATTRIBUTE Brocade-AVPairs2 3 string ATTRIBUTE Brocade-AVPairs3 4 string ATTRIBUTE Brocade-AVPairs4 5 string ATTRIBUTE Brocade-Passwd-ExpiryDate 6 string ATTRIBUTE Brocade-Passwd-WarnPeriod 7 string

Then edit the dictionary file « dictionnary » and add:

$INCLUDE dictionary.brocade

Now FreeRADIUS will be able to parse Brocade attributes. User management is more complex on Brocade FC switch:

For a full admin user:

Brocade-Auth-Role+= "admin" // User role Brocade-AVPairs1+= "HomeLF=128" // Main logical fabric Brocade-AVPairs2+= "LFRoleList=admin:1-128"// Admin of all fabrics Brocade-AVPairs3+= "ChassisRole=admin" // Admin of the chassis

For a simple user it is simpler:

Brocade-Auth-Role+= "user"


# OpenLDAP configuration


## Schema importation

We need to import the LDAP schema that come from FreeRADIUS before configuring LDAP. It is located in /usr/share/freeradius-« version »/example/openldap.schema/.

cp /usr/share/doc/freeradius-2.1.12/examples/openldap.schema /etc/openldap/schema/radius.schema cd /tmp mkdir converted_schema

Create a file named « schema-to-convert » which contains:

include /etc/openldap/radius.schema

Then:

slaptest -f /tmp/schema_to_convert -F /tmp/converted_schema

We need to modify the output LDIF file before importing it. Change the CN and DN:

dn: cn=radius,cn=schema,cn=config cn: radius

Then delete the last 7 lines and import it:

ldapadd -Y EXTERNAL -H ldapi:// -f /tmp/converted_schema/cn=config/cn=schema/cn={0}radius.ldif


## Create users and groups

Users and groups creation is done via LDIF files. Each files represents an LDAP object. We will have 2 groups and 2 users. There is different ways to use the attributes seen previously. One solution is to put them directly into the LDAP.

### swadmin.groups.lab.ldif

dn: cn=swadmin,ou=groups,dc=lab objectClass: groupOfNames objectClass: radiusprofile // Imported class cn: swadmin radiusReplyItem: Cisco-AVPair+= "shell:priv-lvl*15" radiusReplyItem: Cisco-AVPair+= "shell:roles* network-admin vdc-admin" radiusReplyItem: Brocade-Auth-Role+= "admin" radiusReplyItem: Brocade-AVPairs1+= "HomeLF=128" radiusReplyItem: Brocade-AVPairs2+= "LFRoleList=admin:1-128" radiusReplyItem: Brocade-AVPairs3+= "ChassisRole=admin" radiusServiceType: NAS-Prompt-User // Service-type we talked about earlier member:

### swoperator.groups.lab.ldif

dn: cn=swoperator,ou=groups,dc=lab objectClass: groupOfNames objectClass: radiusprofile cn: swoperator radiusReplyItem: Cisco-AVPair+= "shell:priv-lvl*1" radiusReplyItem: Cisco-AVPair+= "shell:roles* network-operator vdc-operator" radiusReplyItem: Brocade-Auth-Role+= "user" radiusServiceType: NAS-Prompt-User member:

### admin.users.lab.ldif

dn: uid=admin,ou=users,dc=labi uid: admin sn: admin cn: admin objectClass: inetOrgPerson objectClass: radiusprofile radiusprofileDN: cn=swadmin,ou=groups,dc=lab // Link to the profile we have just created. UserPassword: {SSHA}fd1hzvaHwNQLBTU7E6qJOSV54CQJQOar // Hashed user password

### ops.users.lab.ldif

dn: uid=ops,ou=users,dc=lab uid: ops sn: ops cn: ops objectClass: inetOrgPerson objectClass: radiusprofile radiusprofileDN: cn=swoperator,ou=groups,dc=labingenico UserPassword: {SSHA}fd1hzvaHwNQLBTU7E6qJOSV54CQJQOar

As you can see, the radiusProfileDN is used to link a user to a specific profile.

Another solution is to use the file /etc/raddb/users to send the attributes, the swadmin and swops groups will not contain radiusReplyItem. This method allow separation of RADIUS management and LDAP management because we can change the attributes without touching the LDAP.

### /etc/raddb/users

DEFAULT LDAP-Group == "swadmin" Filter-Id = "group_name=admin,shell-login-profile,user;", cisco-avpair += "shell:priv-lvl*15", cisco-avpair += "shell:roles* network-admin vdc-admin", Brocade-Auth-role += "admin", Brocade-AVPairs1 += "HomeLF=128", Brocade-AVPairs2 += "LFRoleList=admin:1-128", Brocade-AVPairs3 += "ChassisRole=admin", APC-Service-Type += 1, Auth-Type := LDAP DEFAULT LDAP-Group == "swoperator" cisco-avpair += "shell:priv-lvl*1", cisco-avpair += "shell:roles* network-operator vdc-operator", Brocade-Auth-role += "user", Auth-Type := LDAP DEFAULT Auth-Type := Reject


## Importation of users and groups

To import the LDIF files, use slapadd:

[root@labfreeradius ~]# ldapadd -D "cn=admin,dc=lab" -H ldapi:// -f /etc/openldap/ldif/ops.users.lab.ldif -W


# Enable RADIUS authentication

This step is quite simple if you know your devices. I am going to sum up it for Cisco and Brocade devices.

### Cisco IOS

We need to declare an AAA new model and a group server RADIUS:

aaa new-model aaa group server radius RADIGROUP server-private 192.168.51.26 auth-port 1812 acct-port 1813 key <key defined in client.conf> ip radius source-interface FastEthernet0

Then defined the authentication policy

aaa authentication login default group RADGROUP local aaa authorization console aaa authorization exec default group RADGROUP local aaa accounting exec default start-stop group RADGROUP

This allows the fallback to local authentication is the RADIUS server is not accessible

### Cisco Nexus NX-OS

Almost the same thing for NX-OS:

radius-server host 192.168.51.26 key <key defined in client.conf> authentication accounting aaa authentication login default group radius local aaa accounting default group radius local no aaa user default-role // disabled default role aaa authentication login error-enable // Errors login

### Cisco debugging

To debug RADIUS and AAA:

debug aaa all debuag radius all

Careful with the debug command, do not us « all » except if you are not in a production environment or you are sure of what you are doing.

### Brocade SAN FC Switch

La configuration se fait facilement via l’interface graphique en tant qu’administrateur (j’ai la flemme de faire des capture d’ecran).  
 Confiuration is done easily via the web interface, if you want to do it through CLI:

aaaconfig --add IP -conf radius -s KEY -a pap aaaconfig --authspec "radius;local"

I hope this article will answer some interrogation you may have about RADIUS. I did not find a lot of consistent articles about this particular subject so I hope I can avoid you days of research. Do not hesitate to contact me via mail or in comments.



