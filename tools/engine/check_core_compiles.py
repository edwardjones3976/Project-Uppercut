# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 22:12 UTC | START ]
"""Source-integrity gate for the UppercutCore module. NOT a compile.

WHY THIS EXISTS. CI runs on GitHub-hosted runners, and no GitHub-hosted
runner has UE 5.8. The C++ core only ever compiles inside Unreal on the
operator's Windows box, which means CI was blind to a whole class of
drift: a header renamed but an #include not, a file truncated by the
file-sync failure mode this project has already been bitten by, a
commandlet that quietly stops being a commandlet. This script checks the
things a compiler would have caught first, using nothing but the bytes in
the repository.

WHAT THIS DOES NOT CLAIM (Rule 18). Nothing here compiles, links, or
runs. A green result means the source tree is internally coherent, not
that the module builds under UE 5.8. The build and the engine proofs
(prove_core_range / prove_core_evade / prove_live_arena) remain
operator-run on the Windows box with UE installed; docs/SEE_AND_TEST.md
is the runbook.

WHAT IT CHECKS, all fail-closed:
  1. Every .h/.cpp under sandbox/Source/UppercutCore decodes as strict
     UTF-8 (BOM tolerated).
  2. Every header carries #pragma once.
  3. Every quoted #include resolves: module headers must exist in
     Public/ or Private/; "X.generated.h" must correspond to a real
     module header X.h (UHT generates it from that header and nothing
     else); everything else must match the observed UE include surface
     (UE_PREFIXES / UE_BARE below). An include this script cannot
     classify FAILS - fix the include or extend the whitelist knowingly.
  4. Angle-bracket includes fail. The module has none on purpose (the
     core is pure UE-typed integer code); a new one is a policy change,
     not an accident to wave through.
  5. Braces, parens and brackets balance per file after stripping
     comments, string and char literals - the cheap tripwire for the
     known file-sync truncation failure mode. Raw string literals and
     digit separators (1'000) would defeat the stripper, so their first
     appearance also fails; extend the stripper in the same commit that
     introduces them.
  6. Every *Commandlet.h declares `public UCommandlet`, carries
     UCLASS() and GENERATED_BODY(), and includes
     Commandlets/Commandlet.h - files claiming to be commandlets are
     commandlets.
  7. Any header using GENERATED_BODY() includes its own
     <stem>.generated.h as its LAST #include - a hard UHT requirement.
  8. UppercutCore.Build.cs exists, declares the UppercutCore module,
     lists the dependency modules the includes actually need, and still
     says bUseUnity = false (the 2026-08-06 comment in that file is the
     reason; do not delete the setting without reading it).

The whitelist below was built by surveying every #include in the module
on 2026-08-09 (46 files, 201 includes), not guessed. When UE usage
grows, the failure message names the include so extending the list is a
one-line edit made on purpose.

Stdlib only, Python >= 3.8, Windows and POSIX, cwd-independent:
    python -m tools.engine.check_core_compiles
Exit 0 = all checks passed. Exit 1 = at least one failure, all listed.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = REPO_ROOT / "sandbox" / "Source" / "UppercutCore"
BUILD_CS = MODULE_DIR / "UppercutCore.Build.cs"

# Observed UE include surface (full-module survey, 2026-08-09).
UE_PREFIXES = (
    "Animation/", "Camera/", "Commandlets/", "Components/", "Dom/",
    "Engine/", "GameFramework/", "HAL/", "Kismet/", "Materials/",
    "Misc/", "Modules/", "Serialization/", "Subsystems/", "UObject/",
)
UE_BARE = ("CoreMinimal.h", "UnrealClient.h")

INCLUDE_RE = re.compile(r'^\s*#\s*include\s*(["<])([^">]+)[">]', re.M)
# Strips // and /* */ comments, "..." strings and '...' char literals so
# brace counting sees only structure. Alternation order means whichever
# construct opens first swallows the others inside it.
STRIP_RE = re.compile(
    r'//[^\n]*'
    r'|/\*.*?\*/'
    r'|"(?:\\.|[^"\\\n])*"'
    r"|'(?:\\.|[^'\\\n])*'",
    re.S,
)
RAW_STRING_RE = re.compile(r'\bR"')
DIGIT_SEP_RE = re.compile(r"\d'\d")


def main() -> int:
    failures = []

    if not MODULE_DIR.is_dir():
        print("check_core_compiles: FAIL - module directory missing: %s"
              % MODULE_DIR)
        return 1

    sources = sorted(
        p for p in MODULE_DIR.rglob("*") if p.suffix in (".h", ".cpp")
    )
    if not sources:
        print("check_core_compiles: FAIL - no .h/.cpp sources under %s"
              % MODULE_DIR)
        return 1
    headers = {p.name for p in sources if p.suffix == ".h"}

    texts = {}
    for path in sources:
        rel = path.relative_to(REPO_ROOT).as_posix()
        try:
            texts[path] = path.read_bytes().decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            failures.append("%s: not UTF-8 (%s)" % (rel, exc))

    saw_json_include = False
    for path, text in texts.items():
        rel = path.relative_to(REPO_ROOT).as_posix()

        if path.suffix == ".h" and "#pragma once" not in text:
            failures.append("%s: header without #pragma once" % rel)

        # -- include resolution ------------------------------------------
        incs = INCLUDE_RE.findall(text)
        for form, inc in incs:
            if form == "<":
                failures.append(
                    "%s: angle-bracket #include <%s> - the module has none "
                    "on purpose; if this one is deliberate, extend the "
                    "policy here in the same commit" % (rel, inc))
                continue
            if inc.startswith(("Dom/", "Serialization/Json")):
                saw_json_include = True
            if inc.endswith(".generated.h"):
                stem_header = inc[:-len(".generated.h")] + ".h"
                if stem_header not in headers:
                    failures.append(
                        "%s: includes %s but %s is not in the module - UHT "
                        "generates X.generated.h from X.h and nothing else"
                        % (rel, inc, stem_header))
            elif inc in headers:
                pass  # module header; Public/ and Private/ are include roots
            elif inc in UE_BARE or inc.startswith(UE_PREFIXES):
                pass  # known engine surface; existence is the engine's claim
            elif inc.startswith("Uppercut"):
                failures.append(
                    "%s: includes %s which does not exist in the module - "
                    "renamed-header drift" % (rel, inc))
            else:
                failures.append(
                    '%s: unclassifiable #include "%s" - not a module header, '
                    "not on the observed UE whitelist; fix it or extend "
                    "UE_PREFIXES/UE_BARE knowingly" % (rel, inc))

        # -- structural balance (truncation tripwire) --------------------
        if RAW_STRING_RE.search(text):
            failures.append(
                '%s: raw string literal - the stripper does not handle '
                'R"..."; extend it before using them' % rel)
        elif DIGIT_SEP_RE.search(text):
            failures.append(
                "%s: digit separator (1'000) - it defeats the char-literal "
                "stripper; extend the stripper before using them" % rel)
        else:
            stripped = STRIP_RE.sub(" ", text)
            for pair in ("{}", "()", "[]"):
                n_open = stripped.count(pair[0])
                n_close = stripped.count(pair[1])
                if n_open != n_close:
                    failures.append(
                        "%s: unbalanced %s (%d open vs %d close) - possible "
                        "truncation, the known file-sync failure mode"
                        % (rel, pair, n_open, n_close))

        # -- commandlets are commandlets ---------------------------------
        if path.name.endswith("Commandlet.h"):
            if "public UCommandlet" not in text:
                failures.append(
                    "%s: named a commandlet but does not declare "
                    "'public UCommandlet'" % rel)
            if "UCLASS(" not in text or "GENERATED_BODY()" not in text:
                failures.append(
                    "%s: commandlet header missing UCLASS()/GENERATED_BODY()"
                    % rel)
            if '#include "Commandlets/Commandlet.h"' not in text:
                failures.append(
                    "%s: commandlet header does not include "
                    "Commandlets/Commandlet.h" % rel)

        # -- UHT: generated.h must be the last include -------------------
        if path.suffix == ".h" and "GENERATED_BODY()" in text:
            expected = path.name[:-2] + ".generated.h"
            names = [inc for _, inc in incs]
            if not names or names[-1] != expected:
                failures.append(
                    "%s: uses GENERATED_BODY() so %s must be the LAST "
                    "#include (last is %s)"
                    % (rel, expected, names[-1] if names else "nothing"))

    # -- Build.cs invariants ---------------------------------------------
    if not BUILD_CS.is_file():
        failures.append("sandbox/Source/UppercutCore/UppercutCore.Build.cs: "
                        "missing")
    else:
        build = BUILD_CS.read_bytes().decode("utf-8-sig")
        if "class UppercutCore" not in build:
            failures.append(
                "UppercutCore.Build.cs: does not declare class UppercutCore")
        if not re.search(r"bUseUnity\s*=\s*false", build):
            failures.append(
                "UppercutCore.Build.cs: bUseUnity = false is gone - read the "
                "2026-08-06 comment in that file before deleting it")
        required = ['"Core"', '"CoreUObject"', '"Engine"']
        if saw_json_include:
            required.append('"Json"')
        for token in required:
            if token not in build:
                failures.append(
                    "UppercutCore.Build.cs: dependency %s missing but the "
                    "includes need it" % token)

    n_h = len(headers)
    n_cpp = len(sources) - n_h
    if failures:
        print("check_core_compiles: FAIL - %d problem(s) across %d headers "
              "+ %d cpp files:" % (len(failures), n_h, n_cpp))
        for f in failures:
            print("  - %s" % f)
        return 1

    print("check_core_compiles: OK - %d headers + %d cpp files: UTF-8 "
          "clean, all includes resolve, braces balanced, commandlets "
          "subclass UCommandlet, generated.h placement correct, Build.cs "
          "invariants hold. NOT verified here: compilation, linking, or "
          "any engine behavior - those proofs are operator-run "
          "(docs/SEE_AND_TEST.md)." % (n_h, n_cpp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 22:12 UTC | END ]
