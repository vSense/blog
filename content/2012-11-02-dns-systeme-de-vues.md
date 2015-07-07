---
title: DNS - Système de vues
slug: dns-systeme-de-vues
date_published: 2012-11-02T01:05:51.000Z
date_updated:   2014-09-02T19:07:19.000Z
tags: Bind, Bind, debian, debian, DNS, DNS, domaine, vues
---


Lorsque l’on possède des serveurs dans un LAN accessible aussi depuis Internet (NAT/PAT), il est important que votre serveur DNS vous donne la bonne IP du serveur en fonction de l’origine de la requête. Si elle vient de l’internet vous aurez l’IP publique du serveur, si la requête provient du LAN, vous aurez son IP privée.

Une solution à ce problème consisterait à utiliser deux serveurs de noms. Vous pourriez par exemple devoir utiliser le nom de domaine serveur.lan lorsque vous vous situez dans le LAN et le nom serveur.mondomaine.tld lorsque vous êtes en dehors du LAN.

Tout ça n’est pas très pratique surtout qu’il existe un moyen simple d’adapter vos réponses DNS en fonction de la provenance de la requête.

Nous allons ici mettre en place des vues. Il s’agit en fait de deux fichiers de zones dont les seules différences se situent au niveau des IP. Nous aurons une vue « externe » et une vue « interne ». Lorsque un client depuis le LAN effectue une requête DNS, ce sera dans la zone « interne » que BIND ira chercher l’information, si la requête vient d’ailleurs, ce sera dans la zone « externe ».

Modifions tout d’abord notre named.conf :

```
acl "lan_hosts" {         
  10.0.0.0/24;         
  127.0.0.1; 
};
acl "wan_hosts" {         
  5.X.X.X; 
}; 

view "internal"{

  match-clients{ lan_hosts; }; 
  recursion yes; 

  zone "archifleks.net" {                 
    type master;                 
    file "/etc/bind/internal/vsense.fr.zone";         
  };         

  zone "10.0.0.in-addr.arpa" {                
    type master;                 
    file "/etc/bind/internal/10.0.0.in-addr.arpa.zone";         
  }; 
}; 

view "external"{ 

  match-clients { any; };
  allow-recursion {wan_hosts;}; 
  allow-query-cache {wan_hosts;}; 

  zone "archifleks.net" { 
    type master; 
    file "/etc/bind/external/vsense.fr.zone"; 
  }; 
};

```
Les acl sont un moyen simple de matcher les requêtes qui arriveront sur notre DNS. On crée ensuite nos vues et on applique l’acl correspondante. La directive « allow-recursion » autorise ou non les clients à utiliser le serveur DNS comme DNS publique, ils pourront depuis ce serveur résoudre n’importe quel nom sur l’internet. Dans notre cas, nous offrons cette possibilité à nos machines du LAN et à certains hôtes WAN qui nous appartiennent. Les autres ne pourront résoudre que des noms sur lesquels nous avons autorité.

Nous pouvons maintenant utiliser toujours le nom de nos serveurs avec le domaine vsense.fr. En fonction de notre position, nous recevrons l’IP publique ou l’IP privée du serveur.
