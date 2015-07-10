---
title: SSH "over" HTTPS
authors: Romain Guichard
about_author: Romain Guichard est ingenieur cloud @osones
email: rguichard@vsense.fr
slug: ssh-over-https
date_published: 2013-11-14T14:49:03.000Z
date_updated:   2014-09-02T19:09:37.000Z
tags: apache, https, mod_proxy, nginx, reverse proxy, shell, shellinabox, ssh
---


Dans la longue liste des systèmes administrables via une interface web, il y a FreeNAS qui est très bon. Très bien fait, on trouve de quoi tout faire et la CLI permet de faire ce qui n’est pas prévu par la GUI. La GUI possède un truc plutôt cool, **une interface en ligne de commande intégrée à la page web**. Même pas besoin d’avoir un client SSH, vous avez juste besoin d’un navigateur.  D’où le titre de l’article – *ssh « over » https* – ce n’est pas vraiment de l’encapsulation à proprement parler mais ça y ressemble.

Je cherchais un moyen d’obtenir le même genre de CLI intégré à une page web pour nos serveurs perso. Le but étant de s’affranchir du blocage du port 22 de certaines entreprises et d’éviter d’avoir à monter un tunnel VPN juste pour faire du SSH.

Un soft existe pour cela : **shellinabox**.

On va voir comment l’installer et en supplément utiliser votre serveur web (Apache et Nginx) comme reverse proxy et pouvoir taper sur ce shell via une url shell.votredomaine.tld. Shellinabox utilise le port 4200 par défaut et ce port est vraisemblablement aussi bloqué par votre entreprise.

On commence par aller chercher les sources (version 2.14 au 14/11/2013) sur google code :

`wget http://shellinabox.googlecode.com/files/shellinabox-2.14.tar.gz tar -zxvf shellinabox-2.14.tar.gz`

On regarde dans le fichier INSTALL.Debian la procédure. C’est très simple :

`i="$(dpkg-checkbuilddeps 2>&1 | sed -e 's/.*dependencies: //;t;d')" [ -n "$i" ] && sudo apt-get install $i dpkg-buildpackage apt-get install libssl0.9.8 libpam0g openssl`

dpkg-buildpackage remplace le combo configure/make/install. Il est possible qu’il vous manque des dépendances pour cette commande ainsi que pour dpkg-checkbuilddeps, n’hésitez pas à les lancer sans argument juste pour voir si le système couine ou pas.

Cela doit vous générer des .deb que vous installez avec « dpkg -i »

A ce niveau là vous pouvez voir avec netstat que votre système est en écoute sur le port TCP 4200. Vous avez donc accès à Shellinabox via **http://votreserveur:4200** ! 😀

Personnellement la première fois que j’ai vu ça j’étais content mais un peu moins à l’idée de balancer mon password via HTTP. Donc la première chose à faire c’est de faire passer tout le monde en HTTPS puis on s’affranchira du port 4200 en utilisant un reverse proxy. On passe donc sur la partie configuration de votre Apache/Nginx.

L’URL d’accès de notre shell sera **ssh.serveur.tld**, pour l’exemple.


## Apache

On va commencer avec Apache. On crée deux vhosts, un qui écoute sur le 80 et l’autre sur le 443. Personnellement je ne veux pas laisser le choix à l’utilisateur et je veux forcer le HTTPS. On utilise donc un **redirect** sur le vhost 80 qui renvoi vers le vhost 443.

```
<VirtualHost *:80>
    ServerName ssh.serveur.tld
    Redirect / https://ssh.serveur.tld
</VirtualHost>
```

Et pour la partie 443 on va utiliser une directive proxy_pass pour forwarder les requêtes arrivant sur ssh.serveur.tld:80 vers ssh.serveur.tld:4200. Deux petites choses à vérifier. Que vos DNS sont correctement configurés en interne et en externe, si votre shellinabox est sur la même machine que votre serveur web, le proxy_pass renverra vers localhost:4200. La deuxième chose est d’activer le module proxy d’Apache
```
a2enmod proxy proxy_http
service apache2 restart
```

On peut maintenant passer à la conf du vhost 443.

```
<VirtualHost *:443>
    ServerName ssh.serveur.tld
    SSLEngine on
    SSLCertificateFile /etc/apache2/ssl/cert.crt
    SSLCertificateKeyFile /etc/apache2/ssl/privatekey.key
    SSLProxyEngine on ProxyPass / http://ssh.serveur.tld:4200/
    ProxyPassReverse / http://ssh.serveur.tld:4200/
</VirtualHost>
```

N’oubliez pas le /  à la fin des directives ProxyPass, sinon ça ne marche pas !

On remarquera qu’on n’utilise plus de HTTPS. Le chiffrement se fait du client jusqu’au reverse proxy, au delà c’est en clair.

##  Nginx

Passons à Nginx. C’est pas plus compliqué, pas plus facile, le concept est le même. On fait un redirect du HTTP vers le HTTPS et on proxyse (ouh c’est moche comme mot…) du port 80 vers le port 4200.

```
server {    
    listen                      80;    
    server_name                 ssh.serveur.tld;    
    access_log                  /var/log/nginx/ssh.serveur.tld.access.log;    
    location / {        
        proxy_pass              http://ssh.serveur.tld;        
        proxy_redirect          off;        
        proxy_set_header        Host                $host;        
        proxy_set_header        X-Real-IP           $remote_addr;        
        proxy_set_header        X-Forwarded-For     $proxy_add_x_forwarded_for;    
    }
}
```

Et la conf HTTPS avec proxypass

```
server {    
    listen                  443;    
    server_name             ssh.serveur.tld;    
    access_log              /var/log/nginx/default.https.access.log;    

    ssl                     on;    
    ssl_certificate         /etc/nginx/ssl/cert.pem;    
    ssl_certificate_key     /etc/nginx/ssl/privatekey.key;    
    ssl_session_timeout     5m;    
    ssl_protocols           SSLv3 TLSv1;    
    ssl_ciphers ALL:!ADH:!EXPORT56:RC4+RSA:+HIGH:+MEDIUM:+LOW:+SSLv3:+EXP;    
    ssl_prefer_server_ciphers   on;    

    location / {        
        proxy_pass          http://ssh.serveur.tld;        
        proxy_redirect      off;        
        proxy_set_header    Host            $host;        
        proxy_set_header    X-Real-IP       $remote_addr;        
        proxy_set_header    X-Forwarded-For $proxy_add_x_forwarded_for;    
    }
}
```

Et voilà vous avez donc un shell dans votre page web pour administrer votre serveur. J’ai détecté quelques problèmes avec certaines navigateurs. IE plante lamentablement, Firefox a du mal à faire passer les / et les : c’est assez embêtant pour un shell. Chrome et Chromium font parfaitement leur boulot.
