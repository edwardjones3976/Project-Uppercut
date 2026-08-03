# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:12 UTC | START ]
"""Shared headless Blueprint-authoring discipline, extracted from the generators that
earned it. Import this from new generators; the existing bp_generate_state_walker.py
and bp_generate_range_walker.py keep their inline copies deliberately - they work, and
rewriting working engine code to share a module is risk without benefit.

The rules, each bought with a debugging session (see determinism_probe_results.md):

  1. NEVER trust the handle returned by add_call_function_node. Promotable operators
     get replaced during creation and handles alias other nodes. Every node is
     resolved by a BEFORE/AFTER delta of the graph's node list, filtered by expected
     class, newest numeric suffix winning.
  2. NEVER trust try_create_connection returning True. Every connection is verified
     from the DESTINATION side by owning node and pin name. A single-hop autocast is
     accepted only after tracing the hop back to the real source, and the conversion
     node is absorbed into the seen-set immediately so it cannot win a later delta.
  3. Value-critical chains wire strict=True: a conversion node there means a type
     mismatch that silently destroys the value (the int-truncation defect that made
     two accumulators read zero).
  4. Every set_pin_value is read back and compared.
  5. get_basic_type_by_name("double") returns an INT-category type. Steal the real
     floating type from a live engine pin instead - see steal_types().
  6. Floating constants never go on pins; promotable DOUBLE pins drop literals.
     Put them on member variables and set them on the CDO.
"""
import unreal

lib = unreal.BlueprintEditorLibrary
GE = unreal.BlueprintGraphEditor
PL = unreal.BlueprintGraphPinLibrary
EAL = unreal.EditorAssetLibrary

KML = "/Script/Engine.KismetMathLibrary:"
KSL = "/Script/Engine.KismetSystemLibrary:"
KStr = "/Script/Engine.KismetStringLibrary:"
KArr = "/Script/Engine.KismetArrayLibrary:"

NODE_CLASSES = ("K2Node_CallFunction", "K2Node_PromotableOperator",
                "K2Node_CallArrayFunction", "K2Node_GetArrayItem",
                "K2Node_CommutativeAssociativeBinaryOperator")

steps = []
GG = None


def step(m, v=None):
    steps.append(m if v is None else "%s -> %s" % (m, v))


class G:
    def __init__(self, ge):
        self.ge = ge
        self.seen = set(n.get_name() for n in ge.list_all_nodes())

    def _delta(self, what, klasses):
        now = {n.get_name(): n for n in self.ge.list_all_nodes()}
        new = [now[k] for k in now if k not in self.seen]
        self.seen = set(now)
        cands = [n for n in new if n.get_class().get_name() in klasses]
        if not cands:
            raise RuntimeError("%s: no new node of class %s among %d new"
                               % (what, klasses, len(new)))

        def suffix(n):
            tail = n.get_name().rsplit("_", 1)[-1]
            return int(tail) if tail.isdigit() else -1
        return max(cands, key=suffix)

    def fn(self, path):
        self.ge.add_call_function_node(path)
        return self._delta(path, NODE_CLASSES)

    def getv(self, name):
        self.ge.add_get_member_variable_node(name)
        return self._delta("get " + name, ("K2Node_VariableGet",))

    def setv(self, name):
        self.ge.add_set_member_variable_node(name)
        return self._delta("set " + name, ("K2Node_VariableSet",))

    def branch(self):
        self.ge.add_branch_node()
        return self._delta("branch", ("K2Node_IfThenElse",))

    def absorb(self, node):
        self.seen.add(node.get_name())
        return node


def activate(g):
    """Register the active G so wire() can absorb autocast nodes into its seen-set."""
    global GG
    GG = g
    return g


def pin_of(node, name, direction):
    finder = lib.find_output_pin if direction == "out" else lib.find_input_pin
    p = finder(node, name)
    if not PL.is_valid(p):
        raise RuntimeError("pin '%s' (%s) missing on %s" % (name, direction, node.get_name()))
    return p


def wire(src_node, src_pin, dst_node, dst_pin, label, strict=False):
    a = pin_of(src_node, src_pin, "out")
    b = pin_of(dst_node, dst_pin, "in")
    if not PL.try_create_connection(a, b):
        raise RuntimeError("connect refused: " + label)
    linked = PL.list_connected_pins(b)
    ok = any(PL.get_owning_node(lp).get_name() == src_node.get_name()
             and str(PL.get_pin_name(lp)) == src_pin
             for lp in linked)
    if not ok and strict:
        raise RuntimeError("STRICT wire got a conversion node: " + label)
    if not ok:
        for lp in linked:
            hop = PL.get_owning_node(lp)
            for i in range(6):
                try:
                    hp = lib.find_input_pin_by_index(hop, i)
                except Exception:
                    break
                if not PL.is_valid(hp):
                    break
                if any(PL.get_owning_node(x).get_name() == src_node.get_name()
                       and str(PL.get_pin_name(x)) == src_pin
                       for x in PL.list_connected_pins(hp)):
                    step("autocast accepted: %s via %s" % (label, hop.get_name()))
                    if GG is not None:
                        GG.seen.add(hop.get_name())
                    return
        raise RuntimeError("connect VERIFY FAILED: " + label)


def wire_exec(src_node, dst_node, label):
    a = lib.find_then_pin(src_node)
    b = lib.find_execute_pin(dst_node)
    if not (PL.is_valid(a) and PL.is_valid(b)):
        raise RuntimeError("exec pins missing: " + label)
    if not PL.try_create_connection(a, b):
        raise RuntimeError("exec connect refused: " + label)
    if not any(PL.get_owning_node(lp).get_name() == src_node.get_name()
               for lp in PL.list_connected_pins(b)):
        raise RuntimeError("exec VERIFY FAILED: " + label)


def setpin(node, pin, value, label):
    p = pin_of(node, pin, "in")
    if not PL.set_pin_value(p, value):
        raise RuntimeError("set_pin_value refused: " + label)
    back = str(PL.get_pin_value(p))
    if value.rstrip("0").rstrip(".") not in back and value not in back:
        raise RuntimeError("set_pin VERIFY FAILED %s: wrote %r read %r" % (label, value, back))


def steal_types(g):
    """get_basic_type_by_name lies about 'double'. Take the real types from live pins."""
    tmp_sin = g.fn(KML + "Sin")
    t_double = PL.get_pin_type(pin_of(tmp_sin, "ReturnValue", "out"))
    tmp_ri = g.fn(KML + "RandomIntegerFromStream")
    t_int = PL.get_pin_type(pin_of(tmp_ri, "ReturnValue", "out"))
    tmp_b = g.fn(KML + "Greater_DoubleDouble")
    t_bool = PL.get_pin_type(pin_of(tmp_b, "ReturnValue", "out"))
    g.ge.remove_nodes([tmp_sin, tmp_ri, tmp_b])
    for n in (tmp_sin, tmp_ri, tmp_b):
        g.seen.discard(n.get_name())
    return t_double, t_int, t_bool


def marker_chain(g, prefix, sources, exec_from, label="marker"):
    """BuildString_Int chain -> PrintString(log only). sources = [(node, pin), ...]."""
    parts = [g.fn(KStr + "BuildString_Int") for _ in range(len(sources))]
    setpin(parts[0], "AppendTo", prefix, "s0.prefix")
    for k in range(len(sources) - 1):
        setpin(parts[k], "Suffix", "|", "s%d.suffix" % k)
        wire(parts[k], "ReturnValue", parts[k + 1], "AppendTo", "s%d->s%d" % (k, k + 1))
    for k, (node, pin) in enumerate(sources):
        wire(node, pin, parts[k], "InInt", "%s src%d" % (label, k))
    pr = g.fn(KSL + "PrintString")
    wire(parts[-1], "ReturnValue", pr, "InString", "chain->print")
    setpin(pr, "bPrintToScreen", "false", "pr.screen")
    setpin(pr, "bPrintToLog", "true", "pr.log")
    wire_exec(exec_from, pr, "exec->print")
    return pr


def quit_after(g, bp_print, tick_node, idx_node, max_ticks):
    """Instance 0 quits the game once TickCount reaches max_ticks."""
    ge_i = g.fn(KML + "GreaterEqual_IntInt"); eq_i = g.fn(KML + "EqualEqual_IntInt")
    an = g.fn(KML + "BooleanAND"); br = g.branch(); qn = g.fn(KSL + "QuitGame")
    wire(tick_node, "TickCount", ge_i, "A", "tc->ge.A")
    setpin(ge_i, "B", str(max_ticks), "ge.B")
    wire(idx_node, "MyIndex", eq_i, "A", "idx->eq.A"); setpin(eq_i, "B", "0", "eq.B")
    wire(ge_i, "ReturnValue", an, "A", "ge->and.A")
    wire(eq_i, "ReturnValue", an, "B", "eq->and.B")
    cond = lib.find_condition_pin(br)
    if not PL.try_create_connection(pin_of(an, "ReturnValue", "out"), cond):
        raise RuntimeError("and->branch refused")
    wire_exec(bp_print, br, "print->branch")
    wire_exec(br, qn, "branch->quit")
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:12 UTC | END ]
