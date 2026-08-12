<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-11 19:21 UTC | START ] -->

# Evidence

Probe logs, batch JSON, screenshots, and analyzer output that a gate review
should cite by commit. Required by `CONTRIBUTING.md`.

## Layout

```
evidence/<run-id>/
  README.md          # one paragraph: what was run, seed, command, result
  *.json / *.log     # machine output; do not hand-edit
```

`<run-id>` is a date plus a short slug, e.g. `2026-08-11-snyk-sca`.

## Rules

- Never hand-edit a generated artifact; regenerate it.
- `sandbox/Saved/` is gitignored and is **not** a substitute for this folder.
- Generated files carry the producing tool's `contribution` block, not a
  hand-written tag (`CONTRIBUTION_TAGGING.md`).
- Licensed packs and Unreal `Binaries/` stay out. This folder is *our*
  measurements.

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-11 19:21 UTC | END ] -->
