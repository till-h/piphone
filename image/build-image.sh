#!/usr/bin/env bash
# Build build/piphone.img: Raspberry Pi OS Lite (64-bit, Debian Trixie)
# set up for a headless Pi 5 that you reach over SSH.
#
# Run this on your Linux laptop. It does not need root.
#
#   image/build-image.sh                      uses ~/.ssh/id_ed25519.pub
#   image/build-image.sh ~/.ssh/other.pub     uses another public key
#
# It only changes files on the image's boot (FAT) partition:
#   user-data    first-boot setup: your user and SSH key, firewall, updates
#   ssh          an empty file that switches the SSH server on
#   config.txt   HDMI audio off (so the USB headset is the only sound card),
#                Wi-Fi and Bluetooth off (Ethernet only)

set -euo pipefail

# The official image, pinned to one release and checked against its SHA-256.
IMAGE_URL=https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2026-10-06/2026-10-06-raspios-trixie-arm64-lite.img.xz
IMAGE_SHA256=483db18a48da399b5b7022ffae9a07bc6d99daab30e593aedac09b69ff422843

HERE=$(cd "$(dirname "$0")" && pwd)
BUILD=$(cd "$HERE/.." && pwd)/build
SSH_PUBKEY_FILE=${1:-$HOME/.ssh/id_ed25519.pub}
PI_USER=$(id -un)      # same name as on the laptop, so "ssh piphone.local" just works

die() { echo "ERROR: $*" >&2; exit 1; }

# ---- Check inputs ------------------------------------------------------------
[ -f "$SSH_PUBKEY_FILE" ] || die "SSH public key not found: $SSH_PUBKEY_FILE"
SSH_KEY=$(head -n1 "$SSH_PUBKEY_FILE")
key_ok='^(ssh-ed25519|ecdsa-sha2-nistp256|ssh-rsa) [A-Za-z0-9+/=]+( [^"\\]*)?$'
[[ $SSH_KEY =~ $key_ok ]] || die "$SSH_PUBKEY_FILE does not look like an SSH public key"
[[ $PI_USER =~ ^[a-z][a-z0-9-]{0,31}$ ]] || die "laptop username '$PI_USER' is not a valid Pi username"
for tool in curl sha256sum xz sfdisk dd udisksctl findmnt openssl envsubst; do
    command -v "$tool" >/dev/null || die "missing tool: $tool"
done

mkdir -p "$BUILD/download"

# ---- 1. Download and verify ----------------------------------------------------
XZ=$BUILD/download/$(basename "$IMAGE_URL")
if [ ! -f "$XZ" ]; then
    echo "== Downloading $(basename "$XZ") =="
    curl -fL --proto '=https' -o "$XZ.part" "$IMAGE_URL"
    mv "$XZ.part" "$XZ"
fi
echo "== Checking SHA-256 =="
echo "$IMAGE_SHA256  $XZ" | sha256sum -c -

# ---- 2. Unpack -------------------------------------------------------------------
IMG=$BUILD/piphone.img
echo "== Unpacking to $IMG =="
xz -dc "$XZ" > "$IMG"

# ---- 3. Copy the boot partition out of the image -----------------------------------
# sfdisk line looks like: ".../piphone.img1 : start=16384, size=1048576, type=c"
read -r START SIZE < <(sfdisk -d "$IMG" | awk -F'[=,]' '/img1 :/ {print $2, $4}')
[ -n "${START:-}" ] && [ -n "${SIZE:-}" ] || die "could not find the boot partition"
BOOT=$BUILD/bootfs.img
dd if="$IMG" of="$BOOT" bs=4M iflag=skip_bytes,count_bytes \
   skip=$((START * 512)) count=$((SIZE * 512)) status=none

# ---- 4. Mount it as your user (udisksctl; no root) ----------------------------------
LOOP=$(udisksctl loop-setup --no-user-interaction -f "$BOOT" | grep -o '/dev/loop[0-9]*')
trap 'udisksctl unmount --no-user-interaction -b "$LOOP" >/dev/null 2>&1 || true' EXIT
MNT=""
for _ in $(seq 10); do                  # the desktop usually mounts it by itself
    MNT=$(findmnt -n -o TARGET "$LOOP" || true)
    [ -n "$MNT" ] && break
    sleep 1
done
if [ -z "$MNT" ]; then
    udisksctl mount --no-user-interaction -b "$LOOP" >/dev/null
    MNT=$(findmnt -n -o TARGET "$LOOP")
fi
[ -f "$MNT/config.txt" ] || die "mounted $LOOP at $MNT but it is not the boot partition"

# ---- 5. Write the first-boot settings -------------------------------------------------
echo "== Configuring first boot =="
PASSWORD=$(openssl rand -base64 48 | tr -dc 'A-Za-z0-9' | head -c 20)
PW_HASH=$(openssl passwd -6 -stdin <<< "$PASSWORD")
export PI_USER SSH_KEY PW_HASH
# Only these three variables are replaced; ${distro_codename} stays as is.
envsubst '${PI_USER} ${SSH_KEY} ${PW_HASH}' < "$HERE/user-data" > "$MNT/user-data"

touch "$MNT/ssh"

sed -i -e 's/^dtparam=audio=on$/dtparam=audio=off/' \
       -e 's/^dtoverlay=vc4-kms-v3d$/dtoverlay=vc4-kms-v3d,noaudio/' "$MNT/config.txt"
grep -qx 'dtparam=audio=off' "$MNT/config.txt"              || die "config.txt: audio edit failed"
grep -qx 'dtoverlay=vc4-kms-v3d,noaudio' "$MNT/config.txt"  || die "config.txt: HDMI audio edit failed"
cat >> "$MNT/config.txt" <<'EOF'

[pi5]
# piphone: Wi-Fi and Bluetooth off, the Pi uses its Ethernet cable only
dtoverlay=disable-wifi-pi5
dtoverlay=disable-bt-pi5

[all]
EOF
sync

# ---- 6. Unmount and put the boot partition back into the image ------------------------
udisksctl unmount --no-user-interaction -b "$LOOP" >/dev/null
trap - EXIT
dd if="$BOOT" of="$IMG" bs=4M oflag=seek_bytes seek=$((START * 512)) \
   conv=notrunc,fsync status=none
rm "$BOOT"

( umask 077; echo "$PASSWORD" > "$BUILD/pi-sudo-password.txt" )

cat <<EOF

== Done: $IMG ==

Pi login:       $PI_USER  (SSH key: $SSH_PUBKEY_FILE)
sudo password:  in $BUILD/pi-sudo-password.txt  (change it on the Pi with: passwd)

Write it to the SD card:
  lsblk                          # find the SD card, e.g. /dev/sdb or /dev/mmcblk0
  sudo umount /dev/sdX?*         # if the desktop mounted its partitions
  sudo dd if=$IMG of=/dev/sdX bs=4M conv=fsync status=progress

Then put the card in the Pi, plug in Ethernet and power. First boot installs
updates and may reboot once. Allow about 5 minutes, then:
  ssh piphone.local              # or: ssh $PI_USER@<IP address from your router>
EOF
