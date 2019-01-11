#!/bin/bash
if [ $# -ne 2 ]; then
    echo "[ USAGE ]: $0 <EFS_NAME> <PROJECT_NAME>"
    exit
fi

EFSName=${1}
ProjectName=${2}

sudo apt-get -y install nfs-common
mkdir -p efs
sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport ${EFSName}.efs.us-east-2.amazonaws.com:/ efs

# Make directory
sudo mkdir -p efs/${ProjectName}
ls -l efs
sudo umount efs