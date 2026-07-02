#!/usr/bin/env bash
# lark-cli-as.sh - temporarily run a lark-cli command as an authorized user.
#
# Usage:
#   lark-cli-as.sh <open_id> -- <lark-cli command>

set -euo pipefail

OPEN_ID="${1:-}"
if [ -z "$OPEN_ID" ]; then
  echo "Usage: lark-cli-as.sh <open_id> -- <command>" >&2
  exit 1
fi

shift
if [ "${1:-}" != "--" ]; then
  echo "Usage: lark-cli-as.sh <open_id> -- <command>" >&2
  exit 1
fi

shift
if [ "$#" -eq 0 ]; then
  echo "Usage: lark-cli-as.sh <open_id> -- <command>" >&2
  exit 1
fi

CONFIG="$HOME/.lark-cli/openclaw/config.json"
if [ ! -f "$CONFIG" ]; then
  echo "Missing lark-cli config: $CONFIG" >&2
  exit 2
fi

BACKUP="$(mktemp)"
cp "$CONFIG" "$BACKUP"
restore_config() {
  mv "$BACKUP" "$CONFIG"
}
trap restore_config EXIT INT TERM

USER_NAME="$(jq -r --arg oid "$OPEN_ID" '.apps[0].users[]? | select(.userOpenId == $oid) | .userName' "$CONFIG" 2>/dev/null | head -1)"
USER_NAME="${USER_NAME:-$OPEN_ID}"

jq --arg oid "$OPEN_ID" --arg name "$USER_NAME" \
  '.apps[0].users = [{"userOpenId": $oid, "userName": $name}]' \
  "$CONFIG" > "${CONFIG}.tmp"
mv "${CONFIG}.tmp" "$CONFIG"

"$@"
