---
title: Génération de blog avec Pelican
authors: Romain Guichard
about_author: Romain Guichard est ingenieur cloud @Osones
Email: rguichard@vsense.fr
slug: blog-static-pelican
date_published: 2014-08-28T17:19:42.000Z
date_updated:   2015-06-28T17:19:42.000Z
tags: pelican, markdown, blog, github
category: Misc
---

Le blog vSense tournait jusqu'à présent sur une base de Wordpress et était
hébergé sur notre propre serveur dédié chez OVH. Pour administrer le blog ou
ajouter un article, nous passions par l'interface d'admin de Wordpress. Coté
hébergement, nous gérions nous même la partie serveur HTTP(S), PHP, base de
données etc.

Tout fonctionnait plutôt bien, mais finalement, nous nous sommes dit qu'un blog
c'était juste des pages web statiques.

Alors pourquoi s'embêter avec une base de données, du PHP et un serveur dédié ?

Wordpress pose aussi le problème du travail hors connexion. Comment faisions
nous si vous souhaitions travailler dans le train ?


Voici les outils que nous utilisons désormais en remplacement de l'ancienne
architecture :

- les articles sont tous écris dans des fichiers texte au format markdown
- les articles sont stockés dans un repository git
- Pelican est l'outil permettant de transformer le markdown en html
- Disqus est l'outil utilisé pour disposer d'un système de commentaires

Nous traiterons dans un autre article les changements apportés coté serveur web
et l'utilisation des services Amazon Web Services.

Commençons par installer Pelican et Markdown
```pip install pelican markdown```

Si pip n'est pas installé, le paquet sous debian/ubuntu est `python-pip`

