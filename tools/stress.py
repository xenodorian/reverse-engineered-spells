"""Try to break the budget: inflate each spell one lever at a time and see how far the rules let it go.

Lever 1: raise the spell's main magnitude (damage, healing, or temporary HP).
Lever 2: add extra targets.
Lever 3: re-file the spell one level lower and see which rule blocks it.
Each lever is run twice: with only the budget enforced, and with every rule enforced.
"""
import copy, statistics as st
import pricing as P

MAIN = ("dmg", "c_dmg", "heal", "temp_hp")

def _legal(spec, enforce):
    try:
        rows, t = P.score(spec, enforce=enforce)
    except ValueError:
        return False
    return t <= P.BUDGETS[spec["level"]] + 1e-9

def _with(spec, item, q):
    s = copy.deepcopy(spec)
    s["lines"] = [(i, q if i == item else v) for i, v in spec["lines"]]
    if s.get("upcast") and s["upcast"][0] == item:
        pass
    return s

def max_magnitude(spec, item, enforce):
    q0 = next(v for i, v in spec["lines"] if i == item)
    q = q0
    while _legal(_with(spec, item, q + 0.5), enforce) and q < 400:
        q += 0.5
    return q0, q

def max_targets(spec, enforce):
    lines = list(spec["lines"])
    has = any(i == "target_extra" for i, v in lines)
    if not has:
        lines = lines + [("target_extra", 0)]
    s0 = copy.deepcopy(spec); s0["lines"] = lines
    cur = next(v for i, v in lines if i == "target_extra")
    n = cur
    def with_n(k):
        s = copy.deepcopy(s0)
        s["lines"] = [(i, k if i == "target_extra" else v) for i, v in lines]
        return s
    while n < 60 and _legal(with_n(n + 1), enforce):
        n += 1
    return cur, n

def block_reason(spec, new_level):
    s = copy.deepcopy(spec); s["level"] = new_level
    try:
        rows, t = P.score(s)
    except ValueError as e:
        m = str(e)
        if "cannot be used" in m: return "effect tier"
        if "capped" in m: return "magnitude cap"
        if "control" in m: return "control cap"
        if "strength" in m: return "effect ceiling"
        if "flat item" in m: return "flat item"
        return "other rule"
    return "budget" if t > P.BUDGETS[new_level] else "allowed"

def compute(spells):
    out = {"mag": [], "tgt": [], "hop": []}
    for k, (s, spec) in spells.items():
        item = next((i for i in MAIN if any(x == i for x, v in spec["lines"])), None)
        if item:
            q0, qb = max_magnitude(spec, item, False)
            _, qr = max_magnitude(spec, item, True)
            out["mag"].append((s["name"], spec["level"], item, q0, qb, qr))
        t0, tb = max_targets(spec, False)
        _, tr = max_targets(spec, True)
        out["tgt"].append((s["name"], spec["level"], t0, tb, tr))
        if spec["level"] >= 1:
            out["hop"].append((s["name"], spec["level"], block_reason(spec, spec["level"] - 1)))
    return out

def run(spells):
    r = compute(spells)
    for lvl in (0, 1, 2):
        m = [x for x in r["mag"] if x[1] == lvl]
        if m:
            rb = [x[4] / x[3] for x in m]; rr = [x[5] / x[3] for x in m]
            print(f"level {lvl}: {len(m)} magnitude spells. Max growth, budget only: median x{st.median(rb):.2f}, worst x{max(rb):.2f}. With rules: median x{st.median(rr):.2f}, worst x{max(rr):.2f}")
        t = [x for x in r["tgt"] if x[1] == lvl]
        tb = [x[3] - x[2] for x in t]; tr = [x[4] - x[2] for x in t]
        print(f"level {lvl}: extra targets possible, budget only: median {st.median(tb):g}, max {max(tb)}. With rules: median {st.median(tr):g}, max {max(tr)}")
    from collections import Counter
    for lvl in (1, 2):
        c = Counter(x[2] for x in r["hop"] if x[1] == lvl)
        print(f"level {lvl} spells filed one level lower: {dict(c)}")
