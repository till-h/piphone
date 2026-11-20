# piphone (v2)

> **New development (November 2026).** Started from scratch. It replaces an
> unrelated 2018/19 attempt (Twilio + Chromium) that used to be in this repo.

A Raspberry Pi that calls real landline and mobile numbers. You type the
number in a terminal over SSH and talk through a USB headset.

```
$ ./piphone.sh
/dial +441632960961
...
/hangup
```

## How it works

```
 laptop ──SSH──> Raspberry Pi 5 + USB headset
                   │  baresip (SIP phone program, from Debian)
                   │  TLS  = login and call setup, encrypted
                   │  SRTP = call audio, encrypted
                   ▼
                 SIP provider (pay per minute) ──> phone network ──> landline / mobile
```

There is no custom program. piphone is a locked-down configuration for
[baresip](https://github.com/baresip/baresip) plus two short shell scripts:

| File | What it does |
|------|--------------|
| `setup.sh` | Run once on the Pi. Installs baresip and saves your SIP login to `baresip/accounts`, which only you can read. |
| `piphone.sh` | Starts the phone. |
| `baresip/config` | baresip settings, each one commented. |
| `baresip/accounts` | Your SIP login. Created by `setup.sh` and never committed (see `.gitignore`). |
| `image/build-image.sh` | Run on your laptop. Builds the SD-card image for the Pi (step 0). |
| `image/user-data` | First-boot settings in that image: user, SSH key, firewall, automatic updates. |

## What you need

- Raspberry Pi 5 with an SD card and an Ethernet cable to your router
- **USB headset or USB sound adapter.** The Pi 5 has no headphone jack.
- A SIP provider account (see below)

## 0. SD card for the Pi (on your Linux laptop)

No monitor, keyboard or mouse needed for the Pi. On the laptop:

```bash
image/build-image.sh       # about 1 minute, no root needed
```

The script downloads the official **Raspberry Pi OS Lite (64-bit, Debian
Trixie)** image, pinned to one release and checked against its SHA-256. It
then changes only the boot partition:

- **User** with the same name as your laptop user. **SSH login by key only**,
  using `~/.ssh/id_ed25519.pub`. To use a different key, pass its `.pub` file
  as the argument.
- **sudo password:** randomly generated and saved in `build/pi-sudo-password.txt`
  (readable only by you). Change it on the Pi with `passwd`.
- **Firewall:** incoming traffic is blocked except SSH and `piphone.local`
  name lookup, and only from your home network.
- **Updates:** installed on first boot, then daily and automatically.
- **Hardware:** HDMI audio off, so the USB headset is the default sound card.
  Wi-Fi and Bluetooth off, since the Pi uses the Ethernet cable.

Write the image to the SD card. `dd` overwrites the whole device, so check
the device name carefully with `lsblk`:

```bash
lsblk                                  # SD card is e.g. /dev/sdb or /dev/mmcblk0
sudo umount /dev/sdX?*                 # if the desktop auto-mounted it
sudo dd if=build/piphone.img of=/dev/sdX bs=4M conv=fsync status=progress
```

Put the card in the Pi, connect Ethernet to the router, then power. The
first boot installs updates and may reboot once, so allow about 5 minutes.
Then:

```bash
ssh piphone.local        # or: ssh <your-user>@<IP shown in your router>
```

Why not plain Debian? Plain Debian's support for Pi 5 hardware lags behind
(for example, its Ethernet runs through the RP1 chip). Raspberry Pi OS Lite
*is* Debian Trixie plus the Pi's own kernel and firmware, with no desktop
installed.

## 1. SIP provider: choose and lock down

The provider must offer:

- [ ] a **SIP account you register with**, by username, password and server hostname
- [ ] **TLS and SRTP** encryption
- [ ] calls to landlines and mobiles, pay as you go, no monthly fee

In the provider's web portal:

- [ ] Create a **separate sub-account** for the Pi with a long random password:
      16+ characters, letters and digits, optionally `. _ ~ ! * + @ ^ = -`.
- [ ] **Turn on encryption (TLS/SRTP)** for that sub-account.
- [ ] **Allow only the countries you actually call.** Stolen SIP logins are
      mainly used to call expensive international numbers.
- [ ] If the portal offers it, **only allow registration from your home IP address**.
- [ ] Keep a **small prepaid balance** and switch **automatic top-up off**.

## 2. Install on the Pi

```bash
git clone https://github.com/till-h/piphone.git
cd piphone
./setup.sh        # asks for SIP username, server and password
```

## 3. Make a call

```bash
./piphone.sh
```

| Type | Does |
|------|------|
| `/dial +441632960961` | Call a number. Always use `+` and the country code. |
| `/hangup` | End the call |
| `/accept` | Answer an incoming call (only if your account has a phone number) |
| `/reginfo` | Show whether you are registered with the provider |
| `/help` | List all commands |
| Ctrl-C | Quit |

## Security: what protects what

| Threat | Protection |
|--------|------------|
| Someone on the network reads your password or listens to calls | TLS for signalling and SRTP for audio, both mandatory. `sip_verify_server yes` rejects a server with a fake certificate. |
| Another program or user on the Pi reads your password | `baresip/accounts` is mode 600 (only you can read it). |
| A password containing unusual characters breaks the config | `setup.sh` only accepts characters that are safe in the accounts line. |
| Someone controls the phone over the network | No remote-control modules are loaded. |
| A stolen login runs up a big bill | Provider-side limits in step 1. `rtp_timeout` ends calls where the audio has stopped. |
| Someone logs in to the Pi | SSH accepts only your key; password login is off; SSH is reachable only from private (home) addresses. |
| Anything else on the network reaches the Pi | nftables firewall: inbound blocked by default. Wi-Fi and Bluetooth off. |
| Known security holes stay unpatched | Automatic daily updates from Debian (security) and Raspberry Pi (kernel, firmware). |
| A bug in baresip leads to full control of the Pi | `sudo` needs a password, so a compromised phone program does not automatically get root. |

## Troubleshooting

- **Not registered** (`/reginfo`): check the username, server and password
  (`rm baresip/accounts && ./setup.sh`). Make sure TLS is enabled for the
  sub-account in the provider's portal.
- **TLS or certificate error:** the provider's server certificate failed the
  check. Do **not** turn off `sip_verify_server`. Check the hostname, or ask
  the provider for their TLS hostname.
- **No sound:** run `aplay -l` and `arecord -l`. The USB headset must be listed
  as **card 0**.
- **Call connects but one side is silent:** turn on the provider's NAT option
  for the sub-account, if it has one.
