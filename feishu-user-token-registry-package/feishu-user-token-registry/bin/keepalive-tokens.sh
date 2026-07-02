#!/usr/bin/env bash
# keepalive-tokens.sh - refresh Feishu user tokens on a schedule.
#
# Required runtime variables:
#   LARK_APP_ID or FEISHU_APP_ID

set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AS="$SKILL_DIR/bin/lark-cli-as.sh"
APP_ID="${LARK_APP_ID:-${FEISHU_APP_ID:-}}"
VAULT="$HOME/.lark-cli/token-vault"

if [ -z "$APP_ID" ]; then
  echo "Missing required environment variable: LARK_APP_ID or FEISHU_APP_ID" >&2
  exit 2
fi

echo "Feishu token keepalive - $(date '+%Y-%m-%d %H:%M:%S')"

OK=0
FAIL=0
FAIL_LIST=""

for f in "$VAULT/${APP_ID}_ou_"*.enc; do
  [ -f "$f" ] || continue
  oid=$(basename "$f" | sed "s|${APP_ID}_||;s|.enc||")
  name=$(jq -r --arg oid "$oid" '.users[] | select(.userOpenId == $oid) | .userName' \
    "$HOME/.lark-cli/openclaw/user-registry.json" 2>/dev/null | head -1)
  name="${name:-$oid}"

  out=$("$AS" "$oid" -- lark-cli calendar +agenda --as user --profile "$APP_ID" 2>&1 | grep -v "deprecated\|skills not\|lark-cli update")

  if echo "$out" | grep -qiE "need_user_authorization|unauthorized|20037|20064|invalid_grant|revoked"; then
    echo "fail: $name needs reauthorization"
    FAIL=$((FAIL+1))
    FAIL_LIST="$FAIL_LIST $name"
  else
    echo "ok: $name token refreshed"
    OK=$((OK+1))
  fi
done

echo "Keepalive finished: ok=$OK fail=$FAIL"
if [ "$FAIL" -gt 0 ]; then
  echo "Users requiring reauthorization:$FAIL_LIST"
fi
