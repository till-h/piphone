# piphone

A Raspberry Pi VOIP system for making calls to real landlines and mobiles via a SIP trunk provider.

```
piphone> dial +447911123456
[piphone] Dialling sip:+447911123456@sip.voip.ms ...
[piphone] Call connected
piphone> hangup
[piphone] Call ended
```

---

## How it works

```
  [ Pi + USB headset ]
         |
    baresip (SIP client)
         |
    SIP trunk provider  ←→  Public telephone network (PSTN)
         |
  [ landline / mobile ]
```

- **baresip** — lightweight SIP client installed via `apt`. Handles the SIP protocol and audio.
- **piphone.py** — Python wrapper that starts baresip, sends it commands via stdin, and surfaces call events.
- **SIP trunk provider** — a paid service (pay-per-minute, pennies per call) that bridges your internet connection to the phone network.

---

## Hardware

| Component | Notes |
|-----------|-------|
| Raspberry Pi | Any model with networking. Pi Zero W works. |
| USB audio adapter | **Required for the mic.** The Pi's 3.5mm jack is output-only on most models. A £5 USB dongle works fine. |
| Headset or handset | Plugs into the USB audio adapter. |
| Network | Ethernet preferred for reliability; Wi-Fi works. |

---

## Choosing a SIP trunk provider

You need a SIP trunk account to route calls to real phone numbers. This is a pay-as-you-go service — typical costs are **£0.01–0.02 per minute** to UK landlines/mobiles.

### What to look for

- **Standard SIP/SIP-over-UDP support** — avoid providers that only support proprietary apps or WebRTC.
- **SIP registration** — you register your device with their server (not just REST API calls). This is required for `baresip` to work.
- **PSTN termination** — the ability to dial real (+E.164) phone numbers, not just SIP-to-SIP.
- **Transparent per-minute pricing** — no monthly minimums or hidden fees for a personal project.
- **No mandatory DID** — for outbound-only use, you don't need to buy a phone number (DID). Some providers require one; others don't.

### Recommended providers

| Provider | Best for | SIP domain | Notes |
|----------|----------|------------|-------|
| [VoIP.ms](https://voip.ms) | UK/EU/US, hobbyists | e.g. `uk1.voip.ms` | Cheapest rates, good docs, no monthly fee, standard SIP |
| [Telnyx](https://telnyx.com) | Reliable, low-latency | `sip.telnyx.com` | Slightly more setup, competitive rates |
| [Twilio](https://twilio.com) | Easiest signup | `pstn.twilio.com` | Slightly pricier, excellent docs, free trial credit |
| [Vonage (Nexmo)](https://vonage.com) | EU-focused | `sip.nexmo.com` | Good EU coverage |

### What you'll get from your provider

After signing up you'll receive three things — this is all `piphone` needs:

1. **SIP username** — often your account ID or a number (e.g. `100001_myaccount`)
2. **SIP password** — your authentication credential
3. **SIP domain / server** — the hostname to register with (e.g. `uk1.voip.ms`)

---

## Setup

### 1. Install system dependencies

Run the setup script on your Raspberry Pi:

```bash
bash setup.sh
```

This will:
- Install `baresip` and `alsa-utils` via `apt`
- Install Python dependencies into `.venv`
- Create a `.env` file from the template

If you prefer to do it manually:

```bash
sudo apt update
sudo apt install -y baresip baresip-core alsa-utils
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

### 2. Configure your SIP credentials

```bash
nano .env
```

Fill in the values from your SIP provider's dashboard:

```dotenv
SIP_USER=your_sip_username
SIP_DOMAIN=uk1.voip.ms          # your provider's SIP server
SIP_PASSWORD=your_sip_password
SIP_OUTBOUND=                   # leave blank to use SIP_DOMAIN
NUMBER_FORMAT=E164              # E164 = +447911123456 (recommended)
AUDIO_DEVICE=default            # see audio section below
```

### 3. Configure audio

List your audio devices:

```bash
aplay -l    # output devices
arecord -l  # input/capture devices
```

If you have a USB audio adapter, it will appear as something like `card 1: Device [...]`. Set:

```dotenv
AUDIO_DEVICE=hw:1,0
```

If your system uses PulseAudio or PipeWire (common on Raspberry Pi OS Bookworm), edit `baresip_config/config` and change:

```
audio_player    alsa,default
audio_source    alsa,default
```
to:
```
audio_player    pulse,default
audio_source    pulse,default
```

### 4. Run

```bash
.venv/bin/python piphone.py
```

On first start, piphone will:
1. Write a `baresip_config/accounts` file from your `.env` credentials
2. Start baresip and wait for SIP registration (up to 20 seconds)
3. Print a prompt once registered

---

## Usage

```
piphone> dial +447911123456     # international format recommended
piphone> dial 07911123456       # local format also accepted
piphone> hangup                 # or: h
piphone> answer                 # answer an incoming call (or: a)
piphone> mute                   # toggle mic mute (or: m)
piphone> status                 # show current call state
piphone> quit                   # exit (or: q)
```

---

## File structure

```
piphone/
├── piphone.py              Main application
├── .env                    Your SIP credentials (never commit this)
├── .env.example            Credentials template
├── requirements.txt        Python dependencies (python-dotenv)
├── setup.sh                One-time setup script
└── baresip_config/
    ├── config              baresip settings (audio, codecs, modules)
    └── accounts            Generated at runtime from .env — do not edit
```

---

## Troubleshooting

**Registration times out**
- Double-check `SIP_USER`, `SIP_DOMAIN`, `SIP_PASSWORD` in `.env`
- Test network connectivity: `ping uk1.voip.ms` (or your provider's domain)
- Some providers require UDP port 5060 to be open outbound — check your router/firewall

**No audio / one-way audio**
- Run `aplay -l` and `arecord -l` to confirm your audio device is visible
- Set `AUDIO_DEVICE` in `.env` to the correct device (e.g. `hw:1,0`)
- On PipeWire systems, switch from `alsa` to `pulse` in `baresip_config/config`

**Call connects but remote party can't hear you**
- The Pi's built-in 3.5mm jack is output-only — you need a USB audio adapter for the microphone

**`baresip: command not found`**
- Run `sudo apt install baresip baresip-core`

**Codec errors / call drops**
- Try removing `opus` from `audio_codecs` in `baresip_config/config` to fall back to G.711, which every provider supports

---

## Security note

Your `.env` file contains SIP credentials. Never commit it to version control. The `.gitignore` should exclude it — add one if the repo doesn't have it yet:

```
echo ".env" >> .gitignore
echo "baresip_config/accounts" >> .gitignore
```
