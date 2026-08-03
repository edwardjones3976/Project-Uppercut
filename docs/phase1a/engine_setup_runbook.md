<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 22:16 UTC | START ] -->

# Engine Setup Runbook - First Unreal Install (Decision 0007, item D-7)

**Machine audit, 2026-08-02 (blackbox):** no Epic Games Launcher, no Unreal Engine anywhere on the
system. Python 3.14.5 and git 2.55 present. The validation suite runs clean locally.

> **COMPLETED 2026-08-02.** Steps 1-4 by the Director (launcher + UE 5.8.1 installed, signed in,
> EULA accepted). Steps 5-6 executed by agent under Decision 0009: `UppercutSandbox` created from
> TP_Blank and verified headlessly (ResavePackages, result 0, zero errors/warnings). One first-boot
> quirk worth remembering: Turnkey's `Build.bat -Mode=ValidatePlatforms` ping-loops forever on every
> editor boot from this harness. Diagnosis (2026-08-02): its inner setup fails before UnrealBuildTool
> ever launches — no UBT log is ever created, while the bundled dotnet (10.0.203) runs fine standalone
> — and Build.bat's retry design loops on the failure indefinitely. Remedy: kill the wedged `cmd.exe`
> child; the editor proceeds and completes normally (verified twice, both runs exit 0, zero
> errors/warnings). Harmless to all project work; revisit only if platform SDK validation ever
> actually matters. If a boot hangs silently after `TurnkeySupport` loads, this is the place to look. This
> runbook remains the reference for engine-version changes and the future Blender install.
> <!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 23:23 UTC | edit: completed ] -->

**Why this is a Director action.** Two reasons, both structural. Epic account sign-in and EULA
acceptance are credential and legal acts the agents do not perform under the session safety contract.
And D-7 rules that engine and tool versions are pinned from the actual installed build - recorded,
never guessed (Rule 18). Everything around those two moments is already prepared.

## The click-path (about 15 minutes of your attention, then a long download)

1. **Disk first.** Confirm at least 120 GB free on the install drive. The engine alone runs 60-90 GB
   installed; the launcher, caches and first project want headroom.
2. **Download the Epic Games Launcher** from the official source only:
   `https://store.epicgames.com/download`. Sign in or create your Epic account. (Yours.)
3. **Accept the launcher EULA and install.** (Yours.)
4. In the launcher: **Unreal Engine tab -> Library -> "+" slot -> install the latest 5.x release**
   it offers. Skip optional target platforms for now; they add tens of GB and Phase 1A needs none.
   **Write down the exact version string** (5.x.y) - that string is the D-7 pin.
5. **First project:** Games -> Blank -> **Blueprint** (Decision 0002: Blueprints for early
   prototyping) -> starter content OFF -> name `UppercutSandbox` -> location
   `C:\Users\edwar\project-uppercut\sandbox\`. The repository .gitignore already fences the
   generated directories (Binaries, DerivedDataCache, Intermediate, Saved), so the engine cannot
   flood canon; only source, config and content will ever be committed.
6. **Tell the agents it is installed.** Next actions on our side, in order: stamp the D-7 version
   fields into `docs/phase0/technical_baseline.md`; commit the sandbox skeleton (source, config,
   content only); then run **determinism validation as the first in-engine task** - fixed-tick
   simulation, seeded runs, byte-identical event logs (Decision 0002's condition on Unreal
   acceptance) - before any of steps 3-5 build on the engine.

## Do not

- Install inside a OneDrive-synced or backup-managed path (sync fights the engine's file churn).
- Accept marketplace/content bundles during install; asset intake goes through the Rule 22
  compatibility audit, not the installer.
- Enable engine auto-update once pinned. Version changes are decisions, not surprises.
- Pass `-abslog=` a path the process cannot open. It suppresses **all** logging and the editor looks
  like a silent hang (cost an hour on 2026-08-03). Prefer the default log plus `-NoLogTimes`.
- Assume `new_level()` gives a plain level. In 5.8 it creates a **World Partition** level whose
  actors are external packages that `save_current_level()` does not write - spawned actors silently
  vanish. Use `new_level_from_template(..., "/Engine/Maps/Templates/Template_Default")` and
  `EditorLoadingAndSavingUtils.save_dirty_packages(True, True)`.
- Commit editor-generated credentials. First project load appends an AndroidFileServer section with a
  generated `SecurityToken` to `DefaultEngine.ini`; that plugin is now disabled in the .uproject and
  the committed token was removed (2026-08-02). Diff `sandbox/Config` after any editor session before
  committing.

## Blender (also D-7)

Not needed yet. Install when asset work begins and record its version the same way, at install time.

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 22:16 UTC | END ] -->
