"""Calibrate the prices against the canon spells.

Budgets are inputs: cantrip 25 and level 1 100 are fixed by design. Level 2 (150) and level 3 (250) come
from the earlier scaling study, and the held-out evidence below checks them.

Stage 1  Fit the shared prices (category multipliers and the convexity exponent) to the spells that are made
         only of reusable items, so each costs about its budget. Spells that contain an item no other spell
         uses are left out, because that item could absorb any error.
Stage 2  Price each single-use item so its spell costs about its budget. This is the effect ladder: how
         much a canon effect is worth at its level, once the delivery parts are paid for.
Stage 3  Held-out check. Fit the shared prices on cantrips and level 1 only, then price the level 2 and 3
         spells that use only reusable items. What they cost is what the budget at that level must be.

Writes data/calibration.json. Pure Python, no dependencies.
"""
import json, math, statistics as st
from collections import Counter
import pricing as P

BUDGET_IN = {0: 25.0, 1: 100.0, 2: 150.0, 3: 250.0}
TARGET_FRAC = 0.97       # canon spells are fitted to this share of the budget so they stay legal
LAMBDA = 0.03            # pull toward the hand-set prices
EXP_RANGE = (0.0, 1.4)
FIT_EXTRA = {"dmg_rider", "zone_damage", "miss_half", "temp_hp", "temp_hp_recurring"}   # damage and healing riders used by few spells
FIT_USES = 3             # items used by this many spells or fewer are priced from their spells

def lines_of(spec):
    out = list(spec["lines"])
    for m in spec.get("modes") or []:
        out += list(m)
    return out

def classify(spells):
    use = Counter()
    for k, (s, spec) in spells.items():
        for i in {i for i, q in lines_of(spec) if i in P.ITEMS}:
            use[i] += 1
    # Capabilities (utility, buffs, conditions) used by three spells or fewer are priced from those spells.
    # An item used by one spell is priced exactly from it. An item used by two or three is priced at the
    # median of what each spell implies, and the spread is a measure of how consistent canon is.
    # Damage, healing, and area follow formulas, and capabilities used four or more times are fitted as shared prices.
    bespoke = {i for i, c in use.items() if c <= FIT_USES and (P.ITEMS[i][4] in ("util", "buff", "cond") or i in FIT_EXTRA)}
    generic_spells = [k for k, (s, spec) in spells.items() if not any(i in bespoke for i, q in lines_of(spec))]
    return use, bespoke, generic_spells

def net(spec):
    return P.score(spec, enforce=False)[1]

def objective(spells, keys, levels=None):
    total = 0.0
    n = 0
    for k in keys:
        s, spec = spells[k]
        if levels is not None and spec["level"] not in levels:
            continue
        tgt = TARGET_FRAC * BUDGET_IN[spec["level"]]
        e = net(spec) / tgt - 1
        total += e * e; n += 1
    total /= max(n, 1)
    total += LAMBDA * sum(math.log(P.MULT[c]) ** 2 for c in P.CATS) / len(P.CATS)
    return total

def descend(spells, keys, levels=None, free_exp=True, rounds=80):
    step = 0.25
    best = objective(spells, keys, levels)
    for _ in range(rounds):
        improved = False
        for c in P.CATS:
            for f in (1 + step, 1 / (1 + step)):
                old = P.MULT[c]
                P.MULT[c] = min(4.0, max(0.2, old * f))
                v = objective(spells, keys, levels)
                if v < best - 1e-12:
                    best, improved = v, True
                else:
                    P.MULT[c] = old
        if free_exp:
            for d in (step * 0.4, -step * 0.4):
                old = P.EXP
                P.EXP = min(EXP_RANGE[1], max(EXP_RANGE[0], old + d))
                v = objective(spells, keys, levels)
                if v < best - 1e-12:
                    best, improved = v, True
                else:
                    P.EXP = old
        if not improved:
            step *= 0.6
            if step < 0.003:
                break
    return best

def reset():
    P.MULT.update({c: 1.0 for c in P.CATS})
    P.EXP = 0.4
    P.ITEM_BASE.clear()

def solve_bespoke(spells, bespoke):
    """For each spell, scale its fitted items together (keeping their relative prior prices) until the spell
    costs its target. Done by bisection because the cost also depends on the items through extra targets and
    the weak-effect duration factor. An item used by several spells gets the median of what each implies."""
    prior = {i: P.ITEMS[i][1] for i in bespoke}
    P.ITEM_BASE.clear(); P.ITEM_BASE.update(prior)
    implied = {}
    for it in range(6):
        implied = {i: [] for i in bespoke}
        for k, (s, spec) in spells.items():
            bs = [(i, q) for i, q in lines_of(spec) if i in bespoke]
            if not bs:
                continue
            keep = {i: P.ITEM_BASE[i] for i, q in bs}
            tgt = TARGET_FRAC * BUDGET_IN[spec["level"]]
            def f(lam):
                for i, q in bs:
                    P.ITEM_BASE[i] = prior[i] * lam
                return net(spec)
            lo, hi = 1e-6, 1e4
            if f(lo) >= tgt:
                lam = 0.02          # the rest of the spell already costs its budget: leave the effect a token price
            else:
                for _ in range(60):
                    mid = math.sqrt(lo * hi)
                    if f(mid) < tgt:
                        lo = mid
                    else:
                        hi = mid
                lam = math.sqrt(lo * hi)
            for i, q in bs:
                implied[i].append(prior[i] * lam)
            for i, v in keep.items():
                P.ITEM_BASE[i] = v
        for i, v in implied.items():
            if v:
                P.ITEM_BASE[i] = st.median(v)
    return implied

def run(spells):
    use, bespoke, generic = classify(spells)
    by_level = Counter(spells[k][1]["level"] for k in generic)
    print(f"{len(generic)} spells use only reusable items {dict(by_level)}; {len(bespoke)} single-use effect items")
    # stage 1
    reset(); P.ITEM_BASE.update({i: P.ITEMS[i][1] for i in bespoke})
    obj = descend(spells, generic)
    mult1, exp1 = dict(P.MULT), P.EXP
    # stage 2
    item_implied = solve_bespoke(spells, bespoke)
    # stage 3: held out
    saved = (dict(P.MULT), P.EXP, dict(P.ITEM_BASE))
    reset(); P.ITEM_BASE.update({i: P.ITEMS[i][1] for i in bespoke})
    descend(spells, generic, levels={0, 1})
    held = {}
    for k in generic:
        s, spec = spells[k]
        if spec["level"] >= 2:
            held[k] = net(spec) / TARGET_FRAC
    implied = {l: st.median([v for k, v in held.items() if spells[k][1]["level"] == l]) for l in (2, 3) if any(spells[k][1]["level"] == l for k in held)}
    expo = {}
    for e in (0.0, 0.4, 0.8, 1.2):
        reset(); P.ITEM_BASE.update({i: P.ITEMS[i][1] for i in bespoke}); P.EXP = e
        descend(spells, generic, levels={0, 1}, free_exp=False)
        expo[e] = {l: st.median([net(spells[k][1]) / TARGET_FRAC for k in held if spells[k][1]["level"] == l]) for l in implied}
    P.MULT.update(saved[0]); P.EXP = saved[1]; P.ITEM_BASE.clear(); P.ITEM_BASE.update(saved[2])
    # report
    res = {}
    for k in generic:
        s, spec = spells[k]
        res[k] = net(spec) / BUDGET_IN[spec["level"]]
    allnet = {}
    for k, (s, spec) in spells.items():
        allnet[k] = net(spec) / BUDGET_IN[spec["level"]]
    cal = {"mult": {c: round(P.MULT[c], 4) for c in P.CATS}, "exp": round(P.EXP, 4),
           "budgets": {str(k): int(v) for k, v in BUDGET_IN.items()},
           "item_base": {i: round(v, 3) for i, v in P.ITEM_BASE.items()},
           "fit": {"objective": round(obj, 5), "target_fraction": TARGET_FRAC,
                   "generic_spells": len(generic), "generic_by_level": {str(k): v for k, v in by_level.items()},
                   "held_out_implied_budget": {str(l): round(v, 1) for l, v in implied.items()},
                   "held_out_by_exponent": {str(e): {str(l): round(v, 1) for l, v in d.items()} for e, d in expo.items()},
                   "generic_ratio": {k: round(v, 3) for k, v in res.items()},
                   "item_implied": {i: [round(x, 2) for x in v] for i, v in item_implied.items() if len(v) > 1}}}
    json.dump(cal, open(P.CAL_PATH, "w"), indent=2); open(P.CAL_PATH, "a").write("\n")
    print("mult", cal["mult"]); print("exp", cal["exp"])
    errs = [abs(v - TARGET_FRAC) / TARGET_FRAC for v in res.values()]
    print(f"generic-only spells: mean abs error {st.mean(errs) * 100:.0f}%, worst {max(errs) * 100:.0f}%")
    print("held-out implied budgets", cal["fit"]["held_out_implied_budget"], "by exponent", cal["fit"]["held_out_by_exponent"])
