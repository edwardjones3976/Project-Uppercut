<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ] -->

# Contribution Tagging — Project Uppercut

**Status:** Adopted by Director instruction, 2026-08-02. Recorded in `docs/decisions/0006`, which
supersedes the contrary position in Decision 0005.

Every document, file, code contribution and edit carries an identifying tag at **both start and end**.

## Format

```
[ <Assistant/Tool Name> | <Model/System Label> | <YYYY-MM-DD HH:MM UTC> | START ]
...
[ <Assistant/Tool Name> | <Model/System Label> | <YYYY-MM-DD HH:MM UTC> | END ]
```

Time is 24-hour **UTC**. Obtain it with `date -u` rather than estimating. Use the comment syntax of
the file: `#` for Python and YAML, `//` for C++ and C#, `<!-- -->` for Markdown and XML.

## Always use the currently running model

Read the model label from the session environment every time. Never hardcode or copy a previous one.

## Files that cannot carry comments

JSON, JSONL, CSV, lock files and byte-compared fixtures must not be broken to fit a tag. JSON files
instead carry a `contribution` object:

```json
{ "contribution": { "agent": "...", "model": "...", "start": "...", "end": "..." } }
```

Schemas that validate tagged data permit this key explicitly. Where neither form is possible, the tag
goes in the commit message or edit summary instead.

## Editing existing work

Add a new inline tag at the edit site. **Never modify or remove another contributor's tag lines** —
they are audit evidence.

## Generated artifacts

Generated evidence (simulation reports, replay logs) carries the tag of the tool run that produced it
in its `contribution` block, not a hand-written one.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ] -->
