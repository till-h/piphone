#!/usr/bin/env python3
"""
piphone - Raspberry Pi VOIP system
Make calls to real phone numbers via a SIP provider.

Usage:
    python piphone.py
    piphone> dial +447911123456
    piphone> hangup
"""

import os
import re
import sys
import time
import signal
import threading
import subprocess
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

CONFIG_DIR = Path(__file__).parent / "baresip_config"
ACCOUNTS_FILE = CONFIG_DIR / "accounts"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def load_config() -> dict:
    required = ("SIP_USER", "SIP_DOMAIN", "SIP_PASSWORD")
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print("ERROR: Missing required environment variables:", ", ".join(missing))
        print("Copy .env.example to .env and fill in your SIP credentials.")
        sys.exit(1)

    return {
        "user":       os.environ["SIP_USER"],
        "domain":     os.environ["SIP_DOMAIN"],
        "password":   os.environ["SIP_PASSWORD"],
        "outbound":   os.getenv("SIP_OUTBOUND") or os.environ["SIP_DOMAIN"],
        "number_fmt": os.getenv("NUMBER_FORMAT", "E164").upper(),
        "audio":      os.getenv("AUDIO_DEVICE", "default"),
    }


def write_accounts_file(cfg: dict) -> None:
    """Generate the baresip accounts file from config."""
    CONFIG_DIR.mkdir(exist_ok=True)
    line = (
        f'<sip:{cfg["user"]}@{cfg["domain"]}>'
        f';auth_pass={cfg["password"]}'
        f';outbound="sip:{cfg["outbound"]}"'
    )
    ACCOUNTS_FILE.write_text(line + "\n")


def patch_audio_device(cfg: dict) -> None:
    """Update audio device in baresip config if AUDIO_DEVICE is set."""
    config_file = CONFIG_DIR / "config"
    if not config_file.exists() or cfg["audio"] == "default":
        return
    text = config_file.read_text()
    text = re.sub(r"(audio_player\s+alsa,)\S+", rf"\g<1>{cfg['audio']}", text)
    text = re.sub(r"(audio_source\s+alsa,)\S+", rf"\g<1>{cfg['audio']}", text)
    config_file.write_text(text)


# ---------------------------------------------------------------------------
# Number normalisation
# ---------------------------------------------------------------------------

def normalise_number(raw: str, fmt: str) -> str:
    """Strip formatting and apply the configured number format."""
    digits = re.sub(r"[^\d+]", "", raw)

    # Already has + prefix
    if digits.startswith("+"):
        return digits if fmt == "E164" else digits.lstrip("+")

    # Assume local 10-digit (US/UK style) → prepend +
    if fmt == "E164":
        return "+" + digits
    return digits


# ---------------------------------------------------------------------------
# Baresip controller
# ---------------------------------------------------------------------------

class BaresipController:
    """
    Starts baresip as a subprocess and drives it via its stdin.
    Baresip's stdout is monitored in a background thread and key events
    are printed to the user.
    """

    def __init__(self, config_dir: Path, sip_domain: str, number_fmt: str):
        self.config_dir = config_dir
        self.sip_domain = sip_domain
        self.number_fmt = number_fmt
        self.process: subprocess.Popen | None = None
        self._reader: threading.Thread | None = None
        self._registered = threading.Event()
        self.call_state = "idle"   # idle | calling | ringing | connected | incoming

    def start(self) -> None:
        self.process = subprocess.Popen(
            ["baresip", "-f", str(self.config_dir)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        self._reader = threading.Thread(target=self._read_output, daemon=True)
        self._reader.start()

        print("Starting baresip and registering with SIP provider...", end="", flush=True)
        if self._registered.wait(timeout=20):
            print(" OK")
        else:
            print("\nWARNING: SIP registration timed out. Check credentials / network.")

    def _read_output(self) -> None:
        assert self.process and self.process.stdout
        for line in self.process.stdout:
            line = line.rstrip()
            if not line:
                continue
            lower = line.lower()

            # Registration
            if "registered" in lower and "unregistered" not in lower and "de-registered" not in lower:
                self._registered.set()
                _event(f"Registered: {line}")

            # Call state changes
            elif "established" in lower or "connected" in lower:
                self.call_state = "connected"
                _event("Call connected")
            elif "incoming call" in lower or "ringing" in lower and self.call_state == "idle":
                self.call_state = "incoming"
                _event(f"INCOMING CALL — type 'answer' to pick up  [{line}]")
            elif "call closed" in lower or "call terminated" in lower or "session closed" in lower:
                self.call_state = "idle"
                _event("Call ended")

            # Errors worth surfacing
            elif any(kw in lower for kw in ("error", "failed", "forbidden", "unauthorized")):
                _event(f"[!] {line}")

    def _send(self, text: str) -> None:
        if self.process and self.process.stdin:
            try:
                self.process.stdin.write(text + "\n")
                self.process.stdin.flush()
            except BrokenPipeError:
                pass

    def dial(self, number: str) -> str:
        number = normalise_number(number, self.number_fmt)
        uri = f"sip:{number}@{self.sip_domain}"
        # baresip interactive dial: press 'd', then enter the URI at the prompt
        self._send("d")
        time.sleep(0.15)
        self._send(uri)
        self.call_state = "calling"
        return uri

    def hangup(self) -> None:
        self._send("h")
        self.call_state = "idle"

    def answer(self) -> None:
        self._send("a")
        self.call_state = "connected"

    def mute_toggle(self) -> None:
        self._send("m")

    def stop(self) -> None:
        if self.process:
            self._send("q")
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.terminate()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _event(msg: str) -> None:
    """Print an async event without clobbering the prompt."""
    print(f"\n[piphone] {msg}\npiphone> ", end="", flush=True)


HELP = """
Commands:
  dial <number>    Dial a phone number  (e.g. dial +447911123456)
  d <number>       Shorthand for dial
  hangup  / h      Hang up the current call
  answer  / a      Answer an incoming call
  mute    / m      Toggle microphone mute
  status  / s      Show current call state
  help    / ?      Show this help
  quit    / q      Exit piphone
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=== piphone ===\n")

    cfg = load_config()
    write_accounts_file(cfg)
    patch_audio_device(cfg)

    ctrl = BaresipController(CONFIG_DIR, cfg["domain"], cfg["number_fmt"])

    def _shutdown(sig=None, frame=None):
        print("\nShutting down...")
        ctrl.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)

    ctrl.start()
    print(HELP)

    while True:
        try:
            raw = input("piphone> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not raw:
            continue

        parts = raw.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd in ("dial", "d"):
            if not arg:
                print("Usage: dial <number>")
            else:
                uri = ctrl.dial(arg)
                print(f"Dialling {uri} ...")

        elif cmd in ("hangup", "h"):
            ctrl.hangup()
            print("Hung up.")

        elif cmd in ("answer", "a"):
            ctrl.answer()
            print("Answered.")

        elif cmd in ("mute", "m"):
            ctrl.mute_toggle()
            print("Mute toggled.")

        elif cmd in ("status", "s"):
            print(f"Call state: {ctrl.call_state}")

        elif cmd in ("help", "?"):
            print(HELP)

        elif cmd in ("quit", "q", "exit"):
            break

        else:
            print(f"Unknown command '{cmd}'. Type 'help' for help.")

    _shutdown()


if __name__ == "__main__":
    main()
