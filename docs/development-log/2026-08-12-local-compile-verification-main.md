<!-- [ Claude (Cowork) | Claude Opus 4.8 (claude-opus-4-8) | 2026-08-12 23:21 UTC | START ] -->

# 2026-08-12 - Local operator compile of main verifies UppercutCore builds after the pose-studio merges

After PR #42 (lit pose studio) and PR #43 (fix-forward) landed changes to
UppercutCore C++ - `UppercutMatchDirector.cpp` (+107/-36), `UppercutFighterBase.cpp`,
and the match-director header - CI on `main` was green only on `check_core_compiles`,
which is a source-integrity scan and states in its own output that it does not
compile. GitHub-hosted `windows-authority` has no UE 5.8, so nothing in CI had
actually compiled those changes (Rule 18; Issue #14 Windows/Unreal lane).

To close that gap with the standing interim discipline (operator-run build with
the editor closed), `main` @ `d469d24` was checked out into a clean, isolated
`git worktree` and built with `tools/engine/build_uppercut_core.ps1` (no args;
the repo-relative defaults from PR #41 resolved the project straight from the
worktree checkout, not a hard-coded path).

Result - the C++ compiles:

- `UppercutSandboxEditor` target, Development config, 37/37 actions.
- `[35/37] Link UnrealEditor-UppercutCore.lib`, `[36/37] Link UnrealEditor-UppercutCore.dll`.
- `Result: Succeeded`, `BUILD EXIT: 0`, ~87s via Unreal Build Accelerator.
- Toolchain: UE 5.8, MSVC 14.44 (VS 2022 BuildTools), Windows 10 SDK 10.0.26100, ISPC 1.24.0.

Scope and caveat: this is **local operator evidence**, not CI. It proves `main`
builds at `d469d24` on this machine at this time; it is not durable,
clean-machine compile authority. That still requires the self-hosted UE runner
lane (register and start the `blackbox` runner, then merge PR #38 to route
`windows-authority` to it). Issue #14 stays open until reproducible Unreal
compilation runs in CI. Combat / parity / authenticity rulings untouched.

- Verified revision: `main` @ `d469d24` (merge of PR #43)
- Compile-relevant history: PR #42 (`45762f8`), PR #43 (`d469d24`), the `check_core_compiles` restore (`6f82f6c`)
- Builder: `tools/engine/build_uppercut_core.ps1` (repo-relative since PR #41)
- Pending durable lane: PR #38 (draft) plus the self-hosted runner service

<!-- [ Claude (Cowork) | Claude Opus 4.8 (claude-opus-4-8) | 2026-08-12 23:21 UTC | END ] -->
