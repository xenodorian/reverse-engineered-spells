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
BUDGET_CHECK = {0: 25.0, 1: 100.0, 2: 10**6, 3: 10**6}
LAMBDA = 20.0        # pull toward the hand-set base prices; keeps every multiplier sane
OVER = 12.0          # extra weight for cantrips and level 1 spells over budget or over the effect ceiling

def nets(spells):
    out = {0: [], 1: [], 2: [], 3: []}
    for k, (s, spec) in spells.items():
        out[spec["level"]].append(P.score(spec, enforce=False)[1])
    return out

def excess_effects(spells):
    """Sum of squared amounts by which level 0 and 1 effect totals pass their ceilings."""
    tot = 0.0
    for k, (s, spec) in spells.items():
        lvl = spec["level"]
        if lvl < 3:
            rows, t = P.score(spec, enforce=False)
            e = sum(r[2] for r in rows if r[0] in ("Effect", "Floor"))
            tot += max(0.0, e - P.ceiling(lvl)) ** 2
    return tot

def objective(spells):
    n = nets(spells)
    total = 0.0
    for lvl, vals in n.items():
        if lvl == 3:
            continue            # level 3 is held out: it does not pull on the prices
        tgt = TARGET.get(lvl, st.mean(vals))
        for v in vals:
            d = v - tgt
            total += (OVER if v > BUDGET_CHECK[lvl] else 1.0) * d * d
    total += OVER * excess_effects(spells)
    total += LAMBDA * sum(1 for v in spells.values() if v[1]['level'] < 3) * sum(math.log(P.MULT[c]) ** 2 for c in FIT_CATS)
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
        for lvl in (0, 1, 2, 3):
            if lvl in d:
                run = max(run, d[lvl])
                caps[item][str(lvl)] = run
            elif run:
                caps[item][str(lvl)] = run
    return caps

def control_caps(spells):
    mx = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}
    for k, (s, spec) in spells.items():
        tot = sum(P.price(i, q) for i, q in spec["lines"] if i in P.CONTROL)
        mx[spec["level"]] = max(mx[spec["level"]], tot)
    mx[2] = max(mx[2], mx[1]); mx[3] = max(mx[3], mx[2])
    return {str(k): math.ceil(v) for k, v in mx.items()}

def cover(vals):
    """Smallest multiple of 25 that covers the strongest spell."""
    return int(math.ceil(max(vals) / 25.0 - 1e-9)) * 25

def run(spells):
    """Prices are fitted to cantrips, level 1, and level 2 (levels 0 and 1 against fixed targets, level 2 for
    spread only). Level 3 is held out: it is priced with those prices and its budget is measured, not fitted.
    Budget for level 2 or 3 = smallest multiple of 25 covering the strongest spell at that level.
    Floors: level 1 is 50 (half of 100). From level 2 up the floor is the previous level's budget."""
    P.MULT.update({c: 1.0 for c in P.CATS})
    P.FLOORS.clear(); P.FLOORS.update({1: 50, 2: 100, 3: 150})
    P.BUDGETS.update({0: 25, 1: 100, 2: 150, 3: 10**6})
    BUDGET_CHECK.update({0: 25.0, 1: 100.0, 2: 150.0, 3: 10**6})   # the level 2 budget of 150 is held from the earlier study
    before = nets(spells)
    obj = descend(spells)
    n = nets(spells)
    b2 = cover(n[2])      # confirms 150 still covers the strongest level 2 spell
    P.BUDGETS.update({2: b2}); P.FLOORS.update({3: b2})
    n = nets(spells)
    budgets = {0: 25, 1: 100, 2: b2, 3: cover(n[3])}
    P.BUDGETS.update(budgets)
    after = nets(spells)
    over = {l: round(max(v), 1) for l, v in after.items() if max(v) > budgets[l] + 1e-9}
    print(f"budgets {budgets}, floors {dict(P.FLOORS)}, over budget: {over or 'none'}")
    print("mean", {l: round(st.mean(v), 1) for l, v in after.items()}, "max", {l: round(max(v), 1) for l, v in after.items()})
    cal = {"mult": {c: round(P.MULT[c], 3) for c in P.CATS}, "budgets": {str(k): v for k, v in budgets.items()},
           "floors": {str(k): v for k, v in P.FLOORS.items()}, "caps": observed_caps(spells), "control_cap": control_caps(spells),
           "fit": {"objective": round(obj, 1),
                   "mean_before": {str(k): round(st.mean(v), 1) for k, v in before.items()},
                   "mean_after": {str(k): round(st.mean(v), 1) for k, v in after.items()},
                   "sd_after": {str(k): round(st.pstdev(v), 1) for k, v in after.items()},
                   "max_after": {str(k): round(max(v), 1) for k, v in after.items()}}}
    json.dump(cal, open(P.CAL_PATH, "w"), indent=2); open(P.CAL_PATH, "a").write("\n")
    print(json.dumps(cal["mult"]))
    print("control cap", cal["control_cap"])
