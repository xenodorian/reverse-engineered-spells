import csv, json, os
from collections import Counter
import pointbuy as P

def tbl(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)

GROUPS = [
 ("Damage and healing", ["dmg","dmg_rider","dmg_recurring","heal","temp_hp","temp_hp_recurring"]),
 ("Delivery of a damaging effect", ["rel_attack","rel_save_half","rel_auto","no_save"]),
 ("Buffs, debuffs and movement", ["ac_bonus","die_bonus","advantage_vs_target","advantage_next","protect_types","immune_frightened","speed_bonus","extra_dash","jump_triple","fall_immunity","magic_missile_immune"]),
 ("Conditions (per target)", ["cond_prone","cond_charmed","cond_frightened","cond_blinded","cond_restrained","cond_incapacitated","cond_unconscious","cond_command","forced_move","difficult_terrain","heavy_obscure","util_outline","util_ignite"]),
 ("Utility", ["util_detect","util_detect_aura","util_lore","util_language","util_speak","util_create_water","util_purify","util_food","util_alarm","util_ward","util_illusion_image","util_disguise","util_script","util_servant","util_familiar","util_mark_track","util_mark_move","persist"]),
 ("Targets and area", ["target_extra","split_targets","area_square10","area_square20","area_cone15","area_cube15","area_cube20","area_radius20","area_radius30"]),
]

def patterns_one(sp):
    n = len(sp)
    S = [s for s, _ in sp.values()]
    sc = {k: P.score(spec)[1] for k, (s, spec) in sp.items()}
    def pct(f): return f"{sum(1 for s in S if f(s))} of {n}"
    conc = [sc[k] for k, (s, _) in sp.items() if s["concentration"]]
    non = [sc[k] for k, (s, _) in sp.items() if not s["concentration"]]
    mat = [sc[k] for k, (s, _) in sp.items() if "M" in s["components"]]
    nomat = [sc[k] for k, (s, _) in sp.items() if "M" not in s["components"]]
    avg = lambda a: sum(a) / len(a)
    cls = Counter(len(s["classes"]) for s in S)
    dur = Counter(s["duration"] for s in S)
    ct = Counter(s["casting_time"].split(",")[0] for s in S)
    rows = [
     ("Verbal component", pct(lambda s: "V" in s["components"])),
     ("Somatic component", pct(lambda s: "S" in s["components"])),
     ("Material component", pct(lambda s: "M" in s["components"])),
     ("Material with a gold cost", pct(lambda s: bool(s["material"]) and "gp" in s["material"])),
     ("Concentration", pct(lambda s: s["concentration"])),
     ("Ritual", pct(lambda s: s["ritual"])),
     ("Has an at-higher-levels clause", pct(lambda s: bool(s["at_higher_levels"]))),
     ("Cast as an action", f"{ct['1 action']} of {n}"),
     ("Cast as a bonus action or reaction", f"{ct['1 bonus action'] + ct['1 reaction']} of {n}"),
     ("Cast time of a minute or more", f"{ct['1 minute'] + ct['1 hour']} of {n}"),
     ("Instantaneous duration", f"{dur['Instantaneous']} of {n}"),
     ("Average classes per spell", f"{sum(k * v for k, v in cls.items()) / n:.1f}"),
     ("Spells on exactly one class list", f"{cls[1]} of {n}"),
     ("Average net cost, concentration spells", f"{avg(conc):.0f}"),
     ("Average net cost, other spells", f"{avg(non):.0f}"),
     ("Average net cost, spells with a material", f"{avg(mat):.0f}"),
     ("Average net cost, spells with no material", f"{avg(nomat):.0f}"),
    ]
    return rows

def patterns(sp):
    c = {k: v for k, v in sp.items() if v[1]['level'] == 0}
    l = {k: v for k, v in sp.items() if v[1]['level'] == 1}
    a, b = patterns_one(c), patterns_one(l)
    return [(x[0], x[1], y[1]) for x, y in zip(a, b)]

C_GROUPS = [
 ("Damage and rider effects", ["c_dmg","c_slow10","c_no_heal","c_no_reactions","c_disadv_next","c_adv_self","c_ignore_cover"]),
 ("Boosts", ["c_d4_check","c_d4_save","c_weapon"]),
 ("Utility", ["c_light","c_lights4","c_hand","c_mend","c_message","c_illusion_min","c_trick","c_nature","c_wonder","c_stabilize","c_throw"]),
]

def effect_total(rows):
    return sum(r[2] for r in rows if r[0] == "Effect")

def write(sp):
    scored = []
    for k, (s, spec) in sp.items():
        rows, t = P.score(spec)
        scored.append((t, s["name"], k, s, rows, spec["level"], effect_total(rows)))
    scored.sort(key=lambda x: (x[5], -x[0], x[1]))
    C = [x for x in scored if x[5] == 0]
    L1 = [x for x in scored if x[5] == 1]
    floored = [x for x in L1 if any(r[0] == "Floor" for r in x[4])]
    os.makedirs(os.path.join(P.ROOT, "data"), exist_ok=True)
    with open(os.path.join(P.ROOT, "data", "point-buy.json"), "w") as f:
        json.dump({"budgets": {"cantrip": P.BUDGETS[0], "level_1": P.BUDGETS[1]},
            "level_1_effect_floor": P.L1_FLOOR, "cantrip_effect_ceiling": P.CANTRIP_CEIL,
            "limit_refund_cap_share": P.LIMIT_CAP,
            "effects": {k: {"label": v[0], "points": v[1], "unit": v[2], "tier": "shared" if k in P.SHARED else "level_1"} for k, v in P.EFFECTS.items()},
            "cantrip_effects": {k: {"label": v[0], "points": v[1], "unit": v[2], "cap": P.C_CAPS.get(k)} for k, v in P.C_EFFECTS.items()},
            "limits": {k: {"label": v[0], "points": v[1]} for k, v in P.LIMITS.items()},
            "casting_time": dict(P.CASTING), "range": P.RANGE, "duration": P.DURATION,
            "concentration": P.CONC, "ritual": P.RITUAL, "scaling_level_1": P.SCALING, "scaling_cantrip": P.CANTRIP_SCALING,
            "components": P.COMP, "material_gp_tiers": [{"max_gp": c, "points": v} for c, v in P.GP_TIERS],
            "consumed_multiplier": P.CONSUMED_MULT,
            "class_availability": [{"max_classes": c, "points": v} for c, v in P.CLASS_AVAIL]}, f, indent=2)
        f.write("\n")
    with open(os.path.join(P.ROOT, "data", "spell-scores.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["spell", "level", "net_cost", "budget", "points_left", "effect_total", "concentration", "components", "classes"])
        for t, n, k, s, rows, lv, e in scored:
            w.writerow([n, lv, t, P.BUDGETS[lv], round(P.BUDGETS[lv] - t, 1), round(e, 1), s["concentration"], "".join(s["components"]), len(s["classes"])])

    L = []
    A = L.append
    A("# Spell Point Buy\n")
    A("A point budget system for building cantrips and 1st-level spells. A cantrip gets **25 points**. A 1st-level spell gets **100 points**. Effects, range, and duration cost points. Components and limits give points back. A spell is legal if its net cost is at or under its budget.\n")
    A("> This is a homebrew tool. The numbers are my own design, tuned against the 24 cantrips in `spells/cantrip/` and the 49 level 1 spells in `spells/level-1/`. They are not official. The DMG guidance they lean on was summarized from memory and is unverified (see `docs/creating-a-spell.md`). The spell files themselves were also written from memory and are not checked against the books. Playtest before trusting any score.\n")
    A("## The cantrip and level 1 clearance rules\n")
    A("Two rules keep a firm gap between the tiers. \"Effects\" means the capability lines only: damage, healing, conditions, utility, targets, and area. Range, casting time, duration, and refunds are not counted.\n")
    A(tbl(["Rule", "Applies to", "What it does"], [
        ["Level 1 floor", "Level 1 spells", f"Effects must total at least {P.L1_FLOOR}. If they total less, you pay the gap as a \"Level 1 effect floor\" line. So anything a level 1 spell does costs 50 or more at its level 1 strength."],
        ["Cantrip ceiling", "Cantrips", f"Effects must total {P.CANTRIP_CEIL} or less. The calculator rejects a cantrip above that, because it would be level 1 strength."],
        ["Cantrip tier items", "Cantrips", "A cantrip can only use the cantrip-scale effects and the shared items in the tables below. Level 1 effect items are blocked."],
        ["Cantrip damage cap", "Cantrips", "Cantrip damage tops out at an average of 6.5 (1d12). Level 1 damage starts at about 10."],
        ["Limit refund cap", "Both", f"Refunds from limits cannot exceed {int(P.LIMIT_CAP * 100)}% of the effect cost. This stops a trivial effect from being bought for free by stacking caveats."]]))
    top_c = max(x[6] for x in C)
    A(f"\nResult on the current spells: the highest cantrip effect total is {top_c:g}. {len(floored)} of the {len(L1)} level 1 spells needed the floor top-up: " + ", ".join(x[1] for x in sorted(floored, key=lambda x: x[1])) + ".\n")
    A("## How to build a spell in six steps\n")
    A("1. **Pick the level.** Cantrip budget is 25. Level 1 budget is 100.")
    A("2. **Pick the effect.** Add up the costs from the effect tables. Multiply per-unit items by their quantity. Check the floor or ceiling rule.")
    A("3. **Pick delivery.** Add the cost of range, casting time, and duration. Add area or extra target costs.")
    A("4. **Add components.** Components are refunds. Material components with a gold cost refund the most.")
    A("5. **Add limits.** Each caveat that really constrains the spell refunds points, up to the cap. Do not claim a limit that never matters.")
    A("6. **Add up.** Net cost = effects + delivery + duration - refunds. Stay at or below budget, then playtest.\n")
    A("Skip the arithmetic with the calculator: `python tools/pointbuy.py calc examples/new-spell.json` or `examples/new-cantrip.json`. Set `\"level\": 0` for a cantrip.\n")
    A("### Reading a score\n")
    A(tbl(["Tier", "Net cost", "Meaning"], [
        ["Level 1", "Over 100", "Over budget. Add limits or cut effects."],
        ["Level 1", "85 to 100", "Premium. Among the best first-level spells (Guiding Bolt, Bless, Sleep)."],
        ["Level 1", "55 to 84", "Standard. Solid, reliable spells."],
        ["Level 1", "Under 55", "Utility or situational. You have headroom: spend unused points on range, duration, or targets."],
        ["Cantrip", "Over 25", "Over budget."],
        ["Cantrip", "20 to 25", "Strong cantrip. Reliable damage or a flexible effect (Fire Bolt, Shillelagh)."],
        ["Cantrip", "Under 20", "Minor or niche. Room to add range or a rider."]]))
    A("\n## What the existing spells show\n")
    A("Counted from the spell files, and used to set the refund sizes below.\n")
    A(tbl(["Pattern", "Cantrips (24)", "Level 1 (49)"], patterns(sp)))
    A("\nTakeaways: nearly every spell has a verbal component, most have a somatic one, and about half have a material. Materials are common, so a mundane material refunds little. Gold-cost materials are rare (3 level 1 spells, no cantrips), so they refund heavily. Spells with materials do not score higher than spells without in this set, so the data does not by itself show that materials mark stronger spells. The larger refund for gold-cost materials follows the design rule that costly components limit power, not a trend in these files. Concentration spells are the long-duration ones, so the concentration refund offsets part of the duration cost. Cantrips never use rituals and rarely use concentration. About half of damage cantrips scale with character level, which is why scaling has its own cantrip price.\n")
    A("## Cost tables (points you spend)\n")
    A("### Level 1 effects\n")
    A("These are level 1 only, except the items marked shared, which cantrips may also use.\n")
    for g, ids in GROUPS:
        A(f"#### {g}\n")
        A(tbl(["Item", "Points", "Unit", "Cantrips?"], [[P.EFFECTS[i][0], P.EFFECTS[i][1], P.EFFECTS[i][2], "shared" if i in P.SHARED else "no"] for i in ids]))
        A("")
    A("### Cantrip effects\n")
    A("Weaker versions of level 1 effects. Cantrips are limited to these and the shared items. Level 1 spells may use them too.\n")
    for g, ids in C_GROUPS:
        A(f"#### {g}\n")
        A(tbl(["Item", "Points", "Unit"], [[P.C_EFFECTS[i][0] + (f" (max {P.C_CAPS[i]:g})" if i in P.C_CAPS else ""), P.C_EFFECTS[i][1], P.C_EFFECTS[i][2]] for i in ids]))
        A("")
    A("### Range\n")
    A(tbl(["Range", "Points"], [[k, v] for k, v in P.RANGE.items()]))
    A("\n### Casting time\n")
    A(tbl(["Casting time", "Points"], [[k, f"{v:+d}"] for k, v in P.CASTING]))
    A("\nA longer casting time is a refund. A bonus action or reaction costs more because it stacks with your other actions.\n")
    A("### Duration\n")
    A(tbl(["Duration", "Points"], [[k, v] for k, v in P.DURATION.items()]))
    A("\n### Other costs\n")
    A(tbl(["Item", "Points"], [["Ritual casting (cast without a slot)", f"+{P.RITUAL}"], ["Scales with higher slots (level 1)", f"+{P.SCALING}"], ["Scales with character level (cantrip)", f"+{P.CANTRIP_SCALING}"]]))
    A("\nCantrip scaling is scored at the base tier only. Extra dice at levels 5, 11, and 17 are covered by the scaling charge.\n")
    A("## Refund tables (points you get back)\n")
    A("### Components\n")
    A(tbl(["Component", "Refund"], [["Verbal", P.COMP["V"]], ["Somatic", P.COMP["S"]], ["Material, no stated cost", P.COMP["M"]]]))
    A("\nMaterials with a stated gold cost replace the plain material refund:\n")
    prev = 0; rows = []
    for cap, v in P.GP_TIERS:
        rows.append([f"{prev + 1} to {cap} gp" if cap < 10**9 else f"over {prev} gp", v, round(v * P.CONSUMED_MULT)]); prev = cap
    A(tbl(["Cost of material", "Refund, kept", "Refund, consumed"], rows))
    A("\nA consumed material refunds 1.5 times as much, because the caster pays again on every cast.\n")
    A("### Caveats and limits\n")
    A(tbl(["Limit", "Refund"], [[v[0], v[1]] for v in P.LIMITS.values()]))
    A("\n### Class availability\n")
    A(tbl(["Spell is on this many class lists", "Points"], [["1", P.CLASS_AVAIL[0][1]], ["2 or 3", P.CLASS_AVAIL[1][1]], ["4 or 5", P.CLASS_AVAIL[2][1]], ["6 or more", f"+{P.CLASS_AVAIL[3][1]}"]]))
    A("\nConcentration refunds %d points. Use it only if the spell lasts a minute or more.\n" % -P.CONC)
    A("## Worked examples\n")
    for key in ("fire-bolt", "magic-missile", "sleep"):
        s, spec = sp[key]; rows, t = P.score(spec)
        A(f"### {s['name']}: {t:g} of {P.BUDGETS[spec['level']]} points\n")
        A(tbl(["Type", "Item", "Points"], [[c, l, f"{p:+g}"] for c, l, p in rows]))
        A("")
    for title, group, lv in (("Scorecard: 24 cantrips", C, 0), ("Scorecard: 49 level 1 spells", L1, 1)):
        A(f"## {title}\n")
        A(tbl(["Spell", "Net cost", "Left", "Effects", "Conc.", "Comp.", "Classes"],
              [[n, f"{t:g}", f"{P.BUDGETS[lv] - t:g}", f"{e:g}", "yes" if s["concentration"] else "", "".join(s["components"]), len(s["classes"])] for t, n, k, s, rows, _, e in group]))
        A("")
    A("Full line items for any spell: `python tools/pointbuy.py score <spell-file-name>`, for example `score fire-bolt`. The same data is in `data/spell-scores.csv` and `data/point-buy.json`.\n")
    A("## Known limits of this model\n")
    A("- Damage is valued by average roll. It does not model how monsters resist or how often a save fails.")
    A("- Hard control effects may be priced unevenly. Incapacitated (72) now costs more than unconscious (52) because Hideous Laughter has no hit point pool and a target that takes damage gets advantage on its repeat save, while Sleep is capped by a pool and ends on damage. That is my judgment, not tested at a table. Adjust the condition costs if your group disagrees.")
    A("- The 50 point floor applies to a spell's whole effect package, not to each item. A single level 1 effect item can cost less than 50 as long as the spell's effects total 50 or more. If you wanted every individual item priced at 50 or more, the level 1 budget would need to rise.")
    A("- Cantrip scaling is flat priced. A cantrip that scales much harder than the standard dice steps should pay extra.")
    A("- Spell level beyond 1 is not modeled.")
    A("- A limit only refunds points if it matters. DMs should reject a limit that never comes up.")
    A("- Utility spells such as Identify score low because they have little combat value. That is not a mistake. Raise their duration or area for a stronger version.\n")
    open(os.path.join(P.ROOT, "docs", "spell-point-buy.md"), "w").write("\n".join(L) + "\n")
