#!/usr/bin/env bash
# piphone setup. Run once on the Raspberry Pi; safe to run again.
#
#   1. Installs baresip (the SIP phone program) from Debian's package archive.
#   2. Asks for your SIP login and saves it to baresip/accounts, a file only
#      you can read.

set -euo pipefail
cd "$(dirname "$0")"

die() { echo "ERROR: $*" >&2; exit 1; }

echo "== 1/2 Installing baresip =="
sudo apt-get update
sudo apt-get install -y --no-install-recommends baresip-core alsa-utils ca-certificates

ACCOUNTS=baresip/accounts

if [ -f "$ACCOUNTS" ]; then
    echo "== 2/2 $ACCOUNTS already exists, keeping it =="
    echo "   (to enter a new login: rm $ACCOUNTS && ./setup.sh)"
else
    echo "== 2/2 Your SIP login (from your provider's web portal) =="
    read -rp  "SIP username:          " sip_user
    read -rp  "SIP server (hostname): " sip_server
    read -rsp "SIP password (hidden): " sip_pass; echo

    # Only allow characters that cannot break the one-line accounts format.
    user_ok='^[A-Za-z0-9._+-]+$'
    server_ok='^[A-Za-z0-9.-]+$'
    pass_ok='^[A-Za-z0-9._~!*+@^=-]{16,}$'
    [[ $sip_user   =~ $user_ok   ]] || die "username: only letters, digits and . _ + -"
    [[ $sip_server =~ $server_ok ]] || die "server: a plain hostname, e.g. sip.example.com"
    [[ $sip_pass   =~ $pass_ok   ]] || die "password: 16+ characters; letters, digits and . _ ~ ! * + @ ^ = - only"

    # One baresip account line:
    #   transport=tls       signalling encrypted (TLS)
    #   mediaenc=srtp-mand  call audio encrypted (SRTP); calls fail rather than go unencrypted
    #   regint=600          re-register every 10 minutes
    umask 077
    printf '<sip:%s@%s;transport=tls>;auth_pass=%s;mediaenc=srtp-mand;regint=600\n' \
        "$sip_user" "$sip_server" "$sip_pass" > "$ACCOUNTS"
fi

chmod 600 "$ACCOUNTS"
echo
echo "Setup done. Start the phone with:  ./piphone.sh"
