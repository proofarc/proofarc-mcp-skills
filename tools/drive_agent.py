#!/usr/bin/env python3
"""Drive a Claude Code agent through a scripted conversation and check each reply.

Plays the user: sends each `say` of a scenario as the next turn of ONE conversation
(`claude -p … --resume <session>`), records the reply, time, cost, skills and tools used,
and checks the reply against `expect` / `forbid` regexes. Writes a JSON log and a
Markdown transcript next to the scenario (or to --out).

  python3 tools/drive_agent.py tools/scenarios/local/<your-scenario>.json
  python3 tools/drive_agent.py <scenario> --model claude-haiku-4-5-20251001 --plugin-dir ./plugins/proofarc-skills

Scenario (JSON):
{
  "name": "…",
  "cwd": "~/some-folder",                   # folder the agent runs in (not this repo: its CLAUDE.md would take over)
  "model": "claude-haiku-4-5-20251001",
  "plugin_dir": "./plugins/proofarc-skills",  # optional: test the working copy; it takes precedence over the installed plugin
                                              # relative paths (cwd, mcp_config) are relative to the scenario file
  "mcp_config": "/path/to/mcp.json",          # optional; with "strict_mcp": true only these servers are connected
  "allowed_tools": ["Skill", "mcp__<proofarc-server>__*"],
  "turns": [
    {"say": "create UI tests for Toolshop",
     "expect": ["(?i)which app"], "forbid": ["(?i)playwright|cypress"],
     "expect_skill": "crawl-to-tests", "max_seconds": 60},
    {"say": "1", "expect": ["(?i)environment|project"]}
  ]
}

Scenario keys (all optional except one of turns/goal):
  turns: [{say, expect, forbid, expect_skill, forbid_skill_prefix, forbid_tools, max_seconds, yaml_expect, yaml_forbid}]
  goal: {first, expect_skill, until, until_tools: {tool: min_calls}, rules: [{when, say}],
         approve_say (regex of replies that approve a plan), max_turns, forbid, forbid_tools}
  mcp_servers: [names] -> run with only these servers (copied from ~/.claude.json into a 0600 file)
  start_page_rx: regex for selectors already on the starting page (a final check on them fails)
  yaml_expect / yaml_forbid: regexes the created test YAML must / must not match
"""
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

def resolve(sc, path):
    """~ and absolute paths as given; anything else is relative to the scenario file."""
    p = Path(path).expanduser()
    return p if p.is_absolute() else (Path(sc["_dir"]) / p).resolve()

def mcp_config_for(names):
    """Only these MCP servers, copied from the user's Claude config (e.g. leave out a broken connector)."""
    d = json.load(open(os.path.expanduser("~/.claude.json"))); found = {}
    def walk(o):
        if isinstance(o, dict):
            for k, v in (o.get("mcpServers") or {}).items():
                if k in names and k not in found: found[k] = v
            for v in o.values(): walk(v)
    walk(d)
    missing = [n for n in names if n not in found]
    if missing: sys.exit(f"MCP servers not configured locally: {missing}")
    p = Path(os.path.expanduser("~/.cache/drive_agent")); p.mkdir(parents=True, exist_ok=True); p = p / "mcp.json"
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)  # holds auth headers: never world-readable
    with os.fdopen(fd, "w") as f: json.dump({"mcpServers": found}, f)
    return p

def run_turn(sc, say, session, args):
    cmd = ["claude", "-p", say, "--output-format", "stream-json", "--verbose"]
    model = args.model or sc.get("model")
    if model and model != "default": cmd += ["--model", model]
    if session: cmd += ["--resume", session]
    pdir = args.plugin_dir or sc.get("plugin_dir")
    if pdir: cmd += ["--plugin-dir", str(Path(pdir).expanduser().resolve())]
    if sc.get("mcp_servers"):
        cmd += ["--mcp-config", str(mcp_config_for(sc["mcp_servers"])), "--strict-mcp-config"]
    elif sc.get("mcp_config"):
        cmd += ["--mcp-config", str(resolve(sc, sc["mcp_config"]))]
        if sc.get("strict_mcp"): cmd += ["--strict-mcp-config"]
    tools = sc.get("allowed_tools") or ["Skill"]
    cmd += ["--allowedTools", *tools]
    t0 = time.time()
    turn = {"say": say, "seconds": 0, "skills": [], "tools": [], "reply": "", "cost": 0.0}
    env = {**os.environ, "DISABLE_AUTOUPDATER": "1"}  # an update mid-run reinstalls `claude` and kills the turn
    try:
        for attempt in range(6):
            try:
                p = subprocess.run(cmd, cwd=str(resolve(sc, sc.get("cwd", "."))), stdin=subprocess.DEVNULL,
                                   capture_output=True, text=True, timeout=args.turn_timeout, env=env)
                break
            except FileNotFoundError:  # `claude` briefly missing while it is being reinstalled
                if attempt == 5: raise
                time.sleep(20)
    except subprocess.TimeoutExpired:
        turn.update(seconds=args.turn_timeout, reply=f"(timed out after {args.turn_timeout}s)", is_error=True)
        return turn
    turn["seconds"] = round(time.time() - t0, 1)
    for line in p.stdout.splitlines():
        try: e = json.loads(line)
        except ValueError: continue
        if e.get("type") == "system" and e.get("subtype") == "init":
            turn["session"] = e.get("session_id"); turn["model"] = e.get("model")
        elif e.get("type") == "assistant":
            for c in e["message"].get("content", []):
                if c.get("type") == "tool_use":
                    if c["name"] == "Skill": turn["skills"].append(c["input"].get("skill"))
                    elif c["name"] == "Bash" and (re.fullmatch(r"\s*(echo|printf)\b[^;&|`$]*", c["input"].get("command", ""))
                                                  or re.fullmatch(r"\s*cat\s*<<\s*'?EOF'?\n[^`$]*\nEOF\s*", c["input"].get("command", ""))):
                        turn.setdefault("warnings", []).append("print-only Bash (status message): " + c["input"]["command"][:80])
                    elif c["name"] == "Bash" and "/tool-results/" in c["input"].get("command", "") and not re.search(r"curl|wget|python|http", c["input"]["command"]):
                        turn.setdefault("warnings", []).append("Bash on a saved tool result (should be Read): " + c["input"]["command"][:80])
                    else:
                        turn["tools"].append(re.sub(r"^mcp__.+?__", "", c["name"]))
                        if c["name"].endswith("create_ui_test_from_yaml"):
                            turn.setdefault("yamls", []).append(c["input"].get("yaml_text", ""))
        elif e.get("type") == "result":
            turn["reply"] = e.get("result") or ""
            turn["cost"] = round(e.get("total_cost_usd") or 0, 4)
            turn["session"] = e.get("session_id") or turn.get("session")
            turn["is_error"] = e.get("is_error", False)
    if not turn["reply"] and p.returncode:
        turn["reply"] = f"(claude exited {p.returncode}) {p.stderr[-500:]}"
    return turn

def steps_of(y):
    """Split UI-test YAML into [{action, selector, ...}] without needing PyYAML (block or flow style)."""
    out = []
    for block in re.split(r"(?m)^\s*-\s+(?=[{\w])", y)[1:]:
        st = {}
        flow = re.match(r"\{(.*)\}\s*$", block.strip(), re.S)
        pairs = re.findall(r"(\w+):\s*(\"[^\"]*\"|'[^']*'|[^,}]*)", flow.group(1)) if flow else \
                [m.groups() for m in (re.match(r"\s*(\w+):\s*(.*)$", ln) for ln in block.splitlines()) if m]
        for k, v in pairs: st[k] = v.strip().strip('"\'')
        if "action" in st: out.append(st)
    return out

def yaml_problems(y, spec):
    """Weak tests that still pass: the checks a rule-following test must not have."""
    probs, steps = [], steps_of(y)
    cleared, prev = set(), None
    for st in steps:
        sel = st.get("selector", "")
        if st["action"] == "CLEAR": cleared.add(sel)
        if st["action"] == "SEND_KEYS" and sel not in cleared and not (prev and prev["action"] == "CLEAR"):
            probs.append(f"SEND_KEYS {sel} without CLEAR first (rule 5)")
        if st["action"].startswith(("VALIDATE_", "WAIT_FOR_TEXT")) and sel in ("body", "html"):
            probs.append(f"{st['action']} on the whole page body proves nothing about the action (rule 7)")
        prev = st
    asserts = [st for st in steps if st["action"].startswith(("VALIDATE_", "WAIT_FOR_"))]
    rx = spec.get("start_page_rx")
    if rx and asserts and re.search(rx, asserts[-1].get("selector", "")):
        probs.append(f"final check {asserts[-1]['action']} {asserts[-1].get('selector','')} targets something already on the starting page (rule 7)")
    typed = next((i for i, st in enumerate(steps) if st["action"] == "SEND_KEYS"), None)
    if rx and typed is not None:
        after = steps[typed + 1:]
        clicked = next((i for i, st in enumerate(after) if st["action"] == "CLICK" and re.search(rx, st.get("selector", ""))), None)
        if clicked is not None and not any(a["action"].startswith(("VALIDATE_", "WAIT_FOR_")) and not re.search(rx, a.get("selector", "")) for a in after[:clicked]):
            probs.append("after typing, it clicks an item the starting page already shows before checking any result, so it works even if the action did nothing (rule 7)")
    return probs

def check(turn, spec):
    fails = []
    for y in turn.get("yamls", []):
        fails += ["created test: " + p for p in yaml_problems(y, spec)]
        for rx in spec.get("yaml_forbid") or []:
            if re.search(rx, y): fails.append(f"created test contains forbidden /{rx}/")
        for rx in spec.get("yaml_expect") or []:
            if not re.search(rx, y): fails.append(f"created test lacks /{rx}/")
    if spec.get("approve_say") is not None and "create_ui_test_from_yaml" in turn["tools"] and not re.fullmatch(spec["approve_say"], turn["say"].strip()):
        fails.append("created a test without the user's approval of a plan")
    if turn.get("is_error") or not turn["reply"].strip(): fails.append("claude error or empty reply: " + turn["reply"][:120])
    for rx in spec.get("expect", []):
        if not re.search(rx, turn["reply"]): fails.append(f"reply lacks /{rx}/")
    for rx in spec.get("forbid", []):
        if re.search(rx, turn["reply"]): fails.append(f"reply contains forbidden /{rx}/")
    bad = spec.get("forbid_skill_prefix")
    if bad and any((x or "").startswith(bad) for x in turn["skills"]): fails.append(f"skill {bad} started but shouldn't")
    sk = spec.get("expect_skill")
    if sk and not any(sk in (s or "") for s in turn["skills"]): fails.append(f"skill {sk} not started (got {turn['skills'] or 'none'})")
    if spec.get("max_seconds") and turn["seconds"] > spec["max_seconds"]: fails.append(f"took {turn['seconds']}s > {spec['max_seconds']}s")
    for t in spec.get("forbid_tools", []):
        if any(re.fullmatch(t, x) for x in turn["tools"]): fails.append(f"used forbidden tool {t}")
    return fails

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenario"); ap.add_argument("--model"); ap.add_argument("--plugin-dir")
    ap.add_argument("--out"); ap.add_argument("--turn-timeout", type=int, default=900)
    ap.add_argument("--keep-going", action="store_true", help="continue after a failed check")
    args = ap.parse_args()
    sc = json.load(open(args.scenario)); sc["_dir"] = str(Path(args.scenario).resolve().parent)
    out = Path(args.out or Path(args.scenario).with_suffix("")).expanduser()
    session, log, failed = None, [], 0
    if "goal" in sc:
        sc["turns"] = []  # filled as we go
        g = sc["goal"]; say = g["first"]; asked = 0
        print(f"▶ {sc.get('name', args.scenario)} (goal mode)  model={args.model or sc.get('model')}")
        while asked < g.get("max_turns", 10):
            asked += 1
            spec = {"say": say, "forbid_tools": g.get("forbid_tools", []), "forbid": g.get("forbid", []), "max_seconds": g.get("max_seconds"), "start_page_rx": sc.get("start_page_rx"), "yaml_expect": sc.get("yaml_expect"), "yaml_forbid": sc.get("yaml_forbid"), "approve_say": g.get("approve_say")}
            if asked == 1 and g.get("expect_skill"): spec["expect_skill"] = g["expect_skill"]
            sc["turns"].append(spec)
            turn = run_turn(sc, say, session, args); session = turn.get("session") or session
            turn["fails"] = check(turn, {**{k: sc.get(k) for k in ("start_page_rx", "yaml_expect", "yaml_forbid")}, **{k: v for k, v in spec.items() if v is not None}}); log.append(turn)
            print(f"\n{'✓' if not turn['fails'] else '✗'} turn {asked}: {say!r}  {turn['seconds']}s  ${turn['cost']}  tools={len(turn['tools'])}")
            print("   " + turn["reply"][:400].replace("\n", "\n   "))
            for f in turn["fails"]: print(f"   ✗ {f}")
            for w in turn.get("warnings", []): print(f"   ⚠ {w}")
            if turn["fails"]: failed += 1
            done_tools = all(sum(t.get("tools", []).count(k) for t in log) >= n for k, n in g.get("until_tools", {}).items())
            if re.search(g.get("until", "$^"), turn["reply"]) and done_tools: break
            nxt = next((r["say"] for r in g.get("rules", []) if re.search(r["when"], turn["reply"])), None)
            if nxt is None:
                turn["fails"].append("no rule matched the agent's question; stuck"); failed += 1; break
            say = nxt
        else:
            if log: log[-1]["fails"].append(f"goal /{g.get('until')}/ not reached in {asked} turns"); failed += 1
        total_s = sum(t["seconds"] for t in log); total_c = sum(t["cost"] for t in log)
        print(f"\n{len(log)} turns, {failed} failed, goal {'reached' if log and re.search(g.get('until', '$^'), log[-1]['reply']) and all(sum(t.get('tools', []).count(k) for t in log) >= n for k, n in g.get('until_tools', {}).items()) else 'NOT reached'}, {total_s:.0f}s, ${total_c:.2f}, session {session}")
        sc.pop("_dir", None)
        json.dump({"scenario": sc, "session": session, "turns": log}, open(f"{out}.log.json", "w"), indent=1)
        with open(f"{out}.transcript.md", "w") as f:
            for i, t in enumerate(log, 1): f.write(f"## Turn {i}: `{t['say']}`\n\n{t['reply']}\n\n" + "".join(f"- ✗ {x}\n" for x in t["fails"]))
        sys.exit(1 if failed else 0)
    print(f"▶ {sc.get('name', args.scenario)}  model={args.model or sc.get('model')}  cwd={sc.get('cwd', '.')}")
    for i, spec in enumerate(sc["turns"], 1):
        turn = run_turn(sc, spec["say"], session, args)
        if i > 1 and session and turn.get("session") and turn["session"] != session:
            turn.setdefault("fails_pre", []).append("conversation was not continued (new session id)")
        session = turn.get("session") or session
        turn["fails"] = turn.pop("fails_pre", []) + check(turn, {**{k: sc.get(k) for k in ("start_page_rx", "yaml_expect", "yaml_forbid")}, **{k: v for k, v in spec.items() if v is not None}})
        if not session:
            turn["fails"].append("no session id: later turns can't continue this conversation"); log.append(turn); failed += 1; break
        log.append(turn)
        mark = "✓" if not turn["fails"] else "✗"
        print(f"\n{mark} turn {i}: {spec['say']!r}  {turn['seconds']}s  ${turn['cost']}  skills={turn['skills']}  tools={len(turn['tools'])}")
        print("   " + turn["reply"][:600].replace("\n", "\n   "))
        for f in turn["fails"]: print(f"   ✗ {f}")
        if turn["fails"]:
            failed += 1
            if not args.keep_going: break
    total_s = sum(t["seconds"] for t in log); total_c = sum(t["cost"] for t in log)
    print(f"\n{len(log)}/{len(sc['turns'])} turns run, {failed} failed, {total_s:.0f}s, ${total_c:.2f}, session {session}")
    sc.pop("_dir", None)
    json.dump({"scenario": sc, "session": session, "turns": log}, open(f"{out}.log.json", "w"), indent=1)
    with open(f"{out}.transcript.md", "w") as f:
        f.write(f"# {sc.get('name')}\n\nmodel `{args.model or sc.get('model')}` · {len(log)} turns · {total_s:.0f}s · ${total_c:.2f} · {failed} failed\n\n")
        for i, t in enumerate(log, 1):
            f.write(f"## Turn {i}: you say `{t['say']}`\n\n{t['seconds']}s · ${t['cost']} · skills {t['skills']} · tools {t['tools']}\n\n{t['reply']}\n\n")
            for x in t["fails"]: f.write(f"- ✗ {x}\n")
    print(f"log: {out}.log.json  transcript: {out}.transcript.md")
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
