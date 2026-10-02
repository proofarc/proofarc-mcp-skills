#!/usr/bin/env bash
# Connect Claude Code to a ProofArc instance over MCP.
# Usage:  bash connect-proofarc.sh https://ui-<company>.proofarc.ai
# Asks for your ProofArc username and password; the password is not shown or saved.
# Rerun it when ProofArc tools start answering 401 / unauthorized.
set -euo pipefail
BASE="${1:-}"
[ -n "$BASE" ] || read -r -p "ProofArc address (e.g. https://ui-company.proofarc.ai): " BASE
[[ "$BASE" == *://* ]] || BASE="https://$BASE"
BASE="${BASE%/}"
HOSTPORT="${BASE#*://}"; HOSTPORT="${HOSTPORT%%/*}"; BASE="${BASE%%://*}://$HOSTPORT"; HOST="${HOSTPORT%%:*}"
NAME="proofarc-${HOST%%.*}"; NAME="${NAME/proofarc-ui-/proofarc-}"

command -v claude  >/dev/null || { echo "Claude Code is not installed: https://claude.com/claude-code"; exit 1; }
command -v python3 >/dev/null || { echo "python3 is required"; exit 1; }

echo "Using $BASE (server name: $NAME)"
read -r  -p "ProofArc username: " PA_USER
read -rs -p "ProofArc password: " PA_PASS; echo

TOKEN=$(PA_USER="$PA_USER" PA_PASS="$PA_PASS" python3 - "$BASE" <<'PY'
import json, os, sys, urllib.request
req = urllib.request.Request(sys.argv[1] + "/api/auth/login",
    data=json.dumps({"username": os.environ["PA_USER"], "password": os.environ["PA_PASS"]}).encode(),
    headers={"Content-Type": "application/json", "User-Agent": "proofarc-connect/1.0 (curl-compatible)"},
    method="POST")
try:
    r = json.loads(urllib.request.urlopen(req, timeout=30).read())
except Exception as e:
    sys.exit(f"Login failed: {e}")
print(r.get("token") or r.get("accessToken") or "")
PY
)
unset PA_PASS
[ -n "$TOKEN" ] || { echo "Login failed: no token returned. Check the username and password."; exit 1; }

claude mcp remove "$NAME" --scope user >/dev/null 2>&1 || true
claude mcp add "$NAME" --scope user --transport http "$BASE/mcp" \
  --header "Authorization: Bearer $TOKEN" >/dev/null
echo "Connected: $NAME -> $BASE/mcp"
echo "Restart Claude Code, then ask: \"list my ProofArc projects\"."
