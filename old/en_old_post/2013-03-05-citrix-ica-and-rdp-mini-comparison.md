---
title: Citrix ICA and RDP mini comparison
slug: citrix-ica-and-rdp-mini-comparison
date_published: 2013-03-04T23:02:28.000Z
date_updated:   2015-06-28T17:20:19.000Z
tags: Citrix, Citrix, ICA, ICA, RDP, RDP, XenDesktop, XenDesktop
---


I did a XenDesktop LAB a while back, I’m going to present you a mini benchmark between the ICA protocol from Citric and the RDP from Microsoft, more specifically the flash player redirection which was a problem for us because of the user who needed Youtube for communication purposes.I did not quantify the FPS so I will be a little subjective about the fluidity.

The ICA test were realized with XenDesktop 5.6 and the RDP test with and without Wyse TCX 4.2 for acceleration and flash player redirection.

The following graphs were realized on a Windows 7 virtual machine with 2 vCPU and 1 GB of RAM. The flash player version is 11. The youtube video is the [following](http://www.youtube.com/watch?v=BTiZD7p_oTc "Fractal Zoom") in 360p.

The thins clients used were Wyse V10LE with WTOS 7.1.122 which do not provide client flash player, the decoding part was server side.


# **Citrix ICA**

In the three following graph the video stayed fluid and was getting more fluid with the increase of compression level.  
 HDX policy:

- Lossy compression level: medium
- Progressive compression: medium

[![](http://res.cloudinary.com/vsense/image/upload/v1435508419/ICA-e1409681084434_ksn1xe.png "ICA")](http://res.cloudinary.com/vsense/image/upload/v1435508419/ICA-e1409681084434_ksn1xe.png)

The video appear twice.

___

HDX policy:



