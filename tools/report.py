import csv, json, os
from collections import Counter
import pricing as P
import analysis

def tbl(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)

def g(x):
    s = f"{x:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s

GROUP_TITLES = [("dmg", "Damage and delivery"), ("heal", "Healing"), ("buff", "Buffs and debuffs"), ("cond", "Conditions and control"), ("util", "Utility"), ("area", "Targets and area")]
GROUPS = [(title, [i for i, v in sorted(P.ITEMS.items(), key=lambda kv: (kv[1][5], kv[0])) if v[4] == cat]) for cat, title in GROUP_TITLES]
TIERS = {0: "Cantrip+", 1: "Level 1+", 2: "Level 2+", 3: "Level 3+"}

def eff(item):
    label, base, unit, ref, cat, tier = P.ITEMS[item]
    return P.price(item, ref) if ref else P.price(item, 1)

def unit_text(item):
    label, base, unit, ref, cat, tier = P.ITEMS[item]
    if ref:
        return f"{unit} (at {ref:g})"
    return unit

def patterns_one(S, nets):
    n = len(S)
    def pct(f): return f"{sum(1 for s in S if f(s))} of {n}"
    cls = Counter(len(s["classes"]) for s in S)
    ct = Counter(s["casting_time"].split(",")[0] for s in S)
    dur = Counter(s["duration"] for s in S)
    conc = [t for (s, t) in zip(S, nets) if s["concentration"]]
    non = [t for (s, t) in zip(S, nets) if not s["concentration"]]
    mat = [t for (s, t) in zip(S, nets) if "M" in s["components"]]
    nomat = [t for (s, t) in zip(S, nets) if "M" not in s["components"]]
    avg = lambda a: f"{sum(a) / len(a):.0f}" if a else "n/a"
    return [
     pct(lambda s: "V" in s["components"]), pct(lambda s: "S" in s["components"]), pct(lambda s: "M" in s["components"]),
     pct(lambda s: bool(s["material"]) and "gp" in s["material"]), pct(lambda s: s["concentration"]), pct(lambda s: s["ritual"]),
     pct(lambda s: bool(s["at_higher_levels"])), f"{ct['1 action']} of {n}", f"{ct['1 bonus action'] + ct['1 reaction']} of {n}",
     f"{ct['1 minute'] + ct['10 minutes'] + ct['1 hour']} of {n}", f"{dur['Instantaneous']} of {n}",
     f"{sum(k * v for k, v in cls.items()) / n:.1f}", f"{cls[1]} of {n}",
     avg(conc), avg(non), avg(mat), avg(nomat)]

PATTERN_LABELS = ["Verbal component", "Somatic component", "Material component", "Material with a gold cost", "Concentration", "Ritual",
    "Has an at-higher-levels clause", "Cast as an action", "Cast as a bonus action or reaction", "Cast time of a minute or more",
    "Instantaneous duration", "Average classes per spell", "Spells on exactly one class list",
    "Average net cost, concentration spells", "Average net cost, other spells", "Average net cost, spells with a material", "Average net cost, spells with no material"]

def write(sp):
    scored = []
    for k, (s, spec) in sp.items():
        rows, t = P.score(spec)
        e = sum(r[2] for r in rows if r[0] in ("Effect", "Floor"))
        scored.append((t, s["name"], k, s, rows, spec["level"], e))
    scored.sort(key=lambda x: (x[5], -x[0], x[1]))
    by = {lv: [x for x in scored if x[5] == lv] for lv in (0, 1, 2, 3)}
    B = P.BUDGETS
    cal = json.load(open(P.CAL_PATH))
    os.makedirs(os.path.join(P.ROOT, "data"), exist_ok=True)
    with open(os.path.join(P.ROOT, "data", "point-buy.json"), "w") as f:
        json.dump({"budgets": {"cantrip": B[0], "level_1": B[1], "level_2": B[2], "level_3": B[3]},
            "effect_floor": {"level_1": P.floor(1), "level_2": P.floor(2), "level_3": P.floor(3)},
            "effect_ceiling": {"cantrip": P.CANTRIP_CEIL, "level_1": P.ceiling(1), "level_2": P.ceiling(2), "level_3": P.ceiling(3)},
            "limit_refund_cap_share": P.LIMIT_CAP, "convexity_exponent": P.EXP,
            "category_multipliers": cal["mult"], "magnitude_caps": cal["caps"], "control_cap": cal["control_cap"],
            "upcast": {"share_of_outright_price": P.UPCAST_SHARE, "max_extra_targets_per_level": P.UPCAST_TARGETS, "max_increase_share_of_base": P.UPCAST_MAX},
            "items": {k: {"label": v[0], "base_price": v[1], "unit": v[2], "convex_reference": v[3], "category": v[4], "min_level": v[5], "price_at_reference": round(eff(k), 2)} for k, v in P.ITEMS.items()},
            "limits": {k: {"label": v[0], "base_refund": v[1], "refund": round(v[1] * P.MULT["limit"], 2)} for k, v in P.LIMITS.items()},
            "casting_time": {k: round(v * P.MULT["cast"], 2) for k, v in P.CASTING},
            "range": {k: round(v * P.MULT["range"], 2) for k, v in P.RANGE.items()},
            "duration": {k: round(v * P.MULT["dur"], 2) for k, v in P.DURATION.items()},
            "concentration": round(P.CONC * P.MULT["conc"], 2), "ritual": round(P.RITUAL * P.MULT["extra"], 2),
            "scaling_flat": {str(k): round(v * P.MULT["extra"], 2) for k, v in P.SCALING.items()},
            "components": {k: round(v * P.MULT["comp"], 2) for k, v in P.COMP.items()},
            "material_gp_tiers": [{"max_gp": c, "refund": round(v * P.MULT["comp"], 2)} for c, v in P.GP_TIERS],
            "consumed_multiplier": P.CONSUMED_MULT,
            "class_availability": [{"max_classes": c, "points": round(v * P.MULT["avail"], 2)} for c, v in P.CLASS_AVAIL]}, f, indent=2)
        f.write("\n")
    with open(os.path.join(P.ROOT, "data", "spell-scores.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["spell", "level", "net_cost", "budget", "points_left", "effect_total", "concentration", "components", "classes"])
        for t, n, k, s, rows, lv, e in scored:
            w.writerow([n, lv, t, B[lv], round(B[lv] - t, 1), round(e, 1), s["concentration"], "".join(s["components"]), len(s["classes"])])

    L = []
    A = L.append
    A("# Spell Point Buy\n")
    A(f"A point budget system for building cantrips and spells of levels 1 to 3. A cantrip gets **{B[0]} points**, a 1st-level spell **{B[1]}**, a 2nd-level spell **{B[2]}**, and a 3rd-level spell **{B[3]}**. Effects, range, and duration cost points. Components and limits give points back. A spell is legal if it passes every rule below and its net cost is at or under its budget.\n")
    A("> This is a homebrew tool. Prices are my own design, calibrated against the 24 cantrips, 49 level 1 spells, and 53 level 2 spells in `spells/`, with the 43 level 3 spells held out and measured.  They are not official. The spell files were written from memory and are not checked against the books, and the DMG guidance in `docs/creating-a-spell.md` is also from memory. Why the budgets are 150 and 250 at levels 2 and 3, and how the curve was chosen, is in `docs/spell-scaling-analysis.md`. Playtest before trusting any score.\n")
    A("## Budgets and clearances\n")
    A(tbl(["Level", "Budget", "Effects must total", "Magnitude caps", "Strong conditions total at most"], [
        ["Cantrip", B[0], f"{P.CANTRIP_CEIL} or less", "yes", "no strong conditions"],
        ["Level 1", B[1], f"{P.floor(1)} to {P.ceiling(1)}", "yes", cal["control_cap"]["1"]],
        ["Level 2", B[2], f"{P.floor(2)} to {P.ceiling(2)}", "yes", cal["control_cap"]["2"]],
        ["Level 3", B[3], f"{P.floor(3)} to {P.ceiling(3)}", "yes", cal["control_cap"]["3"]]]))
    A("\n\"Effects\" means the capability lines only: damage, healing, buffs, conditions, utility, targets, and area. Range, casting time, duration, and refunds are not counted.\n")
    A("## Rules\n")
    A(tbl(["Rule", "What it does"], [
        ["Effect floor", f"A level 1 spell's effects must total at least {P.floor(1)}, level 2 at least {P.floor(2)}, level 3 at least {P.floor(3)}. A smaller total is topped up with a floor line, so anything a level 1 spell does costs {P.floor(1)} or more at its strength, and each later floor equals the previous level's whole budget."],
        ["Effect ceiling", f"Cantrip effects must total {P.CANTRIP_CEIL} or less, just under the level 1 floor. From level 1 up, effects cannot exceed the level's budget."],
        ["Items by level", "Each item has a minimum level, shown in the tables. A spell can only use items at or below its level."],
        ["Magnitude caps", "Damage, healing, temporary HP, extra targets, AC, and other scalable items cannot exceed the highest value used at that level in the existing spells, carried up from lower levels. Damage has separate caps for touch spells, area spells, spells that split across targets, and cantrips that add a rider, because those get more or less damage than a plain ranged hit. Spells cast as a bonus action or reaction have their own lower caps for damage and healing."],
        ["Control cap", "Strong conditions (charmed, blinded, restrained, paralyzed, and so on) together cannot cost more than the cap for the level. Extra targets count toward it."],
        ["Extra targets", "Each extra target costs a share of every per-target line the spell already pays for: damage 70%, strong conditions 60%, buffs 50%, utility 50% (only if the spell has no area), healing 25%. A spell with nothing per-target cannot take extra targets, and area spells already hit everyone inside."],
        ["Convex price", f"Damage, healing, and AC rise faster than linearly. Price is proportional to amount to the power {1 + P.EXP:.1f}, so doubling an amount more than doubles its price."],
        ["Area price", "Price follows the square root of the footprint in square feet, so a larger area never costs less."],
        ["Duration and weak effects", f"A cantrip whose effects total under {P.DURATION_REF} pays between half and all of the duration price, in proportion. A one-hour light is not worth the same as a one-hour invisibility. Level 1 and 2 spells always pay in full because their effects start at the floor."],
        ["No duplicates", "List each item and each limit once. Flat items are taken once. Use the quantity for per-unit items."],
        ["Limit refund cap", f"Refunds from limits cannot exceed {int(P.LIMIT_CAP * 100)}% of the effect cost."],
        ["Upcasting", f"List the increase per slot level. It costs {int(P.UPCAST_SHARE * 100)}% of buying that increase outright, and an extra target costs {int(P.UPCAST_SHARE * 100)}% of what a base extra target costs. Extra targets rise by at most {P.UPCAST_TARGETS} per slot level. A damage, healing, or temporary HP increase cannot exceed the base amount per slot level. Scaling in other ways pays a flat charge."],
        ["Cantrip scaling", f"A damage cantrip that scales with character level pays {int(P.CANTRIP_SCALE_SHARE * 100)}% of its damage price, so scaling a d10 costs more than scaling a d4."],
        ["Reach beyond the listed range", "A spell that is Self but throws or fires something farther pays for the farther range (Produce Flame hurls 30 feet)."]]))
    A("\n## How to build a spell in seven steps\n")
    A("1. **Pick the level.** Budgets are cantrip %d, level 1 %d, level 2 %d, level 3 %d." % (B[0], B[1], B[2], B[3]))
    A("2. **Pick the effect.** Add the costs from the tables. Multiply per-unit items by their quantity. Check the caps, the control cap, and the floor or ceiling.")
    A("3. **Pick delivery.** Add range, casting time, and duration. Add area or extra target costs.")
    A("4. **Add upcasting** if the spell scales.")
    A("5. **Add components.** Components are refunds. Material components with a gold cost refund the most.")
    A("6. **Add limits.** Each caveat that really constrains the spell refunds points, up to the cap. Do not claim a limit that never matters.")
    A("7. **Add up.** Net cost = effects + delivery + duration - refunds. Stay at or below budget, then playtest.\n")
    A("Skip the arithmetic with the calculator: `python tools/pointbuy.py calc examples/new-spell.json`. Set `\"level\"` to 0, 1, or 2. Write quantities as the second value in a line, and an optional `\"upcast\": [\"dmg\", 3.5]`.\n")
    A("### Reading a score\n")
    brows = []
    for lv, nm in ((0, "Cantrip"), (1, "Level 1"), (2, "Level 2"), (3, "Level 3")):
        b = B[lv]
        brows += [[nm, f"Over {b}", "Over budget."],
                  [nm, f"{round(b * 0.9)} to {b}", "Premium. Among the strongest spells of the level."],
                  [nm, f"{round(b * 0.6)} to {round(b * 0.9) - 1}", "Standard."],
                  [nm, f"Under {round(b * 0.6)}", "Utility or situational. Headroom to spend on range, duration, or targets."]]
    A(tbl(["Tier", "Net cost", "Meaning"], brows))
    A("\n## What the existing spells show\n")
    A("Counted from the spell files, and used to set the refund sizes below.\n")
    cols = []
    for lv in (0, 1, 2, 3):
        S = [x[3] for x in by[lv]]; nets = [x[0] for x in by[lv]]
        cols.append(patterns_one(S, nets))
    A(tbl(["Pattern", "Cantrips (%d)" % len(by[0]), "Level 1 (%d)" % len(by[1]), "Level 2 (%d)" % len(by[2]), "Level 3 (%d)" % len(by[3])], [[PATTERN_LABELS[i]] + [cols[l][i] for l in range(4)] for i in range(len(PATTERN_LABELS))]))
    A("\nTakeaways: nearly every spell has a verbal component, most have a somatic one, and about half have a material. Materials are common, so a mundane material refunds little. Gold-cost materials are rare and start at level 1, so they refund heavily. Spells with materials do not score higher than spells without in this set, so the data does not by itself show that materials mark stronger spells. The larger refund for gold-cost materials follows the design rule that costly components limit power, not a trend in these files. Concentration spells are the long-duration ones, so the concentration refund offsets part of the duration cost.\n")
    A("## Price tables (points you spend)\n")
    A("Prices are base price times a calibrated category multiplier. \"Points\" is the price of one use. Items marked with a reference amount use the convex curve, and the price shown is at that reference amount. Use the curve table below for other amounts.\n")
    for gname, ids in GROUPS:
        A(f"### {gname}\n")
        A(tbl(["Item", "Points", "Unit", "Available from"], [[P.ITEMS[i][0], g(eff(i)) if i != "target_extra" else "see rules", unit_text(i), TIERS[P.ITEMS[i][5]]] for i in ids]))
        A("")
    A("### Convex price curves\n")
    A("Price for an amount `q` is `base x q x (q / reference)^0.4 x category multiplier`.\n")
    amounts = [(4.5, "dmg"), (7, "dmg"), (10.5, "dmg"), (14, "dmg"), (16.5, "dmg"), (21, "dmg")]
    A(tbl(["Average damage", "Level 1 or 2 damage price", "Healing price at the same amount"], [[q, g(P.price("dmg", q)), g(P.price("heal", q))] for q, _ in amounts]))
    A("\nCantrip damage (`c_dmg`) uses its own lower base and is capped at an average of 6.5.\n")
    A("### Range\n")
    A(tbl(["Range", "Points"], [[k, g(v * P.MULT["range"])] for k, v in P.RANGE.items()]))
    A("\n### Casting time\n")
    A(tbl(["Casting time", "Points"], [[k, g(v * P.MULT["cast"])] for k, v in P.CASTING]))
    A("\nA longer casting time is a refund. A bonus action or reaction costs more because it stacks with your other actions.\n")
    A("### Duration\n")
    A(tbl(["Duration", "Points"], [[k, g(v * P.MULT["dur"])] for k, v in P.DURATION.items()]))
    A("\n### Other costs\n")
    A(tbl(["Item", "Points"], [["Ritual casting (cast without a slot)", g(P.RITUAL * P.MULT["extra"])], ["Flat upcast charge, level 1 (no listed increase)", g(P.SCALING[1] * P.MULT["extra"])], ["Flat upcast charge, level 2 (no listed increase)", g(P.SCALING[2] * P.MULT["extra"])], ["Flat upcast charge, level 3 (no listed increase)", g(P.SCALING[3] * P.MULT["extra"])]]))
    A("\nCantrips are scored at the base tier only. Extra dice at levels 5, 11, and 17 are covered by the cantrip scaling share. Listed upcast increases (see the rules) replace the flat charge.\n")
    A("## Refund tables (points you get back)\n")
    A("### Components\n")
    A(tbl(["Component", "Refund"], [["Verbal", g(P.COMP["V"] * P.MULT["comp"])], ["Somatic", g(P.COMP["S"] * P.MULT["comp"])], ["Material, no stated cost", g(P.COMP["M"] * P.MULT["comp"])]]))
    A("\nMaterials with a stated gold cost replace the plain material refund:\n")
    prev = 0; rows = []
    for cap, v in P.GP_TIERS:
        rows.append([f"{prev + 1} to {cap} gp" if cap < 10**9 else f"over {prev} gp", g(v * P.MULT["comp"]), g(v * P.MULT["comp"] * P.CONSUMED_MULT)]); prev = cap
    A(tbl(["Cost of material", "Refund, kept", "Refund, consumed"], rows))
    A("\nA consumed material refunds 1.5 times as much, because the caster pays again on every cast.\n")
    A("### Caveats and limits\n")
    A(tbl(["Limit", "Refund"], [[v[0], g(v[1] * P.MULT["limit"])] for v in P.LIMITS.values()]))
    A("\n### Concentration and class availability\n")
    A(tbl(["Item", "Points"], [["Concentration", g(P.CONC * P.MULT["conc"])], ["On 1 class list", g(P.CLASS_AVAIL[0][1] * P.MULT["avail"])], ["On 2 or 3 class lists", g(P.CLASS_AVAIL[1][1] * P.MULT["avail"])], ["On 4 or 5 class lists", g(P.CLASS_AVAIL[2][1] * P.MULT["avail"])], ["On 6 or more class lists", "+" + g(P.CLASS_AVAIL[3][1] * P.MULT["avail"])]]))
    A("\nUse concentration only if the spell lasts a minute or more.\n")
    A("## Worked examples\n")
    for key in ("fire-bolt", "magic-missile", "hold-person", "fireball"):
        s, spec = sp[key]; rows, t = P.score(spec)
        A(f"### {s['name']}: {t:g} of {B[spec['level']]} points\n")
        A(tbl(["Type", "Item", "Points"], [[c, l, f"{p:+g}"] for c, l, p in rows]))
        A("")
    for title, lv in (("Scorecard: 24 cantrips", 0), ("Scorecard: 49 level 1 spells", 1), ("Scorecard: 53 level 2 spells", 2), ("Scorecard: 43 level 3 spells", 3)):
        A(f"## {title}\n")
        A(tbl(["Spell", "Net cost", "Left", "Effects", "Conc.", "Comp.", "Classes"],
              [[n, f"{t:g}", f"{B[lv] - t:g}", f"{e:g}", "yes" if s["concentration"] else "", "".join(s["components"]), len(s["classes"])] for t, n, k, s, rows, _, e in by[lv]]))
        A("")
    A("Full line items for any spell: `python tools/pointbuy.py score <spell-file-name>`, for example `score fire-bolt`. The same data is in `data/spell-scores.csv` and `data/point-buy.json`. Recalibrate after any change to prices or builds with `python tools/pointbuy.py fit`, then `report`.\n")
    A("## Known limits of this model\n")
    A("- Damage is valued by average roll. It does not model how monsters resist or how often a save fails.")
    A("- Typical spells score well under their budget. The budget is a ceiling set by the strongest spell at each level. See `docs/spell-scaling-analysis.md`.")
    A("- Hard control effects are priced by my judgment of how much a lost turn is worth. Not tested at a table. Adjust the condition costs if your group disagrees.")
    A("- A few level 2 and level 3 spells pass as one level lower under these rules. The stress test in the analysis lists them.")
    A("- The level 3 budget is measured from 43 spells that were written once and have had no second pass. It is the least checked number here.")
    A("- Run `python tools/pointbuy.py check` after any change. It runs the logic checks and the exploit probes and exits non-zero on a failure.")
    A("- A limit only refunds points if it matters. DMs should reject a limit that never comes up.")
    A("- Utility spells score low because they have little combat value. That is not a mistake. Raise their duration or area for a stronger version.")
    A("- Levels 4 to 9 are not modeled.\n")
    open(os.path.join(P.ROOT, "docs", "spell-point-buy.md"), "w").write("\n".join(L) + "\n")
    open(os.path.join(P.ROOT, "docs", "spell-scaling-analysis.md"), "w").write("\n".join(analysis.write(sp)) + "\n")
