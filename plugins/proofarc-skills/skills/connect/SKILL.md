---
name: connect
description: Connect Claude Code to a ProofArc instance over MCP, or reconnect when ProofArc tools return 401 / unauthorized or aren't listed. Use when the user asks how to connect, sees "not connected", or tool calls fail with an auth error.
---

# Connect to ProofArc

ProofArc's MCP server is at `https://<your-instance>/mcp`. It accepts a login token in the `Authorization` header. The token comes from your ProofArc username and password and is valid for up to 30 days. It is stored in plain text in Claude Code's config (`~/.claude.json`); the password is not stored.

## Check first

- `claude mcp list` (or `/mcp` inside Claude Code) shows the ProofArc server. If it says ✔ Connected, nothing needs doing.
- Tools answering **401 / unauthorized** mean the token has expired or the user was disabled. Reconnect (below); the setup itself is fine.
- `list_projects` working means the connection is good.

## Connect, or reconnect

The script ships with this skill: `connect-proofarc.sh` in this skill's base directory. Give the user the full path.

**The person runs it in their own terminal, not the agent: it asks for a password.**

```bash
bash "<this skill's base directory>/connect-proofarc.sh" https://ui-<company>.proofarc.ai
```

- It asks for the ProofArc username and password. The password isn't shown or saved.
- It logs in and registers the instance as an MCP server named `proofarc-<company>`.
- Afterwards the user must **restart Claude Code**, then ask *"list my ProofArc projects"*.
- It needs `bash` and `python3`. On Windows, use WSL or Git Bash.

## Rules

- Never ask the user to paste their password into the chat. They type it into the terminal prompt.
- Use one login per person. Don't share an admin login for MCP use; ask an admin to create a user with the ANALYST role.
- Each instance is a separate deployment. Never copy URLs, ids or targets from one instance to another; check on the instance you're connected to.
- If the login call fails with 403, the instance's firewall may be blocking the default client. The script sends a `User-Agent` header that the instances accept.
