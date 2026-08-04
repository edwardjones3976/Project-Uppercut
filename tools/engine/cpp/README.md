<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | START ] -->

# UppercutCore — staged C++ scaffold (Phase H, Decision 0012 slice item 3)

This directory **stages** the first C++ slice of the authoritative fight core.
It is parked here, outside the sandbox, for one reason: the sandbox's Blueprint
walkers (Phases B–G) launch the editor against a Blueprint-only `.uproject`,
and activating a C++ module before the machine has a compiler would leave the
project asking for a rebuild it cannot perform — breaking the proven walkers to
stage the unproven scaffold.

**Honesty note (Rule 18): this source has never been compiled.** The machine
has no MSVC toolchain (audited 2026-08-04: no Visual Studio, no cl.exe). The
analyzer half of Phase H — `tools/engine/analyze_core_scaffold.py`, which
defines the marker contract this commandlet must satisfy — is built and
mutation-proven (9 tests). The first build of this module is expected to be a
debugging session, exactly as every walker's first run was; what is proven
today is the contract, not the C++.

## Activation (after the toolchain exists — see the engine setup runbook)

1. Copy `Source/` into `sandbox/` (so `sandbox/Source/UppercutCore/...`).
2. Add to `sandbox/UppercutSandbox.uproject` (top level, beside "Plugins"):

        "Modules": [
            { "Name": "UppercutCore", "Type": "Runtime", "LoadingPhase": "Default" }
        ],

3. Build:

        & "C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\Build.bat" `
            UppercutSandboxEditor Win64 Development `
            -project="C:\Users\edwar\project-uppercut\sandbox\UppercutSandbox.uproject" -waitmutex

4. Run the probe (A1, A2 same seed; B1 different; A3 after a FULL rebuild —
   delete `sandbox/Binaries` and `sandbox/Intermediate`, build again, rerun):

        & "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" `
            "C:\Users\edwar\project-uppercut\sandbox\UppercutSandbox.uproject" `
            -run=UppercutCoreProbe -seed=7777 -steps=400 `
            -canon="C:\Users\edwar\project-uppercut\data\movement_model.json" `
            -out="C:\Users\edwar\project-uppercut\sandbox\Saved\phaseH\A1.txt" `
            -unattended -nosplash -nullrhi

5. Judge every stream with the analyzer; nothing is a PASS until it says so
   and A1 = A2 = A3 ≠ B1 byte-for-byte:

        python tools\engine\analyze_core_scaffold.py sandbox\Saved\phaseH\A1.txt ...

## What the probe computes, and why it is small

The Phase D hysteresis walk — canon range bands, quantized to 1e-4 reach-unit
integers, driven by an explicit 32-bit LCG — already proven in the Python
reference and the Blueprint VM. Phase H's claim is deliberately narrow: the
C++ pipeline (canon bytes in → deterministic integer arithmetic → self-hashing
marker stream out) reproduces the contract byte-for-byte across processes and
across a full rebuild. All arithmetic is integer so the three implementations
cannot drift in a float tail; the one authored-float touchpoint (quantizing
band bounds) rounds values authored at ≤3 decimals, where IEEE doubles in C++
and Python agree exactly.

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 03:42 UTC | END ] -->
