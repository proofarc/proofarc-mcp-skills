#!/usr/bin/env python3
"""Drive a Claude Code agent through a scripted conversation and check each reply.

Plays the user: sends each `say` of a scenario as the next turn of ONE conversation
(`claude -p … --resume <session>`), records the reply, time, cost, skills and tools used,
and checks the reply against `expect` / `forbid` regexes. Writes a JSON log and a
Markdown transcript next to the scenario (or to --out).

  python3 tools/drive_agent.py tools/scenarios/toolshop-crawl-to-tests.json
  python3 tools/drive_agent.py <scenario> --model claude-haiku-4-5-20251001 --plugin-dir ./plugins/proofarc-skills

Scenario (JSON):
{
  "name": "…",
  "cwd": "~/skill-trial",                    # folder the agent runs in (not this repo: its CLAUDE.md would take over)
  "model": "claude-haiku-4-5-20251001",
  "plugin_dir": "./plugins/proofarc-skills",  # optional: test the working copy instead of the installed plugin
  "mcp_config": "/path/to/mcp.json",          # optional; with "strict_mcp": true only these servers are connected
  "allowed_tools": ["Skill", "mcp__proofarc-outpostqa__*"],
  "turns": [
    {"say": "create UI tests for Toolshop",
     "expect": ["(?i)which app"], "forbid": ["(?i)playwright|cypress"],
     "expect_skill": "crawl-to-tests", "max_seconds": 60},
    {"say": "1", "expect": ["(?i)environment|project"]}
  ]
}
"""
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

def run_turn(sc, say, session, args):
    cmd = ["claude", "-p", say, "--output-format", "stream-json", "--verbose"]
    model = args.model or sc.get("model")
    if model and model != "default": cmd += ["--model", model]
    if session: cmd += ["--resume", session]
    pdir = args.plugin_dir or sc.get("plugin_dir")
    if pdir: cmd += ["--plugin-dir", str(Path(pdir).expanduser().resolve())]
    if sc.get("mcp_config"):
        cmd += ["--mcp-config", str(Path(sc["mcp_config"]).expanduser())]
        if sc.get("strict_mcp"): cmd += ["--strict-mcp-config"]
    tools = sc.get("allowed_tools") or ["Skill"]
    cmd += ["--allowedTools", *tools]
    t0 = time.time()
    p = subprocess.run(cmd, cwd=str(Path(sc.get("cwd", ".")).expanduser()), stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, timeout=args.turn_timeout)
    turn = {"say": say, "seconds": round(time.time() - t0, 1), "skills": [], "tools": [], "reply": "", "cost": 0.0}
    for line in p.stdout.splitlines():
        try: e = json.loads(line)
        except ValueError: continue
        if e.get("type") == "system" and e.get("subtype") == "init":
            turn["session"] = e.get("session_id"); turn["model"] = e.get("model")
        elif e.get("type") == "assistant":
            for c in e["message"].get("content", []):
                if c.get("type") == "tool_use":
                    if c["name"] == "Skill": turn["skills"].append(c["input"].get("skill"))
                    else: turn["tools"].append(re.sub(r"^mcp__[^_]+(?:-[^_]+)*__", "", c["name"]))
        elif e.get("type") == "result":
            turn["reply"] = e.get("result") or ""
            turn["cost"] = round(e.get("total_cost_usd") or 0, 4)
            turn["session"] = e.get("session_id") or turn.get("session")
            turn["is_error"] = e.get("is_error", False)
    if not turn["reply"] and p.returncode:
        turn["reply"] = f"(claude exited {p.returncode}) {p.stderr[-500:]}"
    return turn

def check(turn, spec):
    fails = []
    for rx in spec.get("expect", []):
        if not re.search(rx, turn["reply"]): fails.append(f"reply lacks /{rx}/")
    for rx in spec.get("forbid", []):
        if re.search(rx, turn["reply"]): fails.append(f"reply contains forbidden /{rx}/")
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
    sc = json.load(open(args.scenario))
    out = Path(args.out or Path(args.scenario).with_suffix("")).expanduser()
    session, log, failed = None, [], 0
    print(f"▶ {sc.get('name', args.scenario)}  model={args.model or sc.get('model')}  cwd={sc.get('cwd', '.')}")
    for i, spec in enumerate(sc["turns"], 1):
        turn = run_turn(sc, spec["say"], session, args)
        session = turn.get("session") or session
        turn["fails"] = check(turn, spec)
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
