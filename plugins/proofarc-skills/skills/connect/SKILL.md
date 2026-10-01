---
name: connect
description: Connect Claude Code to a ProofArc instance over MCP, or reconnect when ProofArc tools return 401 / unauthorized or aren't listed. Use when the user asks how to connect, sees "not connected", or tool calls fail with an auth error.
---

# Connect to ProofArc

ProofArc's MCP server is at `https://<your-instance>/mcp`. It accepts a login token in the `Authorization` header. The token comes from your ProofArc username and password and lasts 30 days. It is stored in plain text in Claude Code's config (`~/.claude.json`); the password is not stored.

## Check first

- `claude mcp list` (or `/mcp` inside Claude Code) shows the ProofArc server. If it says ✔ Connected, nothing needs doing.
- Tools answering **401 / unauthorized** mean the token has expired (after 30 days) or the user was disabled. Reconnect (below); the setup itself is fine.
- `list_projects` working means the connection is good.

## Connect, or reconnect

**The person runs this in their own terminal, not the agent: it asks for a password.** Save it as `connect-proofarc.sh` and run it with `bash connect-proofarc.sh`. Use bash: zsh's `read -p` means something else. The user types the password at the prompt; it isn't shown or saved anywhere. Set `BASE` to your instance's address, and use a different `NAME` for each instance.

```bash
#!/usr/bin/env bash
BASE="https://ui-<instance>.proofarc.ai"; NAME="proofarc-<instance>"
read -r -p "ProofArc username: " U; read -rs -p "ProofArc password: " P; echo
TOKEN=$(U="$U" P="$P" python3 -c 'import json,os,sys,urllib.request as r
q=r.Request(sys.argv[1]+"/api/auth/login",data=json.dumps({"username":os.environ["U"],"password":os.environ["P"]}).encode(),headers={"Content-Type":"application/json","User-Agent":"proofarc-connect/1.0 (curl-compatible)"},method="POST")
d=json.loads(r.urlopen(q,timeout=30).read());print(d.get("token") or d.get("accessToken") or "")' "$BASE"); unset P
[ -n "$TOKEN" ] || { echo "Login failed"; exit 1; }
claude mcp remove "$NAME" --scope user >/dev/null 2>&1
claude mcp add "$NAME" --scope user --transport http "$BASE/mcp" --header "Authorization: Bearer $TOKEN"
```

Then **restart Claude Code** so it loads the tools, and ask *"list my ProofArc projects"*.

## Rules

- Never ask the user to paste their password into the chat. They type it into the terminal prompt.
- Use one login per person. Don't share an admin login for MCP use; ask an admin to create a user with the ANALYST role.
- Each instance is a separate deployment. Never copy URLs, ids or targets from one instance to another; check on the instance you're connected to.
- If the login call fails with 403, the instance's firewall may be blocking the default client. The script sends a `User-Agent` header that the instances accept.
