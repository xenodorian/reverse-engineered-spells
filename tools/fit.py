"""Calibrate category multipliers so spells of each level cluster near their budget.

The level 1 and cantrip targets are fixed by design (100 and 25). The level 2 target is free: it is
set each pass to the mean level 2 net cost, so the fit only minimizes level 2 spread. After the fit,
the level 2 budget is set so it sits above the level 2 mean by the same ratio as level 1's budget sits
above the level 1 mean.

Writes data/calibration.json. Pure Python, no dependencies.
"""
import json, math, os, statistics as st
import pricing as P

TARGET = {0: 20.0, 1: 95.0}
FIT_CATS = list(P.CATS)
BUDGET_CHECK = {0: 25.0, 1: 100.0}
LAMBDA = 20.0        # pull toward the hand-set base prices; keeps every multiplier sane
OVER = 12.0          # extra weight for cantrips and level 1 spells over budget or over the effect ceiling

def nets(spells):
    out = {0: [], 1: [], 2: []}
    for k, (s, spec) in spells.items():
        out[spec["level"]].append(P.score(spec, enforce=False)[1])
    return out

def excess_effects(spells):
    """Sum of squared amounts by which level 0 and 1 effect totals pass their ceilings."""
    tot = 0.0
    for k, (s, spec) in spells.items():
        lvl = spec["level"]
        if lvl < 2:
            rows, t = P.score(spec, enforce=False)
            e = sum(r[2] for r in rows if r[0] in ("Effect", "Floor"))
            tot += max(0.0, e - P.ceiling(lvl)) ** 2
    return tot

def objective(spells):
    n = nets(spells)
    t2 = st.mean(n[2])
    total = 0.0
    for lvl, vals in n.items():
        tgt = TARGET.get(lvl, t2)
        for v in vals:
            d = v - tgt
            total += (OVER if (lvl < 2 and v > BUDGET_CHECK[lvl]) else 1.0) * d * d
    total += OVER * excess_effects(spells)
    total += LAMBDA * len(spells) * sum(math.log(P.MULT[c]) ** 2 for c in FIT_CATS)
    return total

def descend(spells, rounds=60):
    step = 0.20
    best = objective(spells)
    for _ in range(rounds):
        improved = False
        for c in FIT_CATS:
            for f in (1 + step, 1 / (1 + step)):
                old = P.MULT[c]
                P.MULT[c] = min(3.0, max(0.25, old * f))
                v = objective(spells)
                if v < best - 1e-9:
                    best, improved = v, True
                else:
                    P.MULT[c] = old
        if not improved:
            step *= 0.6
            if step < 0.004:
                break
    return best

def observed_caps(spells):
    """Highest quantity used per scalable item at each level, carried upward so a higher level
    never has a lower cap than the level below it."""
    seen = {}
    for k, (s, spec) in spells.items():
        for item, q in spec["lines"]:
            lab, base, unit, ref, cat, tier = P.ITEMS.get(item, (0, 0, "flat", None, 0, 0))
            if item in P.ITEMS and unit != "flat" and item not in P.CONTROL:
                key = P.cap_key(item, spec)
                d = seen.setdefault(key, {})
                d[spec["level"]] = max(d.get(spec["level"], 0), q)
    caps = {}
    for item, d in seen.items():
        run = 0
        caps[item] = {}
        for lvl in (0, 1, 2):
            if lvl in d:
                run = max(run, d[lvl])
                caps[item][str(lvl)] = run
            elif run:
                caps[item][str(lvl)] = run
    return caps

def control_caps(spells):
    mx = {0: 0.0, 1: 0.0, 2: 0.0}
    for k, (s, spec) in spells.items():
        tot = sum(P.price(i, q) for i, q in spec["lines"] if i in P.CONTROL)
        mx[spec["level"]] = max(mx[spec["level"]], tot)
    mx[2] = max(mx[2], mx[1])
    return {str(k): math.ceil(v) for k, v in mx.items()}

def run(spells):
    before = nets(spells)
    P.MULT.update({c: 1.0 for c in P.CATS})
    obj = descend(spells)
    after = nets(spells)
    m1, m2 = st.mean(after[1]), st.mean(after[2])
    b2 = int(round(100 * m2 / m1 / 25.0)) * 25
    # level 2 effect floor: just above the largest level 1 effect total, rounded up to 5
    l1_eff = []
    for k, (s, spec) in spells.items():
        if spec["level"] == 1:
            rows, t = P.score(spec, enforce=False)
            l1_eff.append(sum(r[2] for r in rows if r[0] in ("Effect", "Floor") and True))
    cal = {"mult": {c: round(P.MULT[c], 3) for c in P.CATS}, "budgets": {"0": 25, "1": 100, "2": b2},
           "l2_floor": P.L2_FLOOR, "caps": observed_caps(spells), "control_cap": control_caps(spells),
           "fit": {"objective": round(obj, 1),
                   "mean_before": {str(k): round(st.mean(v), 1) for k, v in before.items()},
                   "mean_after": {str(k): round(st.mean(v), 1) for k, v in after.items()},
                   "sd_after": {str(k): round(st.pstdev(v), 1) for k, v in after.items()}}}
    json.dump(cal, open(P.CAL_PATH, "w"), indent=2); open(P.CAL_PATH, "a").write("\n")
    print(json.dumps(cal["mult"]))
    print(cal["fit"]); print("budgets", cal["budgets"], "control cap", cal["control_cap"])
