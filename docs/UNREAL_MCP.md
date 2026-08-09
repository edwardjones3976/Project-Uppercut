<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09 19:40 UTC | unreal mcp start ] -->
# Unreal MCP — an agent seat at the editor

## What this is

`ModelContextProtocol` is **Epic's own plugin**, shipped inside UE 5.8 and
described in its own manifest as an *"Anthropic MCP (Model Context Protocol)
server implementation for Unreal Engine."* It is not a third-party download.
It was already on disk at
`Engine/Plugins/Experimental/ModelContextProtocol/`; nothing was fetched or
installed to enable it.

It is marked `IsExperimentalVersion: true` and `EnabledByDefault: false`.

## What was changed

1. `sandbox/UppercutSandbox.uproject` — `ModelContextProtocol` and
   `AllToolsets` enabled, both with `TargetAllowList: ["Editor"]`. The
   allow-list is deliberate: the MCP plugin carries `NoRedist: true` and Epic's
   own documentation cautions against shipping with it. It is editor tooling,
   so it is scoped to editor targets and cannot reach a packaged build.
2. `.mcp.json` at the repo root — an HTTP client entry pointing at
   `http://127.0.0.1:8000/mcp`, so any MCP client opened on this repo finds the
   editor without per-machine setup.
3. `sandbox/Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini` —
   `bAutoStartServer=True`. This is a per-user file and is not committed; the
   same switch lives in **Editor Preferences > General > Model Context
   Protocol**. Without it the server has to be started by hand each session.
   The command line `-ModelContextProtocolStartServer` does the same thing.

## The wire

HTTP only — not stdio, not WebSocket. `127.0.0.1:8000/mcp`, **loopback only**,
and there is no authentication layer. The listener rejects non-loopback
connections by design, which is the whole security model: the server is safe
because nothing off the machine can reach it.

That has a direct consequence worth stating plainly, because it is easy to
assume otherwise: **a Cowork session running in Anthropic's cloud cannot use
this.** The cloud sandbox has no route to a loopback port on blackbox. The
clients that can use it are the ones running on the machine itself — Claude
Code in a terminal, or the Claude desktop app.

## Toolsets

`AllToolsets` is an aggregator that pulls in every authored toolset. The ones
that matter to this project are `AutomationTestToolset` (run automation tests),
`EditorToolset`, `SlateInspectorToolset` (inspect UI), `GASToolsets`,
`StateTreeToolset`, `PhysicsToolsets` and `AnimationAssistantToolset`. Tool
search is on (`bEnableToolSearch=True`), so `tools/list` stays small and the
client discovers toolset tools on demand rather than registering hundreds at
startup.

Custom tools can be registered through the Toolset Registry — the obvious
future one being a tool that loads a recorded fight stream into the sandbox and
plays it, which is the arena side of the First Bell artifact.

## What Unreal MCP does NOT change

It is editor automation. It is not a runtime feature, it has no authority over
combat, and nothing it can do is allowed to become a source of truth. The
existing fence applies unchanged: presentation may not gain combat authority.
An agent moving actors around in the editor is presentation.

## Unity

Not installed on this machine, and this project has no Unity target. Unity's
own MCP server exists and is first-party, but it requires Unity 6 (6000.0) or
later with the AI Assistant package, and it is irrelevant to an Unreal project.
Recorded here so a later session does not go looking for it.
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09 19:40 UTC | unreal mcp end ] -->
