# [ Claude (Cowork) | Claude Opus 4.7 (claude-opus-4-7) | 2026-08-09 19:52 UTC | mcp client start ]
# Minimal MCP client for the editor's loopback HTTP server. Runs ON blackbox,
# which is inside the loopback fence - the cloud cannot reach 127.0.0.1 here.
#
# Modes: list | desc <toolset> | call <tool> [json] | callfile <tool> <file>
#        | shot <tool> <dest.png> [json]
# Toolset tools go through call_tool (see docs/UNREAL_MCP.md, live-test notes).
# Proven against the live editor 2026-08-09: session init, toolset discovery,
# camera moves, actor selection, and the editor photographing itself.
import json
import sys
import urllib.request
import urllib.error

URL = "http://127.0.0.1:8000/mcp"
SESSION = [None]


def rpc(method, params=None, rid=None, timeout=180):
    body = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        body["params"] = params
    if rid is not None:
        body["id"] = rid
    h = {"Content-Type": "application/json",
         "Accept": "application/json, text/event-stream"}
    if SESSION[0]:
        h["Mcp-Session-Id"] = SESSION[0]
    req = urllib.request.Request(URL, json.dumps(body).encode(), h)
    r = urllib.request.urlopen(req, timeout=timeout)
    sid = r.headers.get("Mcp-Session-Id") or r.headers.get("mcp-session-id")
    if sid:
        SESSION[0] = sid
    raw = r.read().decode("utf-8", "replace")
    ctype = r.headers.get("Content-Type") or ""
    if "event-stream" in ctype:
        datas = [ln[5:].strip() for ln in raw.splitlines()
                 if ln.startswith("data:")]
        raw = datas[-1] if datas else ""
    return json.loads(raw) if raw.strip() else None


def connect():
    out = rpc("initialize", {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "uppercut-scratch-client",
                       "version": "0.1"}}, rid=1)
    rpc("notifications/initialized")
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "list"
    init = connect()
    info = init["result"]["serverInfo"]
    print("SERVER %s %s  session=%s"
          % (info.get("name"), info.get("version"), SESSION[0]))
    if mode == "list":
        tools = rpc("tools/list", {}, rid=2)
        for t in tools["result"]["tools"]:
            print("TOOL", t["name"])
            print("   ", (t.get("description") or "").split("\n")[0][:150])
    elif mode == "desc":
        ts = sys.argv[2]
        out = rpc("tools/call", {"name": "describe_toolset",
                                 "arguments": {"toolset_name": ts}}, rid=2,
                  timeout=300)
        inner = json.loads(out["result"]["content"][0]["text"])
        for t in inner["tools"]:
            print("TOOL", t["name"])
            print("   ", (t.get("description") or "").split("\n")[0][:140])
    elif mode == "shot":
        # call a capture tool and save any returned image content to disk
        import base64
        name = sys.argv[2]
        dest = sys.argv[3]
        args = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
        out = rpc("tools/call", {"name": name, "arguments": args}, rid=2,
                  timeout=300)
        n = 0
        for c in out["result"]["content"]:
            if c.get("type") == "image":
                with open(dest, "wb") as fh:
                    fh.write(base64.b64decode(c["data"]))
                n += 1
                print("SAVED", dest, c.get("mimeType"))
            elif c.get("type") == "text":
                print("TEXT", c["text"][:500])
        if not n:
            print("NO IMAGE CONTENT")
    elif mode == "callfile":
        # args come from a JSON file - PowerShell mangles inline JSON quoting
        name = sys.argv[2]
        with open(sys.argv[3], encoding="utf-8") as fh:
            args = json.load(fh)
        out = rpc("tools/call", {"name": name, "arguments": args}, rid=2,
                  timeout=300)
        print(json.dumps(out, indent=1)[:12000])
    elif mode == "call":
        name = sys.argv[2]
        args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        out = rpc("tools/call", {"name": name, "arguments": args}, rid=2,
                  timeout=300)
        print(json.dumps(out, indent=1)[:12000])
# [ Claude (Cowork) | Claude Opus 4.7 (claude-opus-4-7) | 2026-08-09 19:52 UTC | mcp client end ]  
