"""Scaling analysis across cantrips and levels 1 to 3. Produces docs/spell-scaling-analysis.md."""
import json, math, statistics as st
from collections import Counter
import pricing as P
import stress

# Average damage by spell level from the 2014 DMG "Spell Damage" table, level 0 to 9.
# UNVERIFIED: recalled from memory, not checked against the book. Only used as a cross-check.
DMG_TABLE = [5.5, 11, 16.5, 27.5, 33, 44, 55, 60.5, 66, 77]
LEVELS = (0, 1, 2, 3)
NAMES = {0: "Cantrip", 1: "Level 1", 2: "Level 2", 3: "Level 3"}

def tbl(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)

def n1(x):
    return f"{x:.1f}".rstrip("0").rstrip(".") if isinstance(x, float) else str(x)

def linfit(xs, ys):
    n = len(xs); mx, my = sum(xs) / n, sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    pred = [a + b * x for x in xs]
    ss_res = sum((y - p) ** 2 for y, p in zip(ys, pred)); ss_tot = sum((y - my) ** 2 for y in ys)
    return a, b, 1 - ss_res / ss_tot

def group_sums(spec):
    rows, t = P.score(spec, enforce=False)
    d = {c: 0.0 for c in ("dmg", "heal", "buff", "cond", "util", "area")}
    for item, q in spec["lines"]:
        if item in P.ITEMS and item != "target_extra":
            d[P.ITEMS[item][4]] += P.price(item, q)
    extra = sum(r[2] for r in rows if r[1].startswith("Additional targets"))
    d["area"] += extra
    d["floor top-up"] = sum(r[2] for r in rows if r[0] == "Floor")
    d["duration"] = next(r[2] for r in rows if r[0] == "Duration")
    d["range"] = P.RANGE[spec.get("price_range", spec["range"]).split(" (")[0]] * P.MULT["range"]
    d["casting"] = P.lookup(P.CASTING, spec["casting_time"]) * P.MULT["cast"]
    d["refunds"] = sum(r[2] for r in rows if r[0] in ("Refund", "Limit", "Cap", "Availability"))
    d["other"] = t - sum(v for k, v in d.items() if k != "other")
    return d, t

def dims_by_level(sp):
    res = {}
    for lvl in LEVELS:
        acc = {}
        specs = [spec for s, spec in sp.values() if spec["level"] == lvl]
        for spec in specs:
            d, t = group_sums(spec)
            for k, v in d.items():
                acc[k] = acc.get(k, 0) + v
        res[lvl] = {k: v / len(specs) for k, v in acc.items()}
    return res

def raw_metrics(sp):
    out = {}
    for lvl in LEVELS:
        S = [(s, spec) for s, spec in sp.values() if spec["level"] == lvl]
        n = len(S)
        def q(spec, items):
            return sum(v for i, v in spec["lines"] if i in items)
        dm = [q(sp_, ("dmg", "c_dmg")) for s, sp_ in S if q(sp_, ("dmg", "c_dmg"))]
        dmt = [q(sp_, ("dmg", "c_dmg", "dmg_recurring", "zone_damage")) for s, sp_ in S if q(sp_, ("dmg", "c_dmg"))]
        hl = [q(sp_, ("heal",)) for s, sp_ in S if q(sp_, ("heal",))]
        ctl = [c for c in (sum(P.price(i, v) for i, v in sp_["lines"] if i in P.CONTROL) for s, sp_ in S) if c]
        tg = [1 + q(sp_, ("target_extra",)) for s, sp_ in S]
        out[lvl] = {
         "n": n, "dmg_n": len(dm), "dmg_mean": st.mean(dm) if dm else 0, "dmg_max": max(dm) if dm else 0,
         "dmgt_mean": st.mean(dmt) if dmt else 0, "dmgt_max": max(dmt) if dmt else 0,
         "heal_n": len(hl), "heal_max": max(hl) if hl else 0, "ctl_n": len(ctl),
         "tg_mean": st.mean(tg), "tg_max": max(tg),
         "conc": sum(1 for s, _ in S if s["concentration"]) / n,
         "ritual": sum(1 for s, _ in S if s["ritual"]) / n,
         "mat": sum(1 for s, _ in S if "M" in s["components"]) / n,
         "gp": sum(1 for s, _ in S if s["material"] and "gp" in s["material"]),
         "cls": st.mean(len(s["classes"]) for s, _ in S),
         "scal": sum(1 for s, _ in S if s["at_higher_levels"]) / n,
         "long": sum(1 for s, _ in S if s["duration"] in ("1 hour", "8 hours", "24 hours", "10 days", "Until dispelled")) / n,
        }
    return out

def level_stats(sp, floors):
    """Mean, max, and 90th percentile of net cost by level with the given floors, and effect totals."""
    old = dict(P.FLOORS)
    P.FLOORS.clear(); P.FLOORS.update(floors)
    try:
        net = {l: [] for l in LEVELS}; eff = {l: [] for l in LEVELS}
        for s, spec in sp.values():
            rows, t = P.score(spec, enforce=False)
            net[spec["level"]].append(t)
            eff[spec["level"]].append(sum(r[2] for r in rows if r[0] in ("Effect", "Floor")))
    finally:
        P.FLOORS.clear(); P.FLOORS.update(old)
    return net, eff

def p90(v):
    v = sorted(v)
    return v[int(0.9 * (len(v) - 1))]

def write(sp):
    L = []
    A = L.append
    cal = json.load(open(P.CAL_PATH))
    B = P.BUDGETS
    net, eff = level_stats(sp, dict(P.FLOORS))
    net0, eff0 = level_stats(sp, {1: P.floor(1)})       # only the level 1 floor you asked for
    netn, effn = level_stats(sp, {})                       # no floors at all
    m = {l: st.mean(v) for l, v in net.items()}
    m0 = {l: st.mean(v) for l, v in net0.items()}
    mn = {l: st.mean(v) for l, v in netn.items()}
    mx = {l: max(v) for l, v in net.items()}
    mx0 = {l: max(v) for l, v in net0.items()}
    f = cal["fit"]
    A("# Spell Scaling Analysis\n")
    A("How much more should a spell be allowed to do as its level goes up? This study uses the 24 cantrips, 49 level 1 spells, 53 level 2 spells, and 43 level 3 spells in this repo, priced with the point-buy system in `docs/spell-point-buy.md`.\n")
    A("> **Verification status.** The spell files were written from memory of the SRD 5.1 lists and are not checked against the books. The 2014 DMG damage table used as a cross-check was also recalled from memory (UNVERIFIED). The level 2 and level 3 lists may miss a few SRD spells or include one that is not in the SRD. The conclusions describe this data set and my pricing, not official design intent. Only levels 0 to 3 are measured. Anything for level 4 and up is an extrapolation.\n")
    A("## Short answer\n")
    A(f"- **Budgets:** cantrip {B[0]}, level 1 {B[1]}, level 2 {B[2]}, level 3 {B[3]}.")
    A(f"- **Level 3 was a held-out test.** Prices were fitted to cantrips, level 1, and level 2 only. Pricing the 43 level 3 spells with those prices, unchanged, the strongest one costs {mx[3]:.0f}. That sets the level 3 budget at {B[3]}.")
    A(f"- **The earlier placeholder was wrong at level 3.** The previous version of this study proposed `50 x (level + 1)`, which gives 200. The measured strongest level 3 spell costs {mx[3]:.0f}, so 200 would leave {sum(1 for v in net[3] if v > 200)} of the 43 level 3 spells over budget. The recalled DMG damage table predicts {100 * DMG_TABLE[3] / DMG_TABLE[1]:.0f} for level 3 (27.5 over 11 average damage), and the measured budget matches it.")
    A(f"- **Shape:** budgets of {B[1]}, {B[2]}, {B[3]} for levels 1, 2, 3 grow by {B[2] - B[1]}, then {B[3] - B[2]}. The rise picks up speed, like the DMG table's steps of 5.5 and 11. It is not a doubling each level and not a straight line. Three points cannot prove a curve.")
    A(f"- **Much of each level's cost still comes from the effect floors, not from the spells.** With no floors at all, the mean costs are {mn[1]:.0f}, {mn[2]:.0f}, and {mn[3]:.0f} for levels 1, 2, and 3. The floors lift them to {m[1]:.0f}, {m[2]:.0f}, and {m[3]:.0f}. The budgets follow the strongest spells, which sit well above any floor, so they barely move. The means and the weak end of each level are floor-driven. Section 2 shows the numbers.")
    A(f"- **Cantrips are a separate track.** A cantrip budget of {B[0]} is one quarter of level 1. Cantrips have no slot cost, so they are priced as a discount tier, not as level 0 of the same line.")
    A("- **Budget alone is not safe.** Pricing is convex for damage, healing, and AC. Extra targets cost a share of what each target pays. Every scalable item has a hard cap equal to the strongest value seen at that level. The stress test shows what that buys.\n")
    A("## 1. What the spells look like at each level\n")
    R = raw_metrics(sp)
    def row(label, fn):
        return [label] + [fn(R[l]) for l in LEVELS]
    A(tbl(["Measure"] + [NAMES[l] + "s" if l == 0 else NAMES[l] for l in LEVELS], [
        row("Spells", lambda r: r["n"]),
        row("Spells that deal damage", lambda r: r["dmg_n"]),
        row("Mean damage on the first hit (avg)", lambda r: n1(round(r["dmg_mean"], 1))),
        row("Max damage on the first hit (avg)", lambda r: n1(r["dmg_max"])),
        row("Mean damage including repeats (avg)", lambda r: n1(round(r["dmgt_mean"], 1))),
        row("Max damage including repeats (avg)", lambda r: n1(r["dmgt_max"])),
        row("Spells that heal", lambda r: r["heal_n"]),
        row("Max healing on one target (avg)", lambda r: n1(r["heal_max"])),
        row("Spells with a strong condition", lambda r: r["ctl_n"]),
        row("Max targets", lambda r: n1(r["tg_max"])),
        row("Share that need concentration", lambda r: f"{r['conc'] * 100:.0f}%"),
        row("Share lasting an hour or more", lambda r: f"{r['long'] * 100:.0f}%"),
        row("Share that are rituals", lambda r: f"{r['ritual'] * 100:.0f}%"),
        row("Share with a material component", lambda r: f"{r['mat'] * 100:.0f}%"),
        row("Materials with a gold cost", lambda r: r["gp"]),
        row("Mean classes per spell", lambda r: n1(round(r["cls"], 1))),
        row("Share with an at-higher-levels clause", lambda r: f"{r['scal'] * 100:.0f}%")]))
    A("\nWhat stands out:\n")
    A(f"- **First-hit damage barely moves from level 1 to level 2, then jumps at level 3.** The mean first hit is {n1(round(R[1]['dmg_mean'], 1))}, {n1(round(R[2]['dmg_mean'], 1))}, and {n1(round(R[3]['dmg_mean'], 1))} at levels 1, 2, and 3. The best first hit is {n1(R[1]['dmg_max'])}, {n1(R[2]['dmg_max'])}, and {n1(R[3]['dmg_max'])}. Level 3's top figures are Fireball and Lightning Bolt (8d6 each, area, save for half). The DMG table shows the same pattern: a small step from level 1 to 2, a bigger one to 3.")
    A(f"- **Level 2 gets ahead by repeating and lasting, level 3 by hitting harder and wider.** Damage including repeats averages {n1(round(R[1]['dmgt_mean'], 1))}, {n1(round(R[2]['dmgt_mean'], 1))}, and {n1(round(R[3]['dmgt_mean'], 1))}.")
    A(f"- **Cantrip damage is about 40% of level 1.** Mean first hit {n1(round(R[0]['dmg_mean'], 1))} against {n1(round(R[1]['dmg_mean'], 1))}.")
    A(f"- **Concentration and long duration keep rising.** Concentration: {R[0]['conc'] * 100:.0f}%, {R[1]['conc'] * 100:.0f}%, {R[2]['conc'] * 100:.0f}%, {R[3]['conc'] * 100:.0f}%.")
    A(f"- **Gold-cost materials start at level 1 and grow:** {R[0]['gp']}, {R[1]['gp']}, {R[2]['gp']}, {R[3]['gp']} spells.\n")
    A("## 2. Where the growth comes from\n")
    D = dims_by_level(sp)
    order = ["dmg", "heal", "buff", "cond", "util", "area", "floor top-up", "duration", "range", "casting", "refunds", "other"]
    names = {"dmg": "Damage", "heal": "Healing", "buff": "Buffs", "cond": "Conditions", "util": "Utility", "area": "Targets and area", "floor top-up": "Effect floor top-up", "duration": "Duration", "range": "Range", "casting": "Casting time", "refunds": "Refunds (components, limits, concentration, class lists)", "other": "Ritual and scaling charges"}
    rows = []
    for k in order:
        a, b, c, d = (D[l][k] for l in LEVELS)
        rows.append([names[k], f"{a:.1f}", f"{b:.1f}", f"{c:.1f}", f"{d:.1f}", f"{d / b:.2f}" if abs(b) > 0.5 else "n/a"])
    tot = {l: sum(D[l].values()) for l in LEVELS}
    rows.append(["**Net cost**"] + [f"**{tot[l]:.1f}**" for l in LEVELS] + [f"**{tot[3] / tot[1]:.2f}**"])
    A("Mean points per spell, by dimension, using the calibrated prices.\n")
    A(tbl(["Dimension", "Cantrip", "Level 1", "Level 2", "Level 3", "L3 / L1"], rows))
    A("\nRead the last column as the growth in each dimension from level 1 to level 3. Anything near the net ratio grows with the budget. Anything well above it is where higher levels put their extra power. Anything below it is a dimension that should not be allowed to grow as fast.\n")
    A("### How much of each level's cost is the floor?\n")
    A(f"An effect floor adds points to any spell whose effects fall short of it. The level 1 floor of {P.floor(1)} is yours. The level 2 floor ({P.floor(2)}) and level 3 floor ({P.floor(3)}) are mine: each equals the previous level's budget. This table recomputes the means with the floors switched off, using the same prices.\n")
    rows = []
    for label, d in (("No floors at all", mn), (f"Level 1 floor only ({P.floor(1)})", m0), (f"All floors, as adopted ({P.floor(1)}, {P.floor(2)}, {P.floor(3)})", m)):
        rows.append([label] + [f"{d[l]:.1f}" for l in LEVELS] + [f"{d[2] / d[1]:.2f}", f"{d[3] / d[1]:.2f}"])
    A(tbl(["Floors applied", "Cantrip mean", "Level 1 mean", "Level 2 mean", "Level 3 mean", "L2 / L1", "L3 / L1"], rows))
    mxn = {l: max(v) for l, v in netn.items()}
    A(f"\nThe strongest spell at each level, with no floors, costs {mxn[1]:.0f}, {mxn[2]:.0f}, and {mxn[3]:.0f}. With the floors it is {mx[1]:.0f}, {mx[2]:.0f}, and {mx[3]:.0f}. The budgets follow the strongest spell, so the floors barely move them. The floors do set where the weak end of each level sits: the cheapest level 3 spell costs {min(net[3]):.0f} with floors and {min(netn[3]):.0f} without.\n")
    A(f"Two readings of the no-floor means ({mn[1]:.0f}, {mn[2]:.0f}, {mn[3]:.0f}). Either higher-level spells really are only a little stronger on average than lower ones, with a few standouts, or my level 2 and 3 item prices (set by analogy to level 1 items) are too low. I cannot tell which from this data. I kept the floors because they make each level's weak end cost at least the level below's budget. You asked for that clearance between cantrips and level 1, and I extended the idea upward.\n")
    A("## 3. Calibrated prices\n")
    A(f"Each category of price is multiplied by a factor chosen so that cantrips and level 1 spells cluster near their budgets (targets of 20 and 95 against {B[0]} and {B[1]}), with level 2 fitted for spread only. A pull toward the original hand-set prices stops any factor drifting far. Level 3 does not enter the fit.\n")
    mult = cal["mult"]
    names2 = {"dmg": "Damage and hit delivery", "heal": "Healing", "buff": "Buffs", "cond": "Conditions", "util": "Utility", "area": "Area and targets", "range": "Range", "cast": "Casting time", "dur": "Duration", "comp": "Component refunds", "limit": "Limit refunds", "conc": "Concentration refund", "extra": "Ritual and scaling charges", "avail": "Class list availability"}
    A(tbl(["Category", "Multiplier"], [[names2[c], f"{mult[c]:.2f}"] for c in P.CATS]))
    A(f"\nWith these prices the mean net cost is {f['mean_after']['0']}, {f['mean_after']['1']}, {f['mean_after']['2']}, and {f['mean_after']['3']} for cantrips and levels 1, 2, and 3, with standard deviations of {f['sd_after']['0']}, {f['sd_after']['1']}, {f['sd_after']['2']}, and {f['sd_after']['3']}.\n")
    top = sorted(((P.score(spec)[1], sn["name"]) for sn, spec in sp.values() if spec["level"] == 1), reverse=True)[:3]
    A(f"**What calibration cannot do.** Spells of one level are not equally strong, and my build for each spell is a judgment. The fit narrows the spread. It does not remove it. The level 1 mean is {m[1]:.0f} and the median {st.median(net[1]):.0f}, not 100, because the budget is a ceiling set by the strongest spells ({', '.join(f'{n} {t:.0f}' for t, n in top)}) and utility spells sit well under it.\n")
    A("## 4. Which curve?\n")
    A(f"The budgets are set by one rule: the smallest multiple of 25 that covers the strongest spell at that level, with level 1 anchored at 100 and cantrips at 25. That gives {B[1]}, {B[2]}, and {B[3]}. A rule based on the strongest spell is sensitive to one outlier, so here is the same comparison using the 90th percentile of net cost instead of the maximum:\n")
    p = {l: p90(net[l]) for l in LEVELS}
    A(tbl(["Measure", "Level 1", "Level 2", "Level 3", "L2 / L1", "L3 / L1"], [
        ["Strongest spell", f"{mx[1]:.0f}", f"{mx[2]:.0f}", f"{mx[3]:.0f}", f"{mx[2] / mx[1]:.2f}", f"{mx[3] / mx[1]:.2f}"],
        ["90th percentile", f"{p[1]:.0f}", f"{p[2]:.0f}", f"{p[3]:.0f}", f"{p[2] / p[1]:.2f}", f"{p[3] / p[1]:.2f}"],
        ["Mean", f"{m[1]:.0f}", f"{m[2]:.0f}", f"{m[3]:.0f}", f"{m[2] / m[1]:.2f}", f"{m[3] / m[1]:.2f}"],
        ["Recalled DMG damage table", n1(DMG_TABLE[1]), n1(DMG_TABLE[2]), n1(DMG_TABLE[3]), f"{DMG_TABLE[2] / DMG_TABLE[1]:.2f}", f"{DMG_TABLE[3] / DMG_TABLE[1]:.2f}"],
        ["Budget chosen", B[1], B[2], B[3], f"{B[2] / B[1]:.2f}", f"{B[3] / B[1]:.2f}"]]))
    A(f"\nEvery measure rises with level and the ratio to level 1 grows faster each level, with the budget at {B[3] / B[1]:.1f} times level 1 for level 3. The percentile and mean rows are lower in absolute terms because they include many utility spells. I chose the strongest-spell rule because the budget is a ceiling, not a typical cost.\n")
    xs = list(range(1, 10)); ys = DMG_TABLE[1:]
    a, b, r2 = linfit(xs, ys)
    la, lb, lr2 = linfit(xs, [math.log(y) for y in ys])
    pa, pb_, pr2 = linfit([math.log(x) for x in xs], [math.log(y) for y in ys])
    A("Average damage by level, from the table (UNVERIFIED):\n")
    A(tbl(["Level"] + [str(l) for l in range(0, 10)], [["Avg damage"] + [n1(x) for x in DMG_TABLE], ["Share of level 1"] + [f"{x / DMG_TABLE[1]:.2f}" for x in DMG_TABLE]]))
    A("\nFit of that table over levels 1 to 9:\n")
    A(tbl(["Model", "Form", "R squared"], [
        ["Linear", f"damage = {a:.1f} + {b:.1f} x level", f"{r2:.3f}"],
        ["Geometric", f"damage = {math.exp(la):.1f} x {math.exp(lb):.2f}^level", f"{lr2:.3f}"],
        ["Power", f"damage = {math.exp(pa):.1f} x level^{pb_:.2f}", f"{pr2:.3f}"]]))
    best = max((("linear", r2), ("geometric", lr2), ("power", pr2)), key=lambda x: x[1])
    A(f"\nThe best fit over levels 1 to 9 is **{best[0]}**. Over levels 1 to 3 alone the table is not a straight line: it steps 5.5, then 11.\n")
    A("Budget curves for each hypothesis, with level 1 fixed at 100:\n")
    rows = []
    for lvl in range(1, 10):
        rows.append([lvl, f"{100 * DMG_TABLE[lvl] / DMG_TABLE[1]:.0f}", f"{100 * (a + b * lvl) / (a + b):.0f}", f"{100 * 1.5 ** (lvl - 1):.0f}", f"{50 * (lvl + 1)}", f"{100 * lvl}",
                     {1: B[1], 2: B[2], 3: B[3]}.get(lvl, "not measured")])
    A(tbl(["Level", "Follow the DMG table", "Linear fit of the table", "Geometric x1.5", "50 x (level + 1)", "Double each level", "Measured budget"], rows))
    A(f"\n**Recommendation.** Use **{B[1]}, {B[2]}, and {B[3]}** for levels 1, 2, and 3. For levels 4 to 9, the first column (follow the DMG table) is the best provisional guide, because it matched all three measured budgets: 100, 150, 250. That gives 300, 400, 500, 550, 600, and 700 for levels 4 to 9. It rests on a table I recalled from memory and on no spell data above level 3, so treat it as a placeholder until level 4 spells are added.\n")
    A("The cantrip budget does not sit on any of these lines. Cantrips can be cast without limit, so they get a quarter of level 1. Do not extend that to other levels.\n")
    A("## 5. Floors, ceilings, and clearances\n")
    A("A floor is the lowest effect total a spell of that level may have. A ceiling is the highest. Effect total means damage, healing, buffs, conditions, utility, and area. Range, duration, and refunds are not counted. Cantrips are capped just under the level 1 floor. From level 1 up, effects cannot exceed the level's budget.\n")
    rows = []
    for lvl in LEVELS:
        rows.append([NAMES[lvl], B[lvl], P.floor(lvl) or "none", P.ceiling(lvl), f"{min(eff[lvl]):.0f}", f"{max(eff[lvl]):.0f}", f"{min(net[lvl]):.0f}", f"{max(net[lvl]):.0f}"])
    A(tbl(["Level", "Budget", "Effect floor", "Effect ceiling", "Lowest effect total", "Highest effect total", "Lowest net", "Highest net"], rows))
    A(f"\nThe cantrip to level 1 gap is the one you asked for: level 1 effects start at {P.floor(1)}, cantrip effects stop at {P.CANTRIP_CEIL}. From level 2 up each floor is the previous budget ({P.floor(2)}, {P.floor(3)}) and each ceiling is that level's own budget. Adjacent levels therefore meet exactly at a budget with no overlap: level 1 effects top out at {P.ceiling(1)} and level 2 effects start at {P.floor(2)}. Item tiers and magnitude caps add a second layer of separation, which the stress test checks below.\n")
    A("## 6. Stress test: can a player inflate an existing spell?\n")
    r = stress.compute(sp)
    A("For every spell the test raises one lever until the spell stops being legal. Lever one raises the main damage, healing, or temporary HP line. Lever two raises every such line together. Lever three adds targets. Lever four re-files the spell one level lower. Each is run with only the budget enforced and with every rule enforced.\n")
    rows = []
    for lvl in LEVELS:
        mg = [x for x in r["mag"] if x[1] == lvl]
        rb = [x[4] / x[3] for x in mg]; rr = [x[5] / x[3] for x in mg]
        al = [x for x in r["all"] if x[1] == lvl]
        tg = [x for x in r["tgt"] if x[1] == lvl]
        tb = [x[3] - x[2] for x in tg]; tr = [x[4] - x[2] for x in tg]
        rows.append([NAMES[lvl], f"x{st.median(rb):.2f} / x{max(rb):.2f}", f"x{st.median(rr):.2f} / x{max(rr):.2f}",
                     f"x{st.median(x[2] for x in al):.2f} / x{max(x[2] for x in al):.2f}", f"x{st.median(x[3] for x in al):.2f} / x{max(x[3] for x in al):.2f}",
                     f"{max(tb)}", f"{max(tr)}"])
    A(tbl(["Level", "One magnitude, budget only (median / worst)", "One magnitude, all rules", "All magnitudes together, budget only", "All magnitudes together, all rules", "Max extra targets, budget only", "Max extra targets, all rules"], rows))
    wall = [x[3] for x in r["all"]]
    A(f"\n\"All magnitudes together\" raises every damage, healing, and temporary HP line of a spell by the same factor, which is the realistic way to try to make a spell much stronger. With every rule on, the median spell can grow about {(st.median(wall) - 1) * 100:.0f}% and the worst about {(max(wall) - 1) * 100:.0f}%. With only the budget, the worst grew {max(x[2] for x in r['all']):.1f} times.\n")
    worst = sorted(((x[5] / x[3], x) for x in r["mag"]), reverse=True)[:5]
    A("Largest single-line growth under all rules:\n")
    A(tbl(["Spell", "Level", "Lever", "Original", "Most the rules allow"], [[x[0], x[1], x[2], n1(x[3]), n1(x[5])] for g, x in worst]))
    A("\nThe rules cut the worst case but do not remove it. A spell with a small number (Vicious Mockery's d4, Healing Word's d4 plus modifier) can still climb to the strongest value that exists at its level. That is the design: no spell can beat the top of its own level, even if it can get close.\n")
    hop = {lvl: Counter(x[2] for x in r["hop"] if x[1] == lvl) for lvl in (1, 2, 3)}
    A("Lever four re-files each spell one level lower and records which rule stops it:\n")
    kinds = ["effect tier", "magnitude cap", "control cap", "effect ceiling", "budget", "allowed"]
    A(tbl(["Filed as", "Spells"] + kinds, [[f"{NAMES[lvl]} spell as {'a cantrip' if lvl == 1 else NAMES[lvl - 1].lower()}", sum(hop[lvl].values())] + [hop[lvl].get(k, 0) for k in kinds] for lvl in (1, 2, 3)]))
    for lvl in (2, 3):
        allowed = [x[0] for x in r["hop"] if x[1] == lvl and x[2] == "allowed"]
        if allowed:
            A(f"\n**Weak spot at level {lvl}.** Under the current rules, {len(allowed)} level {lvl} spell{'s' if len(allowed) != 1 else ''} can be filed as level {lvl - 1}: {', '.join(allowed)}. Built only from items available one level down, {'each fits' if len(allowed) != 1 else 'it fits'} under that level's budget, so my model sees {'them' if len(allowed) != 1 else 'it'} as the lower level's strength. Either {'they are' if len(allowed) != 1 else 'it is'} underpriced here, or WotC placed {'them' if len(allowed) != 1 else 'it'} higher for reasons (duration, range, flexibility) that my items do not capture. I did not patch this, because forcing an extra item into {'each' if len(allowed) != 1 else 'it'} would be a guess.")
    A("\n## 7. Rules that follow from the study\n")
    A(tbl(["Rule", "Value"], [
        ["Budgets", f"cantrip {B[0]}, level 1 {B[1]}, level 2 {B[2]}, level 3 {B[3]}"],
        ["Effect floor", f"level 1: {P.floor(1)}. level 2: {P.floor(2)}. level 3: {P.floor(3)}"],
        ["Effect ceiling", f"cantrip: {P.CANTRIP_CEIL}. level 1 and up: the budget"],
        ["Items by level", "Each item has a minimum level. A spell cannot use an item above its level."],
        ["Magnitude caps", "Damage, healing, temporary HP, targets, AC, and similar items cannot exceed the highest value seen at that level, carried up from lower levels. Damage has separate caps for touch spells, area spells, split-target spells, and cantrips that add a rider. Spells cast as a bonus action or reaction have lower caps for damage and healing."],
        ["Extra targets", "Each extra target costs a share of the spell's per-target lines (damage 70%, control 60%, buffs 50%, healing 25%) and counts toward the control cap."],
        ["Weak effects pay less for duration", f"A cantrip with effects under {P.DURATION_REF} points pays between half and all of the duration price."],
        ["Area price", "Follows the square root of the footprint."],
        ["Control cap", f"Strong conditions together cost at most {cal['control_cap']['1']} at level 1, {cal['control_cap']['2']} at level 2, and {cal['control_cap']['3']} at level 3. Cantrips have none."],
        ["Flat items and duplicates", "Taken once. Each item and limit is listed once."],
        ["Convex price", f"Price grows with magnitude to the power {1 + P.EXP:.1f}, so doubling damage more than doubles the price."],
        ["Limit refunds", f"Capped at {int(P.LIMIT_CAP * 100)}% of the effect cost."],
        ["Upcasting", f"Each increase per slot level costs {int(P.UPCAST_SHARE * 100)}% of buying it outright. Targets rise by at most {P.UPCAST_TARGETS} per slot level. A damage or healing increase cannot exceed the base amount per slot level."]]))
    A("\n## 8. Limits of this study\n")
    A("- Four levels is too few to pick a curve from spell data alone. The DMG table agrees with the measured budgets, but only if my recollection of it is right.")
    A("- Every spell's build, and the price of every level 2 and level 3 item, is my judgment. The calibration tunes category multipliers, not individual items. A mispriced item stays mispriced.")
    A("- Level 3 was held out of the price fit, so its budget is a measurement. It is also the least checked: the 43 level 3 builds were written once and have had no second pass.")
    A("- The budgets follow the strongest spell at each level. One mispriced standout moves a budget by a full step of 25.")
    A("- The level 2 and 3 lists and spell text come from memory. Some SRD spells may be missing.")
    A("- Caps come from the spells I built, so a mistake in one build moves a cap.")
    A("- Upcasting is priced from the first listed increase only. Spells that scale in other ways pay a flat charge.")
    A("- Concentration, saves, and monster hit points are not modeled. Damage is an average roll.")
    return L
