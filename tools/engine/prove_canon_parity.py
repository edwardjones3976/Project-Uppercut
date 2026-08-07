# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 03:50 UTC | START ]
"""Decision 0023 step 4: Python and C++ must agree about canon identity.

    python -m tools.engine.prove_canon_parity

Runs the C++ canonicalizer over `tests/fixtures/canon_hash_vectors.json` and
checks that every accept vector reproduces both hashes and every rejection
vector is REFUSED.

The refusals matter as much as the hashes. A C++ side that merely fails to crash
would prove nothing: what stops a malformed canon file from quietly acquiring an
identity is that both implementations say no to the same things, for the same
reasons.

Also re-derives the real manifest's identity on both sides. If those disagree,
every dual-hash header the runtime writes would be bound to a different notion
of who decided what counts as authoritative - which is the failure Director
requirement 1 exists to prevent.
"""
import io
import json
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from tools.uppercut_canon import canonical as C  # noqa: E402

ENGINE = os.environ.get("UPPERCUT_ENGINE", r"C:\Program Files\Epic Games\UE_5.8")
CMD = os.path.join(ENGINE, "Engine", "Binaries", "Win64", "UnrealEditor-Cmd.exe")
PROJECT = os.path.join(REPO, "sandbox", "UppercutSandbox.uproject")
OUT = os.path.join(REPO, "sandbox", "Saved", "canon", "vectors_report.txt")

PS_LIST = ("Get-CimInstance Win32_Process | "
           "ForEach-Object { $_.ProcessId.ToString() + '|' + $_.Name + '|' "
           "+ [string]$_.CommandLine }")


def kill_the_wedge():
    """Turnkey's ValidatePlatforms child ping-loops on every editor boot here."""
    out = subprocess.run(["powershell", "-NoProfile", "-Command", PS_LIST],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in out.stdout.decode("utf-8", "replace").splitlines():
        low = line.lower()
        if "validateplatforms" in low or "|ping.exe|" in low:
            subprocess.run(["powershell", "-NoProfile", "-Command",
                            "Stop-Process -Id %s -Force -ErrorAction SilentlyContinue"
                            % line.split("|")[0].strip()])


def run_commandlet():
    if not os.path.exists(CMD):
        raise SystemExit("no engine at %s - set UPPERCUT_ENGINE" % CMD)
    if os.path.exists(OUT):
        os.remove(OUT)
    argv = [CMD, PROJECT, "-run=UppercutCanonVectors", "-repo=%s" % REPO,
            "-out=%s" % OUT, "-unattended", "-nopause", "-nosplash"]
    proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    deadline = time.time() + 15 * 60
    while proc.poll() is None and time.time() < deadline:
        kill_the_wedge()
        time.sleep(2.0)
    if proc.poll() is None:
        proc.kill()
        raise SystemExit("the canon-vectors run never finished")
    if not os.path.exists(OUT):
        raise SystemExit("the commandlet wrote no report")
    return io.open(OUT, encoding="utf-8").read()


def main():
    report = run_commandlet()
    print(report.rstrip())

    failed = 0
    if "failed=0" not in report:
        failed = 1
        print("\nC++ did not agree with the vectors.")

    # Decision 0024 required proof 8: global policy AND per-file role sets, both
    # derived independently on the Python side and compared.
    manifest = C.Manifest.load(os.path.join(REPO, "data", "hash_roles.json"))

    line = [l for l in report.splitlines() if l.startswith("POLICY ")]
    if not line:
        print("the report carries no global policy identity")
        return 1
    _, version, identity = line[0].split()
    if version != manifest.version or identity != manifest.policy_identity:
        failed = 1
        print("\nGLOBAL POLICY IDENTITY DISAGREES")
        print("  python %s %s" % (manifest.version, manifest.policy_identity))
        print("  cpp    %s %s" % (version, identity))
    else:
        print("\nGLOBAL POLICY AGREES  %s %s" % (version, identity))

    role_lines = [l.split() for l in report.splitlines() if l.startswith("ROLESET ")]
    if not role_lines:
        failed = 1
        print("the report carries no per-file role-set identities - Decision "
              "0024 requires them, and a global match alone would hide a "
              "divergent dependency graph")
    checked_roles = 0
    for _, rel, ident in role_lines:
        want = manifest.role_set_identity(rel)
        if ident != want:
            failed = 1
            print("ROLE SET DISAGREES for %s\n  python %s\n  cpp    %s"
                  % (rel, want, ident))
        checked_roles += 1
    if checked_roles and not failed:
        print("ROLE SETS AGREE       %d files" % checked_roles)

    # And every vector, recomputed in Python from the same file, so a vectors
    # file edited to match a broken C++ implementation still fails.
    data = json.load(io.open(os.path.join(REPO, "tests", "fixtures",
                                          "canon_hash_vectors.json"),
                             encoding="utf-8"))
    for v in data["vectors"]:
        raw, sem, _ = C.hashes(v["input_json"], v["patterns"],
                               v["schema_identity"], v["policy_identity"],
                               v["role_set_identity"])
        hexed = C.canonical_bytes(v["input_json"], v["patterns"]).hex()
        if (raw != v["raw_sha256"] or sem != v["semantic_sha256"]
                or hexed != v["canonical_hex"]):
            failed = 1
            print("PYTHON DRIFTED from vector %s" % v["name"])

    print("\n%s" % ("PARITY PROVEN" if not failed else "PARITY FAILED"))
    return failed


if __name__ == "__main__":
    raise SystemExit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 03:50 UTC | END ]
