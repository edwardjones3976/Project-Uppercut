<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 03:21 UTC | START ] -->

# Bitdefender allowlist verification — 2026-08-12

**Verdict: A, B and C pass. The allowlist holds for the four behaviours that
previously broke.** PRO-10 may be closed on this packet.

The repo's prose still described the 2026-08-06 quarantine
(`docs/implementation/unreal_live_backend_integration.md`,
`docs/implementation/agent_tooling.md`). `build_uppercut_core.ps1` being back on
disk was not itself a close — a scanner that re-quarantines on next touch would
look identical. These four probes touch the scanner in the four ways it
previously interfered.

Machine: blackbox. Repo: `C:\Users\edwar\project-uppercut`.
Branch at time of run: `feat/agent-tool-integrations` @ `5167eb7`, tree clean.
Unreal Editor confirmed **not running** before the build probe
(`tasklist /FI "IMAGENAME eq UnrealEditor*"` → no tasks).

## A. `git restore` is not blocked — PASS

The 2026-08-06 symptom was `Permission denied` when git tried to write this
exact path.

```
> git restore -- tools/engine/build_uppercut_core.ps1
RESTORE_OK
08/04/2026  10:55 AM             1,777 build_uppercut_core.ps1
```

No `Permission denied`. File present at its committed size afterwards.

## B. The build script runs to completion and survives — PASS

```
> powershell -NoProfile -ExecutionPolicy Bypass -Command "& '.\tools\engine\build_uppercut_core.ps1' *>&1 | Select-Object -Last 3; Write-Output ('CAPTURED_EXIT=' + $LASTEXITCODE)"
Total execution time: 35.24 seconds
Trace written to file C:\Users\edwar\AppData\Local\UnrealBuildTool\Trace.uba with size 12.6kb
BUILD EXIT: 0
CAPTURED_EXIT=0
```

`BUILD EXIT: 0`. The script was still on disk after the run. A first,
independent invocation (launched detached via `Win32_Process.Create`) produced
`Result: Succeeded` in `sandbox/Saved/build_last.txt`, linking
`UnrealEditor-UppercutCore.dll` — so the toolchain, the bundled dotnet, UBT and
the linker all ran unimpeded.

Note for whoever reads a future run of this script: `Write-Host "BUILD EXIT: $code"`
goes to the **information stream**, which `>` from `cmd` does not capture. A run
redirected that way produces an empty log and looks dead even when it succeeded
(this is the documented hazard in the ops skill). Capture with `*>&1` as above,
or read `sandbox/Saved/build_last.txt` for the UBT result.

## C. A `.cmd` file written into the working tree is not deleted — PASS

The 2026-08-06 symptom was Bitdefender deleting `.cmd` files out of this tree.

```
> (wrote tools/engine/_av_probe.cmd, 178 bytes)
> call tools\engine\_av_probe.cmd
AV_PROBE_ALIVE
> (checked after ~45s)   STILL_PRESENT
> (checked again ~6 min) STILL_PRESENT
```

Written, executed, and still present on two later checks. Deleted deliberately
at the end of this run, per the probe's own terms. **Never committed.**

## D. Non-engine gate sweep — PASS (RC=0)

```
> python -m tools.engine.nightly_verify --no-engine
Project Uppercut nightly verification
  branch  feat/agent-tool-integrations
  head    5167eb7 docs: route agents through Linear, Slack, Snyk, and gh
  tree    clean

PASS tests        217.8s
PASS validators     1.2s
PASS golden         0.3s
PASS research       0.2s
SKIP phase Q     (--no-engine)
SKIP phase matrix (--no-engine)

all 4 gate(s) green - phase Q, phase matrix skipped
```

## Incidental finding, unrelated to AV — a BOM in a commit subject

`nightly_verify` **crashed** on the first two attempts, and the crash had nothing
to do with Bitdefender:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\ufeff' in position 18
  File "tools/engine/nightly_verify.py", line 224, in say
    print(s, flush=True)
```

Commit `5167eb7`'s subject line begins with a UTF-8 BOM (`\ufeff`), so
`head()` returns a string that cannot be encoded to this machine's default
cp1252 stdout. Any tool that prints `head()` through a redirected stdout dies —
and dies *after* printing the branch line, which reads exactly like a hang.

Worked around here with `-X utf8`. **This is a real latent trap in the evidence
tooling**, not a one-off: `say()` will take down any future non-engine gate run
whose HEAD subject carries a BOM or any other non-cp1252 character. The durable
fix is for `nightly_verify` to force a UTF-8 stdout (or sanitise `head()`), and
for whatever produced the BOM'd commit message to stop doing so. Recorded here
rather than fixed, because this packet's job is the allowlist and a fix belongs
in its own commit with its own test.

## Allowlist coverage this packet does and does not establish

Exercised and clean: this clone, `tools\engine\`, `sandbox\`, `UE_5.8` toolchain
(bundled dotnet + UBT + MSVC + linker), host Python, `git`, `powershell.exe`,
`.cmd` creation/execution inside the tree.

**Not exercised here:** `UnrealEditor.exe` / `UnrealEditor-Cmd.exe` under a real
commandlet or PIE run — the two `--no-engine` skips above. The allowlist claim
for the editor binaries themselves rests on the linker writing
`UnrealEditor-UppercutCore.dll` without interference, which is strong but is not
the same as a headless run completing. The first `prove_core_range` /
`prove_live_arena` run after this packet is the real test of that, and if it is
clean the coverage claim is complete.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 03:21 UTC | END ] -->
