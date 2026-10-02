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

The script ships with this skill: `connect-proofarc.sh` in this skill's base directory.

### 1. Check for saved credentials (never print them)

```bash
zsh -ic 'for v in PROOFARC_URL PROOFARC_USERNAME PROOFARC_PASSWORD; do [ -n "${(P)v}" ] && echo "$v set" || echo "$v missing"; done'
```
Only report which variables are set or missing. **Never echo, print or log their values.**

### 2a. All three are set: connect for the user

```bash
zsh -ic 'bash "<this skill's base directory>/connect-proofarc.sh"' </dev/null
```
The script reads the variables, logs in and registers the server as `proofarc-<company>`. Then tell the user: *"Connected to <PROOFARC_URL>. Restart Claude Code (or run `/mcp` → Reconnect), then ask me again."* If the user also mentioned a different address, pass it as the first argument; it takes priority over `PROOFARC_URL`.

### 2b. Some are missing: show the user what to add

> To connect without typing your password each time, add these lines to `~/.zshrc` (or `~/.bashrc`), then open a new terminal:
> ```bash
> export PROOFARC_URL="https://ui-<company>.proofarc.ai"
> export PROOFARC_USERNAME="<your ProofArc username>"
> export PROOFARC_PASSWORD="<your ProofArc password>"
> ```
> Or run this once in your own terminal; it asks for whatever is missing:
> ```bash
> bash "<this skill's base directory>/connect-proofarc.sh" https://ui-<company>.proofarc.ai
> ```

Give the real path in place of the placeholder. Never ask the user to paste a password into the chat.

### After connecting

- The user must **restart Claude Code** (or `/mcp` → Reconnect), then ask *"list my ProofArc projects"*.
- The token is valid for up to 30 days. When tools answer 401, run the script again.
- It needs `bash` and `python3`. On Windows, use WSL or Git Bash.

## Rules

- Never ask the user to paste their password into the chat. It comes from `PROOFARC_PASSWORD`, or the user types it at the script's prompt in their own terminal.
- Never print the values of `PROOFARC_USERNAME` or `PROOFARC_PASSWORD` in a command's output or a reply.
- Use one login per person. Don't share an admin login for MCP use; ask an admin to create a user with the ANALYST role.
- Each instance is a separate deployment. Never copy URLs, ids or targets from one instance to another; check on the instance you're connected to.
- If the login call fails with 403, the instance's firewall may be blocking the default client. The script sends a `User-Agent` header that the instances accept.
