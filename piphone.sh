#!/usr/bin/env bash
# Start the phone.
#
# Then type, for example:
#   /dial +441632960961   call a number (always use +countrycode format)
#   /hangup               end the call
#   /accept               answer an incoming call
#   /reginfo              show whether you are registered with your provider
#   /help                 list all commands
# Ctrl-C quits.

set -euo pipefail
cd "$(dirname "$0")"

[ -f baresip/accounts ] || { echo "No SIP login yet. Run ./setup.sh first." >&2; exit 1; }
chmod 600 baresip/accounts

exec baresip -f "$PWD/baresip"
