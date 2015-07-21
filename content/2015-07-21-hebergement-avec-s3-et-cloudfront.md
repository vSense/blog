---
title: Hébergement d'un site statique
authors: Romain Guichard
about_author: Romain Guichard est ingenieur cloud @Osones
Email: rguichard@vsense.fr
slug: hebergement-avec-aws-s3-et-aws-cloudfront
lang: fr
date_published: 2014-08-28T17:19:42.000Z
tags: codeship, ci, amazon, S3, cloudfront, cloud, blog, cdn, object storage
category: Misc
summary: Pelican est un générateur de blog statique écrit en Python vous permettant d'écrire vos articles au format markdown. Il s'agit de la solution utilisée sur vSense pour générer notre nouveau blog. En plus de sa simplicité, celui peut être complété par un nombre important de plugins et de thèmes. Ce billet sera suivi d'un deuxième visant à présenter la migration du blog chez Amazon Web Services
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

*Nous avons préparé une image Docker contenant tout le nécessaire pour travailler
avec Pelican :
[**vsense/pelican**](https://registry.hub.docker.com/u/vsense/pelican/). Le
readme vous guidera sur la marche à suivre.*

Pour l'installation sans passer par Docker, commençons par Pelican et Markdown
`pip install pelican markdown`

Si pip n'est pas installé, le paquet sous debian/ubuntu est  `python-pip`

Pelican vient avec une commande permettant d'initialiser un projet. Afin de
versionner vos articles avec git, je vous conseille soit d'initialiser votre
projet dans un répo git ou de placer uniquement le dossier *content* généré (qui
contient vos articles) dans un répo. Ainsi vous versionnerez soit l'intégralité de votre blog, soit
uniquement ses articles.

`pelican-quickstart`

Vous allez être solicités pour répondre à plusieurs questions et notamment si
vous souhaitez uploader votre blog sur un cloud public (S3, Rackspace, Github)
ou un serveur distant (FTP, SSH). Les choix par défaut conviennent bien pour la
plupart des projets. Quant à l'upload, nous détaillerons cette partie dans un
autre article.

Vous obtenez normalement une arborescence comme celle ci :

```
.
├── Makefile
├── README.md
├── content
├── develop_server.sh
├── fabfile.py
├── img
├── output
├── pelicanconf.py
├── publishconf.py
└── themes
```

Dans *content/* se trouveront vos articles et vos pages.

Les metadata de vos articles (à placer en tête d'article) prennent la forme suivante :

```
---
title: Mon article
authors: Romain Guichard
about_author: Ingénieur Cloud
email: rguichard@vsense.fr
slug: mon-article
date_published: 2014-04-14T17:16:29.000Z
date_updated:   2015-06-28T17:19:51.000Z
tags: article, blog, pelican
category: Misc
---
```

Pour le reste, vous pouvez tout simplement écrire votre article en y ajoutant la
syntaxe Markdown là où vous en avez besoin.

Vous devez ensuite générer vos pages html avec la commande `make html` et vous
pourrez consulter votre site en local (sur le port 8000)  en lançant un serveur web avec `make
serve`. Vous pouvez tout aussi bien lancer un navigateur web pointant sur le
dossier output généré lors du `make html`.

[rajoute disqus ici]

Il est finalement assez simple d'utiliser Pelican pour générer un blog statique.
Le PHP devient quelque chose de parfaitement évitable maintenant que tout peut
être obtenir via du javascript.

Nous détaillerons dans un autre billet la migration du blog depuis notre serveur
OVH vers Amazon Web Services. Nous verrons comment obtenir un site résilient,
anycasté pour un prix dérisoire.
