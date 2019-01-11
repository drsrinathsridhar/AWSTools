#!/bin/bash
sudo apt-get -y install nfs-common
mkdir -p efs
sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport fs-cad642b3.efs.us-east-2.amazonaws.com:/ efs

# Make directory
sudo mkdir -p efs/test5
ls -l efs
sudo umount efs