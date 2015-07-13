---
title: Comparaison Citrix ICA et RDP
authors: Kevin Lefevre
about_author: Kevin Lefevre est ingenieur cloud @Osones
email: klefevre@vsense.fr
slug: comparaison-citrix-ica-et-rdp
date_published: 2013-03-04T23:02:28.000Z
date_updated:   2015-06-28T17:20:19.000Z
tags: Citrix, ICA, RDP, XenDesktop
category: Système
---


Dans le cadre d’un LAB XenDesktop, je vais vous présenter un mini benchmark de débit entre le protocole ICAde Citrix et le protocole RDP de Microsoft plus particulièrement dans le cas de la redirection Flash Player. Je n’ai pas quantifié le nombre de fps donc je serai assez subjectif sur la fluidité.

Les tests ICA sont réalisés avec XenDesktop 5.6 et les test RDP avec et sans Wyse TCX 4.2 pour l’accélération et redirection Flash-Player.

Les graphiques suivants ont été réalisés sur une machine virtuelle Windows 7 avec 2 vCPU et 1 Go de RAM. La version de flash Player est la 11. La vidéo Youtube est la [suivante](http://www.youtube.com/watch?v=BTiZD7p_oTc "Best fractale Zoom") en résolution 360p.

Les clients légers utilisés sont des Wyse V10LE en version WTOS 7.1.122 et n’intègre pas de client Flash-Player, le décodage est donc coté serveur.


# **Citrix ICA**

Dans les trois différents cas, la vidéo reste fluide et devient de plus en plus fluide au fur et à mesure que l’on augmente la compression.

Politique HDX:

- Lossy compression level: medium
- Progressive compression: medium

[![](http://res.cloudinary.com/vsense/image/upload/v1435508419/ICA-e1409681084434_ksn1xe.png "ICA")](http://res.cloudinary.com/vsense/image/upload/v1435508419/ICA-e1409681084434_ksn1xe.png)

Dans ce premier graphique, la vidéo est présente deux fois.

Politique HDX:

- Lossy compression level: high
- Progressive compression level: very-high

[![](http://res.cloudinary.com/vsense/image/upload/v1435508418/ICA-very-high-comp-high-lossless1_orwlva.png "ICA-very-high-comp-high-lossless")](http://res.cloudinary.com/vsense/image/upload/v1435508418/ICA-very-high-comp-high-lossless1_orwlva.png)

Politique HDX:

- Lossy compression level: high
- Progressive compression: ultra-high

[![](http://res.cloudinary.com/vsense/image/upload/v1435508417/ICA-ultra-high-comp-high-lossless1_iq8ugl.png "ICA-ultra-high-comp-high-lossless")](http://res.cloudinary.com/vsense/image/upload/v1435508417/ICA-ultra-high-comp-high-lossless1_iq8ugl.png)


# Microsoft RDP

Sans Wyse TCX suite, la vidéo n’est pas du tout fluide et le plug-in Flash-Player à planté avant la fin de la vidéo. Débit environ deux fois supérieur à l’ICA

[![](http://res.cloudinary.com/vsense/image/upload/v1435508416/RDP-Win7-2proc-1gbram-noTCX1_acom7n.png "RDP-Win7-2proc-1gbram-noTCX")](http://res.cloudinary.com/vsense/image/upload/v1435508416/RDP-Win7-2proc-1gbram-noTCX1_acom7n.png)

Avec Wyse TCX, video fluide, acceptable pour l’utilisateur mais tout de même moins qu’en ICA. Pas d’amélioration de débit.

[![](http://res.cloudinary.com/vsense/image/upload/v1435508416/RDP-Win7-2proc-1gbram-TCX1_tpd8h8.png "RDP-Win7-2proc-1gbram-TCX")](http://res.cloudinary.com/vsense/image/upload/v1435508416/RDP-Win7-2proc-1gbram-TCX1_tpd8h8.png)
