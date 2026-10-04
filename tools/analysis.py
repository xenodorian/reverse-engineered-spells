"""Scaling analysis across cantrips, level 1, and level 2. Produces docs/spell-scaling-analysis.md."""
import json, math, statistics as st
import pricing as P
import stress

# Average damage by spell level from the 2014 DMG "Spell Damage" table, level 0 to 9.
# UNVERIFIED: recalled from memory, not checked against the book. Only used as a cross-check.
DMG_TABLE = [5.5, 11, 16.5, 27.5, 33, 44, 55, 60.5, 66, 77]

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
    """Mean contributions by dimension for one spell, in points."""
    d = {c: 0.0 for c in ("dmg", "heal", "buff", "cond", "util", "area")}
    for item, q in spec["lines"]:
        if item in P.ITEMS:
            d[P.ITEMS[item][4]] += P.price(item, q)
    eff = sum(d.values())
    rows, t = P.score(spec, enforce=False)
    top = sum(r[2] for r in rows if r[0] == "Floor")
    d["floor top-up"] = top
    d["duration"] = P.DURATION[spec["duration"]] * P.MULT["dur"]
    d["range"] = P.RANGE[spec["range"].split(" (")[0]] * P.MULT["range"]
    d["casting"] = P.lookup(P.CASTING, spec["casting_time"]) * P.MULT["cast"]
    d["refunds"] = sum(r[2] for r in rows if r[0] in ("Refund", "Limit", "Cap", "Availability"))
    d["other"] = t - sum(v for k, v in d.items() if k != "other") - 0  # ritual and scaling
    return d, eff + top, t

def dims_by_level(sp):
    res = {}
    for lvl in (0, 1, 2):
        acc = {}
        specs = [spec for s, spec in sp.values() if spec["level"] == lvl]
        for spec in specs:
            d, e, t = group_sums(spec)
            for k, v in d.items():
                acc[k] = acc.get(k, 0) + v
        res[lvl] = {k: v / len(specs) for k, v in acc.items()}
    return res

def raw_metrics(sp):
    out = {}
    for lvl in (0, 1, 2):
        S = [(s, spec) for s, spec in sp.values() if spec["level"] == lvl]
        n = len(S)
        def q(spec, items):
            return sum(v for i, v in spec["lines"] if i in items)
        dm = [q(sp_, ("dmg", "c_dmg")) for s, sp_ in S if q(sp_, ("dmg", "c_dmg"))]
        dmt = [q(sp_, ("dmg", "c_dmg", "dmg_recurring", "zone_damage")) for s, sp_ in S if q(sp_, ("dmg", "c_dmg"))]
        hl = [q(sp_, ("heal",)) for s, sp_ in S if q(sp_, ("heal",))]
        ctl = [sum(P.price(i, v) for i, v in sp_["lines"] if i in P.CONTROL) for s, sp_ in S]
        ctl = [c for c in ctl if c]
        tg = [1 + q(sp_, ("target_extra",)) for s, sp_ in S]
        out[lvl] = {
         "n": n,
         "dmg_n": len(dm), "dmg_mean": st.mean(dm) if dm else 0, "dmg_max": max(dm) if dm else 0,
         "dmgt_mean": st.mean(dmt) if dmt else 0, "dmgt_max": max(dmt) if dmt else 0,
         "heal_n": len(hl), "heal_mean": st.mean(hl) if hl else 0, "heal_max": max(hl) if hl else 0,
         "ctl_n": len(ctl), "ctl_mean": st.mean(ctl) if ctl else 0, "ctl_max": max(ctl) if ctl else 0,
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

def mean_nets(sp, l1f, l2f):
    old = (P.L1_FLOOR, P.L2_FLOOR)
    P.L1_FLOOR, P.L2_FLOOR = l1f, l2f
    try:
        n = {0: [], 1: [], 2: []}
        for s, spec in sp.values():
            n[spec["level"]].append(P.score(spec, enforce=False)[1])
    finally:
        P.L1_FLOOR, P.L2_FLOOR = old
    return {l: st.mean(v) for l, v in n.items()}

def write(sp, base_mult=None):
    L = []
    A = L.append
    nets = {0: [], 1: [], 2: []}; effs = {0: [], 1: [], 2: []}
    for k, (s, spec) in sp.items():
        rows, t = P.score(spec)
        nets[spec["level"]].append(t)
        effs[spec["level"]].append(sum(r[2] for r in rows if r[0] in ("Effect", "Floor")))
    cal = json.load(open(P.CAL_PATH))
    m = {l: st.mean(v) for l, v in nets.items()}
    B = P.BUDGETS
    A("# Spell Scaling Analysis\n")
    A("How much more should a spell be allowed to do as its level goes up? This study uses the 24 cantrips, 49 level 1 spells, and 53 level 2 spells in this repo, priced with the point-buy system in `docs/spell-point-buy.md`.\n")
    A("> **Verification status.** The spell files were written from memory of the SRD 5.1 lists and are not checked against the books. The 2014 DMG damage table used as a cross-check was also recalled from memory (UNVERIFIED). The level 2 list may miss a few SRD spells or include one that is not in the SRD. The conclusions describe this data set and my pricing, not official design intent. Only levels 0 to 2 are measured. Anything for level 3 and up is an extrapolation.\n")
    A("## Short answer\n")
    A(f"- **Budgets:** cantrip {B[0]}, level 1 {B[1]}, level 2 {B[2]}.")
    sens = {name: mean_nets(sp, a, b) for name, a, b in (("none", 0, 0), ("l1", P.L1_FLOOR, 0), ("both", P.L1_FLOOR, P.L2_FLOOR))}
    A(f"- **Growth is neither a doubling nor a flat step.** After calibration, level 2 spells cost {m[2] / m[1]:.2f} times what level 1 spells cost on average. The level 2 budget is that ratio applied to 100 and rounded to the nearest 25, which gives {B[2]}, not 200.")
    A(f"- **Much of that ratio comes from the effect floor, not from the spells.** With no floors, level 2 costs only {sens['none'][2] / sens['none'][1]:.2f} times level 1 under my prices. The floors (level 1 at {P.L1_FLOOR}, level 2 at {P.L2_FLOOR}) lift it to {sens['both'][2] / sens['both'][1]:.2f}. So {B[2]} rests on the floor design and on the DMG damage table, not on the spell data alone. Section 2 shows the numbers.")
    A(f"- **The recalled DMG damage table independently gives {DMG_TABLE[2] / DMG_TABLE[1]:.2f}** for level 2 over level 1 average damage. That agrees with {B[2] / B[1]:.2f}, but it is one data point from memory and covers damage only.")
    A("- **Shape:** from level 1 on, the evidence fits a straight line in spell level (about +50 points per level at the start), not an exponential. The data cannot prove that past level 2.")
    A(f"- **Cantrips are a separate track.** A cantrip budget of {B[0]} is one quarter of level 1. Cantrips have no slot cost, so they are priced as a discount tier, not as level 0 of the same line.")
    A("- **Budget alone is not safe.** Pricing is convex for damage, healing, and targets, and every scalable item has a hard cap equal to the strongest value seen at that level. Details are in the stress test below.\n")
    A("## 1. What the spells look like at each level\n")
    R = raw_metrics(sp)
    def row(label, f):
        return [label] + [f(R[l]) for l in (0, 1, 2)]
    A(tbl(["Measure", "Cantrips", "Level 1", "Level 2"], [
        row("Spells", lambda r: r["n"]),
        row("Spells that deal damage", lambda r: r["dmg_n"]),
        row("Mean damage on the first hit (avg)", lambda r: n1(round(r["dmg_mean"], 1))),
        row("Max damage on the first hit (avg)", lambda r: n1(r["dmg_max"])),
        row("Mean damage including repeats (avg)", lambda r: n1(round(r["dmgt_mean"], 1))),
        row("Max damage including repeats (avg)", lambda r: n1(r["dmgt_max"])),
        row("Spells that heal", lambda r: r["heal_n"]),
        row("Max healing on one target (avg)", lambda r: n1(r["heal_max"])),
        row("Spells with a strong condition", lambda r: r["ctl_n"]),
        row("Mean targets (1 + extras)", lambda r: n1(round(r["tg_mean"], 1))),
        row("Max targets", lambda r: n1(r["tg_max"])),
        row("Share that need concentration", lambda r: f"{r['conc'] * 100:.0f}%"),
        row("Share lasting an hour or more", lambda r: f"{r['long'] * 100:.0f}%"),
        row("Share that are rituals", lambda r: f"{r['ritual'] * 100:.0f}%"),
        row("Share with a material component", lambda r: f"{r['mat'] * 100:.0f}%"),
        row("Materials with a gold cost", lambda r: r["gp"]),
        row("Mean classes per spell", lambda r: n1(round(r["cls"], 1))),
        row("Share with an at-higher-levels clause", lambda r: f"{r['scal'] * 100:.0f}%")]))
    A("\nWhat stands out:\n")
    A(f"- **Average first-hit damage barely moves from level 1 to level 2.** It is {n1(round(R[1]['dmg_mean'], 1))} at level 1 and {n1(round(R[2]['dmg_mean'], 1))} at level 2. The best first hit rises from {n1(R[1]['dmg_max'])} to {n1(R[2]['dmg_max'])}, and that level 2 figure is three Scorching Ray attacks added together. Damage including repeats rises from {n1(round(R[1]['dmgt_mean'], 1))} to {n1(round(R[2]['dmgt_mean'], 1))}. Level 2 spells get ahead by repeating (Flaming Sphere, Moonbeam, Heat Metal) and by lasting longer, not by hitting harder once.")
    A(f"- **Cantrip damage is about 40% of level 1.** Mean first hit {n1(round(R[0]['dmg_mean'], 1))} against {n1(round(R[1]['dmg_mean'], 1))}. The best cantrip hit is {n1(R[0]['dmg_max'])}, the best level 1 hit {n1(R[1]['dmg_max'])}.")
    A(f"- **Concentration and long duration rise with level.** {R[0]['conc'] * 100:.0f}% of cantrips need concentration, against {R[1]['conc'] * 100:.0f}% at level 1 and {R[2]['conc'] * 100:.0f}% at level 2.")
    A(f"- **Gold-cost materials start at level 1 and become more common.** {R[0]['gp']} cantrips, {R[1]['gp']} level 1 spells, {R[2]['gp']} level 2 spells.\n")
    A("## 2. Where the growth comes from\n")
    D = dims_by_level(sp)
    order = ["dmg", "heal", "buff", "cond", "util", "area", "floor top-up", "duration", "range", "casting", "refunds", "other"]
    names = {"dmg": "Damage", "heal": "Healing", "buff": "Buffs", "cond": "Conditions", "util": "Utility", "area": "Targets and area", "floor top-up": "Effect floor top-up", "duration": "Duration", "range": "Range", "casting": "Casting time", "refunds": "Refunds (components, limits, concentration, class lists)", "other": "Ritual and scaling charges"}
    rows = []
    for k in order:
        a, b, c = D[0][k], D[1][k], D[2][k]
        rows.append([names[k], f"{a:.1f}", f"{b:.1f}", f"{c:.1f}", f"{c / b:.2f}" if abs(b) > 0.5 else "n/a"])
    tot = {l: sum(D[l].values()) for l in (0, 1, 2)}
    rows.append(["**Net cost**", f"**{tot[0]:.1f}**", f"**{tot[1]:.1f}**", f"**{tot[2]:.1f}**", f"**{tot[2] / tot[1]:.2f}**"])
    A("Mean points per spell, by dimension, using the calibrated prices.\n")
    A(tbl(["Dimension", "Cantrip", "Level 1", "Level 2", "L2 / L1"], rows))
    A("\nRead the last column as the growth in each dimension. Anything near the net ratio grows with the budget. Anything well above it is where level 2 puts its extra power. Anything below it is a dimension that should not be allowed to grow as fast.\n")
    A("### How much of the level 2 premium is the floor?\n")
    A("The effect floor adds points to any spell whose effects fall short of it. Level 2 has far more spells under its floor, so the floor drives a large share of the level 2 cost. This table recomputes mean net cost with the floors switched off, using the same calibrated prices.\n")
    rows = []
    for label, key in (("No floors", "none"), (f"Level 1 floor only ({P.L1_FLOOR})", "l1"), (f"Both floors, as adopted ({P.L1_FLOOR} and {P.L2_FLOOR})", "both")):
        v = sens[key]
        rows.append([label, f"{v[0]:.1f}", f"{v[1]:.1f}", f"{v[2]:.1f}", f"{v[1] / v[0]:.2f}", f"{v[2] / v[1]:.2f}"])
    A(tbl(["Floors applied", "Cantrip mean", "Level 1 mean", "Level 2 mean", "L1 / cantrip", "L2 / L1"], rows))
    A(f"\nWith no floors, level 2 spells cost about {sens['none'][2] / sens['none'][1]:.2f} times level 1 spells. Two readings fit. Either level 2 spells really are only a little stronger than level 1 spells in raw terms, or my level 2 item prices (set by analogy to level 1 items) are too low. I cannot tell which from this data. The floor rule makes the {B[2] / B[1]:.1f} ratio true by construction, and the DMG damage table agrees with {B[2] / B[1]:.1f}, so I kept it. If you would rather let the spells speak, set the level 2 floor lower and the budget falls toward {B[1] * sens['l1'][2] / sens['l1'][1]:.0f}.\n")
    A("## 3. Calibrated prices\n")
    A("Each category of price is multiplied by a factor chosen so that spells of each level cluster near their budget. Level 1 and cantrip targets are fixed (95 and 20 against budgets of 100 and 25). The level 2 target is free. A pull toward the original hand-set prices stops any factor drifting far.\n")
    mult = cal["mult"]
    names2 = {"dmg": "Damage and hit delivery", "heal": "Healing", "buff": "Buffs", "cond": "Conditions", "util": "Utility", "area": "Area and targets", "range": "Range", "cast": "Casting time", "dur": "Duration", "comp": "Component refunds", "limit": "Limit refunds", "conc": "Concentration refund", "extra": "Ritual and scaling charges", "avail": "Class list availability"}
    A(tbl(["Category", "Multiplier"], [[names2[c], f"{mult[c]:.2f}"] for c in P.CATS]))
    f = cal["fit"]
    A(f"\nBefore calibration the mean net cost was {f['mean_before']['0']} for cantrips, {f['mean_before']['1']} at level 1, and {f['mean_before']['2']} at level 2. After: {f['mean_after']['0']}, {f['mean_after']['1']}, and {f['mean_after']['2']}, with standard deviations of {f['sd_after']['0']}, {f['sd_after']['1']}, and {f['sd_after']['2']}.\n")
    top = sorted(((P.score(spec)[1], sn["name"]) for sn, spec in sp.values() if spec["level"] == 1), reverse=True)[:3]
    med1 = st.median(nets[1])
    A(f"**What calibration cannot do.** Spells of one level are not equally strong, and my build for each spell is a judgment. The fit narrows the spread. It does not remove it. The level 1 mean is {m[1]:.0f} and the median {med1:.0f}, not 100, because the budget is a ceiling set by the strongest spells ({', '.join(f'{n} {t:.0f}' for t, n in top)}) and utility spells sit well under it. Moving typical spells up to 100 would push the strongest ones over budget.\n")
    A("## 4. Which curve? Linear, geometric, or power\n")
    A(f"Two budget points are known: {B[1]} at level 1 and {B[2]} at level 2. Both a straight line (+{B[2] - B[1]} per level) and a geometric curve (x{B[2] / B[1]:.1f} per level) pass through them, so the spell data alone cannot choose. The recalled DMG damage table spans levels 1 to 9 and can.\n")
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
    A(f"\nThe best fit is **{best[0]}**. The linear and power fits are close, and both beat geometric for this table. A geometric curve would overshoot at high levels: a 1.5x step compounds to about 25x by level 9, while the table reaches 7x. (Treat the table as a rough check, since I recalled it and a miss in one entry would shift the fits.)\n")
    A("Budget curves for each hypothesis, with level 1 fixed at 100:\n")
    rows = []
    for lvl in range(1, 10):
        rows.append([lvl,
            f"{100 * DMG_TABLE[lvl] / DMG_TABLE[1]:.0f}",
            f"{100 * (a + b * lvl) / (a + b):.0f}",
            f"{100 * 1.5 ** (lvl - 1):.0f}",
            f"{50 * (lvl + 1)}",
            f"{100 * lvl}"])
    A(tbl(["Level", "Follow the DMG table", "Linear fit of the table", "Geometric x1.5", "50 x (level + 1)", "Double each level (100 x level)"], rows))
    A(f"\n**Recommendation.** Use **{B[1]} at level 1 and {B[2]} at level 2**. For level 3 and up, use `50 x (level + 1)` as a provisional placeholder, which gives 200 at level 3 and 250 at level 4. That line matches both known points, grows more slowly than the DMG table at level 3 (200 against 250), and never overshoots the way a geometric curve does. It has no spell data behind it yet. The recalled table suggests a jump at level 3 (damage 27.5 against 16.5), so revisit when level 3 spells are added.\n")
    A("The cantrip budget does not sit on this line. The line would give 50 at level 0. Cantrips use a half-line value (25) because they can be cast without limit. Do not extend that to other levels.\n")
    A("## 5. Clearances between levels\n")
    A(f"A clearance is the gap between the highest effect total allowed at one level and the lowest allowed at the next. Effect total means damage, healing, conditions, utility, and area only. Range, duration, and refunds are not counted.\n")
    rows = []
    for lvl, name in ((0, "Cantrip"), (1, "Level 1"), (2, "Level 2")):
        rows.append([name, B[lvl], P.floor(lvl) or "none", P.ceiling(lvl) if P.ceiling(lvl) < 10**8 else "none", f"{min(effs[lvl]):.0f}", f"{max(effs[lvl]):.0f}", f"{min(nets[lvl]):.0f}", f"{max(nets[lvl]):.0f}"])
    A(tbl(["Level", "Budget", "Effect floor", "Effect ceiling", "Lowest effect total", "Highest effect total", "Lowest net", "Highest net"], rows))
    A(f"\nThe cantrip to level 1 gap is the one you asked for: level 1 effects start at {P.L1_FLOOR}, cantrip effects stop at {P.CANTRIP_CEIL}. I applied the same idea one step up. A level 2 spell's effects must total at least {P.L2_FLOOR}, which is the whole level 1 budget, and level 1 effects stop at {P.L2_FLOOR - 1}. The floor top-up is why the cheapest level 2 spells ({', '.join(n for t, n in sorted((P.score(spec)[1], sn['name']) for sn, spec in sp.values() if spec['level'] == 2)[:2])}) still cost {min(nets[2]):.0f} or more.\n")
    A("## 6. Stress test: can a player inflate an existing spell?\n")
    r = stress.compute(sp)
    A("For every spell the test raises one lever until the spell stops being legal. Lever one raises damage, healing, or temporary HP. Lever two adds targets. Each is run with only the budget enforced and with every rule enforced.\n")
    rows = []
    for lvl, name in ((0, "Cantrip"), (1, "Level 1"), (2, "Level 2")):
        mg = [x for x in r["mag"] if x[1] == lvl]
        rb = [x[4] / x[3] for x in mg]; rr = [x[5] / x[3] for x in mg]
        tg = [x for x in r["tgt"] if x[1] == lvl]
        tb = [x[3] - x[2] for x in tg]; tr = [x[4] - x[2] for x in tg]
        rows.append([name, len(mg), f"x{st.median(rb):.2f}", f"x{max(rb):.2f}", f"x{st.median(rr):.2f}", f"x{max(rr):.2f}", f"{max(tb)}", f"{max(tr)}"])
    A(tbl(["Level", "Spells with a magnitude", "Median growth, budget only", "Worst, budget only", "Median growth, all rules", "Worst, all rules", "Max extra targets, budget only", "Max extra targets, all rules"], rows))
    worst = sorted(((x[5] / x[3], x) for x in r["mag"]), reverse=True)[:5]
    A("\nLargest growth under all rules:\n")
    A(tbl(["Spell", "Level", "Lever", "Original", "Most the rules allow"], [[x[0], x[1], x[2], n1(x[3]), n1(x[5])] for g, x in worst]))
    A("\nThe rules cut the worst case but do not remove it. A spell with a small number (Vicious Mockery's d4, Healing Word's d4 plus modifier) can still climb to the strongest value that exists at its level. That is the design: no spell can beat the top of its own level, even if it can get close. Raising the cap would mean accepting stronger spells at that level.\n")
    from collections import Counter
    hop = {1: Counter(x[2] for x in r["hop"] if x[1] == 1), 2: Counter(x[2] for x in r["hop"] if x[1] == 2)}
    A("Lever three re-files each spell one level lower and records which rule stops it:\n")
    kinds = ["effect tier", "magnitude cap", "control cap", "effect ceiling", "budget", "allowed"]
    A(tbl(["Filed as", "Spells"] + kinds, [["Level 1 spell as a cantrip", sum(hop[1].values())] + [hop[1].get(k, 0) for k in kinds], ["Level 2 spell as level 1", sum(hop[2].values())] + [hop[2].get(k, 0) for k in kinds]]))
    allowed = [x[0] for x in r["hop"] if x[1] == 2 and x[2] == "allowed"]
    A(f"\n**Weak spot.** {len(allowed)} level 2 spells pass as level 1 spells under the current rules: {', '.join(allowed)}. Each is built only from level 1 items and priced under 100 when the level 2 floor does not apply. That means my model sees them as level 1 strength spells, which matches how they read (Web is close to Entangle, Barkskin is a +3 AC buff, Blindness/Deafness is a blind-or-deafen with a repeat save, Aid is five temporary HP to three allies). Either those spells are underpriced here, or WotC placed them at level 2 for reasons (duration, range, flexibility) that my items do not capture. I did not patch this, because forcing an extra item into each would be a guess.\n")
    A("## 7. Rules that follow from the study\n")
    A(tbl(["Rule", "Value"], [
        ["Budgets", f"cantrip {B[0]}, level 1 {B[1]}, level 2 {B[2]}"],
        ["Effect floor", f"level 1: {P.L1_FLOOR}. level 2: {P.L2_FLOOR}"],
        ["Effect ceiling", f"cantrip: {P.CANTRIP_CEIL}. level 1: {P.L2_FLOOR - 1}"],
        ["Items by level", "Each item has a minimum level. A level 1 spell cannot use a level 2 item."],
        ["Magnitude caps", "Damage, healing, temporary HP, targets, AC, and similar items cannot exceed the highest value seen at that level, carried up from lower levels. Damage from a spell that splits across targets has its own cap."],
        ["Control cap", f"Strong conditions together cost at most {cal['control_cap']['1']} at level 1 and {cal['control_cap']['2']} at level 2. Cantrips have none."],
        ["Flat items", "Taken once. No stacking."],
        ["Convex price", f"Price grows with magnitude to the power {1 + P.EXP:.1f}, so doubling damage more than doubles the price."],
        ["Limit refunds", f"Capped at {int(P.LIMIT_CAP * 100)}% of the effect cost."],
        ["Upcasting", f"Each increase per slot level costs {int(P.UPCAST_SHARE * 100)}% of buying it outright. Targets rise by at most {P.UPCAST_TARGETS} per slot level. A damage or healing increase cannot exceed the base amount per slot level."]]))
    A("\n## 8. Limits of this study\n")
    A("- Three levels is too few to pick a curve from spell data alone. The DMG table breaks the tie only if my recollection of it is right.")
    A("- Every spell's build, and the price of every level 2 item, is my judgment. The calibration tunes category multipliers, not individual items. A mispriced item stays mispriced.")
    A("- The level 2 list and spell text come from memory. Some SRD level 2 spells may be missing.")
    A("- Caps come from the spells I built, so a mistake in one build moves a cap.")
    A("- Upcasting is priced from the first listed increase only. Spells that scale in other ways (duration, radius, hit point pools) pay a flat charge.")
    A("- Concentration, saves, and monster hit points are not modeled. Damage is an average roll.")
    return L
