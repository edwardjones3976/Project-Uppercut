<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 05:50 UTC | START ] -->

# Agent tooling

What an agent working on this repository can reach, what is wired up, and what
still needs the Director's hands. Written because the alternative is each session
rediscovering the same set — which is the same failure the ops skill exists to
stop, one level up.

## Wired up

### The ops skill

`project-uppercut-ops` — the working manual. Encodes the one rule (*a harness may
explore, only the contract may conclude*), what "proven" means, the two gate
commands, pin discipline, the identifying-tag procedure, the standing push
directive, and the environment traps that each cost about an hour the first time.
Delivered as a `.skill` file 2026-08-06; a saved skill loads automatically when
the work matches its description.

**If a session is behaving as though none of this exists, the skill is not
installed.** That is the first thing to check.

### Persistent memory (Perseus Vault)

Local vault at `C:\Users\edwar\.perseus-vault`. Four entities written:

| Key | Category | What it holds |
|---|---|---|
| `uppercut-evidence-discipline` | convention | harness vs contract, what proven means, gates, pin discipline |
| `uppercut-environment-traps` | convention | the seven ways this machine wastes an hour |
| `uppercut-design-rules` | architecture | identity, the guard rule, emergent-over-hardcoded, Decision 0012 split, tags, push |
| `uppercut-state-2026-08-06` | decision | phases proven, gates closed, what is contract-only, what is in flight |

This exists because **this conversation has been compacted twice**, and each time
the texture goes: what was tried, what was rejected and why. A summary keeps the
conclusions and loses the corrections, which are the expensive part.

Semantic recall is disabled on this install, so recall is keyword-only. That is
worth turning on if the vault grows.

### Issue tracking (Linear)

Team **Project Uppercut**, project **Unreal live backend integration**.

`PRO-5` M1 gates (done) · `PRO-6` M2 runtime subsystem · `PRO-7` M3 port R and S ·
`PRO-8` M4 dev arena and HUD · `PRO-9` M5 round flow and soul proof ·
`PRO-10` whitelist the repo in Bitdefender (needs Ed).

The milestone plan lives here rather than only in a markdown file so that
"what is actually left" survives a session boundary.

### Nightly verification

A scheduled task runs at 03:00 local every day: the test suite, the validators,
both golden streams, the research gate, and the Phase Q parity proof. It reports
**only what changed or broke**, and it is explicitly forbidden from committing,
pushing or fixing anything — a nightly run that edits the repo unsupervised is
worse than one that reports.

The case it exists for: a golden stream drifts with no decision record that day.
That means a phase silently stopped being proven, and the sooner that is said out
loud the cheaper it is.

### Research acquisition

`tools/research/harvest.py` gets scholarly identity from OpenAlex.
`tools/research/ingest.py` files full text an agent fetched — by Firecrawl if it
is ever installed, by Exa's fetch, by an ordinary web fetch, or by hand — into
untracked `research/raw/` with `fetched_via`, `source_url` and `fetched_at`
attached to the record.

The seam is deliberate. **Acquisition is the replaceable part; the gate is not.**
A quote whose provenance is "an agent had it in context once" is not evidence.

## Available and not yet used

**Subagents.** Read-only explorers for fan-out searches across the repo, a
planning agent for architecture, general-purpose agents for parallel work. Worth
reaching for on questions like "which documents still assert something the canon
rulings contradicted" — one call instead of forty serial reads.

**Workflow orchestration.** Deterministic multi-agent scripts: pipelines,
fan-out, adversarial verification panels where independent agents try to *refute*
a finding before it is believed, loop-until-dry discovery. The natural fit is the
R and S ports — each ported subsystem verified against its contract in parallel —
and a repo-wide audit for claims that outlived their evidence.

Given this project's history of nine diagnoses corrected by the next measurement,
the adversarial pattern is the one to reach for: spawn skeptics whose job is to
*break* a finding, and believe it only if they cannot.

## Needs the Director

**Snyk** is installed (CLI 1.1306.2) and reachable, but unauthenticated — a scan
returns `User not authenticated`. Authenticating opens a browser and is Ed's
action. Once done, `snyk_code_scan` (SAST over the Python and the C++) and
`snyk_sca_scan` become available.

**Superpowers** is a Claude Code **CLI** plugin marketplace and is not in this
account's claude.ai catalog, so it cannot be installed into Cowork. If that
methodology is wanted, run Claude Code CLI in this repo and add the marketplace
there; it operates on the same working tree.

**Bitdefender whitelisting** — `PRO-10`. It is currently deleting scripts from
the working tree and blocking git from restoring them.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 05:50 UTC | END ] -->

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-11 19:21 UTC | START ] -->

## Cursor MCP and host tools (2026-08-11)

These are wired for agents on the Windows host. Tokens stay in Cursor / `gh`
credential store — never in this repo.

| Tool | Status | How an agent should use it |
|---|---|---|
| **Linear** | MCP authenticated. Team `Project Uppercut` (`b0ce8ea1-…`). Project *Unreal live backend integration*. Team doc: [Agent tool routing](https://linear.app/project-uppercut/document/agent-tool-routing-beb58abfab20). | Issues are work truth. PRO-2 and PRO-5 Done. PRO-11 (Snyk Code) Backlog. PRO-6/7/8/9/10 still Backlog. |
| **GitHub CLI** | `gh` logged in as `edwardjones3976` (keyring). Scopes: `repo`, `read:org`, `gist`. | PRs, issues, Actions. GitHub **MCP** may still fail tool discovery — use `gh`, do not report "no GitHub". |
| **Slack** | MCP ready. `#uppercut-ops` (`C0BP62MBFNK`). | Humans only. Nightly drift, Director asks, Bitdefender. Draft if the user has not seen the text. |
| **Snyk** | MCP ready. Folder trusted. SCA of `requirements-dev.txt`: **0 issues** (2026-08-11). | Re-scan after dependency edits. Snyk Code (SAST) is **disabled** for org `edwardjones3976` (`SNYK-CODE-0005`) until the Director enables it. |
| **Unreal MCP** | `.mcp.json` → `http://127.0.0.1:8000/mcp`. Proven 2026-08-09. | Editor loopback only. See `docs/UNREAL_MCP.md`. Cloud / Cowork cannot reach it. |
| **Cursor plugins** | `.cursor/settings.json` enables Linear, Slack, Snyk. | If a session cannot see a plugin, check this file and Cursor Settings → MCP. |

Repo-side pointers: `AGENTS.md`, `.cursor/rules/agent-tooling.mdc`, `evidence/`.

### Snyk note (supersedes the unauthenticated claim above)

Snyk MCP `snyk_sca_scan` ran clean on `requirements-dev.txt` (Python 3.14.5).
The earlier "unauthenticated" sentence is stale. SAST is a separate org switch,
not a missing login.

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-11 19:21 UTC | END ] -->

