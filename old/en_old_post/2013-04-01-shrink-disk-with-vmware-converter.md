---
title: Shrink disk with VMware Converter
slug: shrink-disk-with-vmware-converter
date_published: 2013-04-01T16:23:10.000Z
date_updated:   2015-06-28T17:20:24.000Z
tags: Converter, Converter, ESX, ESX, ESXi, ESXi, partition, partition, shrink, SQL, SQL, VMware, VMware
---


Back when I was migrating from VMFS3 to VMFS5, I found a machine with 80go of free disk space it did not needed. Storage is expensive et we need it so I wanted to recover the space badly. The disk was not fragmented and the VM was running an Microsoft SQL server which took over all the space du to a full recovery mode. Even when I recover the space, Windows would not shrink disk space due to $BITMAP all over the file system. I am not an expert but those $BITMAP informs about available cluster, correct me if I’m wrong, and you cannot move them so easily. There is always the cold defragmentation or resizing but I did not wanted to shutdown the service for too long.

Une solution est de réaliser un clone de la machine virtuelle avec VMware Converter (gratuit sur le site de VMware) et de convertir la machine virtuelle vers le même datacenter: c’est équivalent à créer un clone à chaud avec vSphere mais Converter vous laisse redimensionner les disques et récupérer de l’espace libre.

A solution is to clone the virtual machine with VMware Converter (It is free at VMware) and do a migration in the same DC/Cluster: It create a hot clone and let you shrink disk space when going to advanced options. I’m not going to detail all the steps (there is really good documentation).

Just before validating the final step, you can go to advanced options and resize your file system.

<div class="wp-caption aligncenter" id="attachment_38" style="width: 310px">![Screenshot converter](http://res.cloudinary.com/vsense/image/upload/h_131,w_300/v1435508424/convert1_yxlxp9.png "VMware Converter")Shrink disk with VMware Converter

</div>Once the conversion is done, you will have a shutdown clone, you could use this machine but you risk to create IP or SID conflict (if on Windows). One solution is to re-run a sysprep for exemple.

You have for habits to separate DATA from SYSTEM (Duh!) To avoid trouble like above, we can remount the new disk on the old machine:

- Unmount the resize disk from the new clone
- Unmount the old disk from the old machine
- Mount the new disk on the old machine.
- Power on the old machine.

<div style="text-align: justify;">That did the trick for an SQL Server, it was completely transparent. I still had to reboot the machine to do the disk swap but the downtime was minimal.</div>

