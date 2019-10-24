#!/bin/bash

###############
# H-NOCS
###############
wget -O .bashrc.user https://raw.githubusercontent.com/drsrinathsridhar/home/stanford/.bashrc.user
wget -O .bashrc https://raw.githubusercontent.com/drsrinathsridhar/home/stanford/.bashrc
source .bashrc
mkdir code
cd code/
# OPTIONAL
git clone https://github.com/drsrinathsridhar/CatRecon
cd CatRecon
git config credential.helper store
cd ~
sudo mkdir /media/efs
sudo chmod a+rw /media/efs/
sudo apt-get install nfs-common
sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport fs-fe744587.efs.us-east-2.amazonaws.com:/ /media/efs
ln -s /media/efs/input ~/input
ln -s /media/efs/output ~/output
source activate pytorch_p36
conda install opencv
pip install palettable gputil
pip install git+https://github.com/drsrinathsridhar/tk3dv.git

[ Optional ]
pip install --upgrade pip
nano /etc/fstab
fs-fe744587:/ /media/efs efs defaults,_netdev 0 0


###############
# X-NOCS
###############
wget -O .bashrc.user https://raw.githubusercontent.com/drsrinathsridhar/home/stanford/.bashrc.user
wget -O .bashrc https://raw.githubusercontent.com/drsrinathsridhar/home/stanford/.bashrc
source .bashrc
mkdir code
cd code/
# OPTIONAL
git clone https://github.com/drsrinathsridhar/CatRecon
cd CatRecon
git config credential.helper store
cd ~
sudo mkdir /media/efs
sudo chmod go+rw /media/efs/
sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport fs-7646d70f.efs.us-east-2.amazonaws.com:/ /media/efs
ln -s /media/efs/input ~/input
ln -s /media/efs/output ~/output
source activate pytorch_p36
conda install opencv
pip install palettable
pip install git+https://github.com/drsrinathsridhar/tk3dv.git

[ Optional ]
cp ~/input/bash_history ~/.bash_history
pip install --upgrade pip
sudo mkdir /media/CatReconEFS
sudo chmod go+rw /media/CatReconEFS/
sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport fs-5c3a4825.efs.us-east-2.amazonaws.com:/ /media/CatReconEFS

sudo mkdir /media/CatReconEFS_COPY
sudo chmod go+rw /media/CatReconEFS_COPY
sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport fs-7317530a.efs.us-east-2.amazonaws.com:/ /media/CatReconEFS_COPY
