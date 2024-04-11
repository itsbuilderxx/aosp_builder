#!/bin/bash

# Set environment variables
ROM_DIR=/rombuilds
DEVICE=fog
git config --global user.name "itsbuilderxx"
git config --global user.email "karimhasan@gmail.com"


# Install dependencies
sudo apt-get update
sudo apt-get install -y \
  git-core gnupg flex bison build-essential zip curl \
  zlib1g-dev libc6-dev-i386 libncurses5 x11proto-core-dev \
  libx11-dev lib32z1-dev libgl1-mesa-dev libxml2-utils \
  xsltproc unzip fontconfig

# Install repo
sudo apt-get install -y openjdk-8-jdk
mkdir -p /bin
curl https://storage.googleapis.com/git-repo-downloads/repo > /bin/repo
chmod a+x /bin/repo

# Set up rombuilds folder
sudo mkdir -p $ROM_DIR

# Sync source code into rombuilds folder
cd $ROM_DIR
/bin/repo init -u https://github.com/SuperiorExtended/manifest -b UDC --git-lfs
/bin/repo sync --force-sync

# Clone kernel source
sudo git clone -b fog-r-oss https://github.com/alternoegraha/wwy_kernel_xiaomi_fog_rebase/ kernel/xiaomi/$DEVICE

# Clone vendor tree
sudo git clone -b fourteen https://github.com/alternoegraha/vendor_xiaomi_fog vendor/xiaomi/$DEVICE

# Clone device tree
sudo git clone -b fourteen-oss https://github.com/alternoegraha/device_xiaomi_fog device/xiaomi/$DEVICE

# Source build environment
source build/envsetup.sh

# Choose target
lunch SuperiorExtended_${DEVICE}-userdebug

# Build ROM
make bacon -j$(nproc --all)
