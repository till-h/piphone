# piphone (v2)

> **New development (November 2026).** This branch starts from scratch and
> shares no history with `master`, which holds an unrelated 2018/19 attempt
> (Twilio + Chromium).

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

## What you need

- Raspberry Pi 5 with an SD card and an Ethernet cable to your router
- **USB headset or USB sound adapter.** The Pi 5 has no headphone jack.
- A SIP provider account (see below)

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
git clone -b v2-new-development https://github.com/till-h/piphone.git
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
