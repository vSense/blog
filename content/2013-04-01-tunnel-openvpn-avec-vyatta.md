---
title: Tunnel OpenVPN avec Vyatta
authors: Romain Guichard, Kevin Lefevre
about_author: Romain Guichard est ingenieur cloud @Osones
email: rguichard@vsense.fr
slug: tunnel-openvpn-avec-vyatta
date_published: 2013-04-01T17:19:39.000Z
date_updated:   2015-06-28T17:20:20.000Z
tags: OpenVPN, OVH, Vyatta
category: Réseau
---


Nous avions auparavant un VPS chez Virpus, un hébergeur américain dont le datacenter est situé à Houston au Texas. Un VPN était monté jusque là bas et nous sortions donc sur Internet avec une IP américaine, assez utile pour s’inscrire sur Google Music à l’époque ! Le problème c’est la latence, quand on reste en dessous des 100ms ça va, quand ça commence à dépasser les 300ms, ça devient vite désagréable. Maintenant que nos serveurs sont situés à Roubaix, ça devient bien plus intéressant.

Globalement les VPN ont deux usages, soit pour interconnecter de façon sécurisée deux réseaux, soit à fournir une porte de sortir sécurisée sur Internet. Interconnecter nos réseaux privés avec le LAN de l’ESX ne présente pas beaucoup d’intérêt, en revanche sortir sur Internet en contournant les limitations (filtrage par protocoles, par port ou par contenu) qui peuvent avoir été mises en place par votre opérateur/administrateur c’est plutôt sympa. Dans notre cas, il s’agit de notre école, qui bloque tout trafic UDP et pas mal de ports « non standards ». Et quand on a besoin de télécharger un torrent sur le campus ou de faire une partie de Minecraft, on est bien content d’avoir un VPN relativement rapide à disposition.

Les tunnels VPN sont montés directement sur le Vyatta bien que nous aurions pu utiliser [les virtuals appliances que proposent le site d’OpenVPN.](http://openvpn.net/index.php/access-server/download-openvpn-as-vm.html) Vyatta peut à la fois fonctionner comme client ou comme serveur, tout dépend de ce dont vous avez besoin. Lorsque nous avons organisé l’UTT Arena (LAN party homologuée, 300 joueurs, moins cette année là) au mois de mai dernier, nous utilisions le tunnel VPN pour permettre aux joueurs d’accéder aux serveurs Starcraft et League of Legends, Vyatta était utilisé en tant que client coté LAN, la porte de sortie était un autre serveur (hébergé aussi chez OVH). Sur notre architecture c’est le contraire, on sort par le Vyatta.

Vyatta intègre directement la possibilité de créer des interfaces de type « OpenVPN ». Leur configuration se fait grâce aux commandes de Vyatta, néanmoins toutes les options d’OpenVPN ne sont pas comprises et vous pouvez ajouter des options plus exotiques à votre configuration.

Voici un schéma du réseau mis en place :

![openvpn](http://res.cloudinary.com/vsense/image/upload/h_204,w_300/v1435508420/openvpn1_yu0vn1.png "openvpn")](http://blog.vsense.fr/wp-content/uploads/2012/07/openvpn.png)Tunnels (en bleu) OpenVPN avec Vyatta

Vyatta est donc notre serveur OpenVPN. Chaque client établi une connexion point-à-point avec le serveur, Vyatta fait office de serveur DHCP dans ce cas et fourni des adresses dans le réseau 10.0.1.0/24. La première adresse lui étant réservé.

Les options du tunnel VPN sont les suivantes :

- Protocole : TCP (préféré UDP si vous le pouvez)
- Port : 1863 (port utilisé par MSN, généralement ouvert sur les firewalls)
- Hashage : SHA1
- Chiffrement : AES256
- comp-lzo activée

Ce qui nous donne la configuration suivante :

```
openvpn vtun0 {        
    description TUNNEL-VPN        
    encryption aes256        
    hash sha1        
    local-port 1863        
    mode server        
    openvpn-option --comp-lzo        
    protocol tcp-passive        
    replace-default-route {        
    }        
    server {                  
        subnet 10.0.1.0/24            
        topology subnet        
    }        
    tls {            
        ca-cert-file /config/auth/ca.crt            
        cert-file /config/auth/vyatta.crt            
        dh-file /config/auth/dh1024.pem            
        key-file /config/auth/vyatta.key        
    }    
}

Bien entendu, n’oubliez pas de générer vos clés et certificats, pour Vyatta et pour les clients. Un petit tour sur [Openmaniak](http://openmaniak.com/openvpn_pki.php) si besoin est 😉 . Le dernier paramètre dont nous n’avons pas parlé est *replace-default-route*. Cet argument précise aux clients de changer leur passerelle par défaut et de la remplacer par le tunnel VPN. De cette façon, tout le trafic est routé par le tunnel et vous sortez sur Internet par l’IP publique de votre Vyatta.

On peut constater le lancement correcte de notre interface vtun0 en regardant le fichier /var/log/messages :

```
Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: Diffie-Hellman initialized with 1024 bit key
Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: /usr/bin/openssl-vulnkey -q -b 1024 -m <modulus omitted>
Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: TLS-Auth MTU parms [ L:1560 D:140 EF:40 EB:0 ET:0 EL:0 ]
Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: Socket Buffers: R=[87380->131072] S=[16384->131072]
Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: TUN/TAP device vtun0 opened
Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: TUN/TAP TX queue length set to 100
Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: /sbin/ifconfig vtun0 10.0.1.1 netmask 255.255.255.0 mtu 1500 broadcast 10.0.42.255
Jul 25 03:09:48 vyatta zebra[1709]: interface vtun0 index 9 <POINTOPOINT,NOARP,MULTICAST> added.
Jul 25 03:09:48 vyatta zebra[1709]: warning: PtP interface vtun0 with addr 10.0.1.1/32 needs a peer address
Jul 25 03:09:48 vyatta zebra[1709]: interface vtun0 index 9 changed <UP,POINTOPOINT,RUNNING,NOARP,MULTICAST>.
Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: Data Channel MTU parms [ L:1560 D:1450 EF:60 EB:135 ET:0 EL:0 AF:3/1 ]
Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: Listening for incoming TCP connection on [undef]
Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: TCPv4_SERVER link local (bound): [undef]
Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: TCPv4_SERVER link remote: [undef]
Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: MULTI: multi_init called, r=256 v=256
Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: IFCONFIG POOL: base=10.0.1.2 size=252
Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: MULTI: TCP INIT maxclients=1024 maxevents=1028 Jul 25 03:09:48 vyatta openvpn-vtun0[4409]: **Initialization Sequence Completed**
```

Il ne vous reste plus qu’à générer le configuration et les certificats pour vos clients. Voici un exemple de configuration fonctionnant avec notre serveur.

```
proto tcp-client
tls-client
remote 46.x.x.123
rport 1863
dev tun
ca ca.crt
cert romain.crt
key romain.key
cipher AES-256-CBC
auth SHA1
comp-lzo
verb 3
pull
```
Une fois le tunnel monté, il faut vérifier que votre route par défaut a bien été modifié par le VPN. Sous Windows : `route print`

Destination réseau    Masque réseau  Adr. passerelle   Adr. interface Métrique          
0.0.0.0          0.0.0.0        10.0.1.1        10.0.1.2     30

Notre route par défaut a désormais comme passerelle l’IP du Vyatta. Notre trafic est entièrement routé dans le tunnel VPN. Afin que vous sortiez réellement par le tunnel VPN, il faut que mettiez en place une translation NAT (du subnet 10.0.1.0/24 vers votre interface WAN) sur le Vyatta de façon à sortir avec l’IP publique de celui ci, référez vous à l’article sur [notre architecture OVH](http://blog.vsense.fr/architecture-ovh/ "Architecture OVH") (dernière partie) si besoin.

Une fois votre PKI en place, il est relativement simple et rapide de monter un tunnel VPN que ce soit pour accéder, depuis chez vous, à votre ordinateur du bureau ou bien pour sécuriser vos échanges avec votre serveur.

Enjoy ~.°
