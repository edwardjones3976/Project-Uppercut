<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 23:05 UTC | START ] -->

# 2026-08-12 — Lit pose studio on main, then fix-forward for a red gate

PR #42 merged the presentation-only lit pose-studio path (lights, floor, locked
camera, `FScreenshotRequest`) that finally produced a non-black Fighter0
overhand-right capture. Substance accepted; landing not accepted: merge-head
`windows-authority` failed `check_core_compiles` on bare includes
`EngineUtils.h` and `TimerManager.h`.

Fix-forward restores green `main` by replacing those includes with whitelist-safe
APIs (`UGameplayStatics::GetAllActorsOfClass` + Tick-armed capture), derives
capture filenames from fighter + resolved clip (or refuses unsupported clips),
makes `tools/engine/pose_fighter0_overhand.ps1` repo-relative via `$PSScriptRoot`
(with `-Repo` override), and records the slice here / in the cross-platform
packet. Combat authority untouched.

- Merged substance: https://github.com/edwardjones3976/Project-Uppercut/pull/42 (`45762f8`)
- Director disposition: PR #42 comment `5273783768`
- Failed merge-head run: https://github.com/edwardjones3976/Project-Uppercut/actions/runs/31648976805

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 23:05 UTC | END ] -->
