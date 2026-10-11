# crawl-to-tests: commands

All of these read the target's stored crawl with `get_crawl_digest(target, …)`. Each takes under a second.

| the user types | call | show |
|---|---|---|
| `find <text>` | `page="*<text>*", level="index"`, then `text="<text>"` | screens whose address contains it, then elements whose label contains it, each with its page |
| `show <page>` | `page="<path or *part*>"`, then `type="form"`, `type="input"`, `type="button"` | that page's fields and buttons, marking which have stable ids |
| `stable <page>` | `page=…, stable_only=true` | only controls with an id a developer chose |
| `explain` | the SKILL.md step 4 results you already have | page groups with counts, forms by page, testability examples |
| `scenario <in your words>` | `get_crawl_digest` per step (`page=`, `text=`, `type=`) | the user's journey mapped onto the crawl, step by step (*Scenarios in the user's own words*, below) |
| `test <screen or idea>` | | 2–3 test ideas for it |
| `where` | | go back to SKILL.md steps 1–2 |
| `fixlist` | `advise_ui(target, full=true)` | a list for the developers: each control with no stable id, its page, and the `data-testid` to add, ranked by how many tests would use it |
| `more` / `done` | | next suggestions / finish |

