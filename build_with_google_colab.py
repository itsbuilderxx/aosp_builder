import subprocess
import os
import requests
import tarfile

# Function to upload files
def upload_files(api_key, *files):
    for file in files:
        command = ['./go-pd', 'upload', '-k', api_key, '-v', file]
        output = subprocess.run(command, capture_output=True, text=True)
        print(output.stdout)

# Set your API key
api_key = "<your-api-key>"

# Set environment variables
RAM_DISK_SIZE_GB = 280
ROM_DIR = "/rombuilds"
DEVICE = "fog"

# Create RAM disk
ramdisk_path = "/mnt/ramdisk"
os.makedirs(ramdisk_path, exist_ok=True)
os.system(f"sudo mount -t tmpfs -o size={RAM_DISK_SIZE_GB}G tmpfs {ramdisk_path}")

# Set up actual storage
os.makedirs(ROM_DIR, exist_ok=True)

# Merge RAM disk with actual storage
os.system(f"sudo mount --bind {ramdisk_path} {ROM_DIR}")

# Download and extract go-pd binary
binary_url = "https://github.com/ManuelReschke/go-pd/releases/download/v1.4.1/go-pd_1.4.1_linux_amd64.tar.gz"
binary_file = "go-pd_1.4.1_linux_amd64.tar.gz"
binary_dir = "go-pd"
response = requests.get(binary_url)
with open(binary_file, "wb") as f:
    f.write(response.content)
with tarfile.open(binary_file, "r:gz") as tar:
    tar.extractall(binary_dir)
os.chmod(os.path.join(binary_dir, "go-pd"), 0o755)

# Set Git configurations
!git config --global user.name "itsbuilderxx"
!git config --global user.email "karimhasan@gmail.com"

# Make the environment non-interactive
os.environ["DEBIAN_FRONTEND"] = "noninteractive"

# Install dependencies
!sudo apt-get update
!sudo apt-get install -y \
  git-core gnupg flex bison build-essential zip curl \
  zlib1g-dev libc6-dev-i386 libncurses5 x11proto-core-dev \
  libx11-dev lib32z1-dev libgl1-mesa-dev libxml2-utils \
  xsltproc unzip fontconfig

# Install repo
!sudo apt-get install -y openjdk-8-jdk
!mkdir -p /bin
!curl https://storage.googleapis.com/git-repo-downloads/repo > /bin/repo
!chmod a+x /bin/repo

# Sync source code into rombuilds folder
%cd $ROM_DIR
!/bin/repo init -u https://github.com/SuperiorExtended/manifest -b UDC --git-lfs
!/bin/repo sync --force-sync

# Clone kernel source
!sudo git clone -b fog-r-oss https://github.com/alternoegraha/wwy_kernel_xiaomi_fog_rebase/ kernel/xiaomi/$DEVICE

# Clone vendor tree
!sudo git clone -b fourteen https://github.com/alternoegraha/vendor_xiaomi_fog vendor/xiaomi/$DEVICE

# Clone device tree
!sudo git clone -b fourteen-oss https://github.com/alternoegraha/device_xiaomi_fog device/xiaomi/$DEVICE

# Source build environment
!source build/envsetup.sh

# Choose target
!lunch SuperiorExtended_${DEVICE}-userdebug

# Build ROM
!make bacon -j$(nproc --all)

# Upload built ROM
rom_file = "/rombuilds/out/target/product/fog/SuperiorExtended_fog-userdebug.zip"
if os.path.exists(rom_file):
    upload_files(api_key, rom_file)
else:
    print("Built ROM file not found.")
