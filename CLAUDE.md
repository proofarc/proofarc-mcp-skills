# Working rules for this repo (the proofarc-skills plugin)

## Every change is documented and reviewed by Fable before it ships

1. **Document it.**
   - Add an entry to `CHANGELOG.md`: the version, the date, and what changed for users.
   - If users would notice the change (a new skill, command, behaviour or install step), also update the docs page in `~/github/proofarc-public-site/public-docs/docs/mcp/claude-code-plugin.md` and the README.
2. **Bump the version** in `plugins/proofarc-skills/.claude-plugin/plugin.json`.
3. **Fable code review before pushing.** Run a subagent on model `fable` over the diff since the last release (`git diff <last-tag-or-commit>..HEAD`). Fix every must-fix finding, or reply in writing why it's not one.
4. **Check.**
   - `claude plugin validate .` and `claude plugin validate ./plugins/proofarc-skills` must pass.
   - Run every changed YAML example through the platform validator.
   - Trial behaviour changes with `claude -p … --model claude-haiku-4-5-20251001 --plugin-dir ./plugins/proofarc-skills`, connected only to the instance being used.
5. **Drive it the way users run it.**
   - Run `python3 tools/drive_agent.py tools/scenarios/<each>.json --plugin-dir ./plugins/proofarc-skills` from the repo.
   - Each scenario runs in an ordinary folder (e.g. `~/skill-trial`, not this repo: this `CLAUDE.md` would take over), with the default model and **all** of the user's MCP servers connected.
   - Every scenario must pass. Run each one at least 3 times; Haiku varies.
   - Fable reads text; only this shows which skill a model actually picks and what it does.
6. **Push** only after steps 1–5. Record the review in the commit message (`Reviewed-by: Fable (<n> findings, all addressed)`).

Trials only use projects Claude created for trials, never a customer's project.
