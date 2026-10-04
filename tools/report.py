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

def patterns(sp):
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

def write(sp):
    scored = []
    for k, (s, spec) in sp.items():
        rows, t = P.score(spec)
        scored.append((t, s["name"], k, s, rows))
    scored.sort(key=lambda x: (-x[0], x[1]))
    # data files
    os.makedirs(os.path.join(P.ROOT, "data"), exist_ok=True)
    with open(os.path.join(P.ROOT, "data", "point-buy.json"), "w") as f:
        json.dump({"budget": P.BUDGET,
            "effects": {k: {"label": v[0], "points": v[1], "unit": v[2]} for k, v in P.EFFECTS.items()},
            "limits": {k: {"label": v[0], "points": v[1]} for k, v in P.LIMITS.items()},
            "casting_time": dict(P.CASTING), "range": P.RANGE, "duration": P.DURATION,
            "concentration": P.CONC, "ritual": P.RITUAL, "scaling": P.SCALING,
            "components": P.COMP, "material_gp_tiers": [{"max_gp": c, "points": v} for c, v in P.GP_TIERS],
            "consumed_multiplier": P.CONSUMED_MULT,
            "class_availability": [{"max_classes": c, "points": v} for c, v in P.CLASS_AVAIL]}, f, indent=2)
        f.write("\n")
    with open(os.path.join(P.ROOT, "data", "spell-scores.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["spell", "net_cost", "points_left", "concentration", "components", "classes"])
        for t, n, k, s, rows in scored:
            w.writerow([n, t, round(P.BUDGET - t, 1), s["concentration"], "".join(s["components"]), len(s["classes"])])

    L = []
    A = L.append
    A("# Spell Point Buy\n")
    A("A 100 point budget system for building 1st-level 5e style spells. Every spell gets 100 points. Effects, range, and duration cost points. Components and limits give points back. Ritual casting and upcasting cost a few extra. A spell is legal if its net cost is 100 or less.\n")
    A("> This is a homebrew tool. The numbers are my own design, tuned against the 49 spells in `spells/level-1/` so that the strongest first-level spells land near 100. They are not official. The DMG guidance they lean on was summarized from memory and is unverified (see `docs/creating-a-spell.md`). Playtest before trusting any score.\n")
    A("## How to build a spell in six steps\n")
    A("1. **Pick the effect.** Add up the costs from the Effect tables. Multiply per-unit items by their quantity.")
    A("2. **Pick delivery.** Add the cost of range, casting time, and duration. Add area or extra target costs.")
    A("3. **Add components.** Components are refunds. Material components with a gold cost refund the most.")
    A("4. **Add limits.** Each caveat that really constrains the spell refunds points. Do not claim a limit that never matters.")
    A("5. **Add up.** Net cost = effects + delivery + duration - refunds. Stay at or below 100.")
    A("6. **Check the band** in the table below, then playtest.\n")
    A("Run the calculator to skip the arithmetic: `python tools/pointbuy.py calc examples/new-spell.json`.\n")
    A("### Reading a score\n")
    A(tbl(["Net cost", "Meaning"], [
        ["Over 100", "Over budget. This is a stronger than first-level spell. Add limits or cut effects."],
        ["85 to 100", "Premium. Among the best first-level spells (Guiding Bolt, Bless, Sleep)."],
        ["55 to 84", "Standard. Solid, reliable spells."],
        ["Under 55", "Utility or situational. You have headroom: spend the unused points on range, duration, or targets."]]))
    A("\n## What the existing spells show\n")
    A("Counted from the 49 spell files, and used to set the refund sizes below.\n")
    A(tbl(["Pattern", "Count"], patterns(sp)))
    A("\nTakeaways: nearly every spell has a verbal component, most have a somatic one, and about half have a material. Materials are common, so a mundane material refunds little. Gold-cost materials are rare (3 spells), so they refund heavily. In this small set, spells with materials do not score higher than spells without, so the data does not by itself show that materials mark stronger spells. The larger refund for gold-cost materials follows the design rule that costly components limit power, not a trend in these 49 files. Concentration spells are the long-duration ones, so the concentration refund offsets part of the duration cost.\n")
    A("## Cost tables (points you spend)\n")
    for g, ids in GROUPS:
        A(f"### {g}\n")
        A(tbl(["Item", "Points", "Unit"], [[P.EFFECTS[i][0], P.EFFECTS[i][1], P.EFFECTS[i][2]] for i in ids]))
        A("")
    A("### Range\n")
    A(tbl(["Range", "Points"], [[k, v] for k, v in P.RANGE.items()]))
    A("\n### Casting time\n")
    A(tbl(["Casting time", "Points"], [[k, f"{v:+d}"] for k, v in P.CASTING]))
    A("\nA longer casting time is a refund. A bonus action or reaction costs more because it stacks with your other actions.\n")
    A("### Duration\n")
    A(tbl(["Duration", "Points"], [[k, v] for k, v in P.DURATION.items()]))
    A("\n### Other costs\n")
    A(tbl(["Item", "Points"], [["Ritual casting (cast without a slot)", f"+{P.RITUAL}"], ["Scales with higher slots", f"+{P.SCALING}"]]))
    A("\n## Refund tables (points you get back)\n")
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
    for key in ("magic-missile", "sleep"):
        s, spec = sp[key]; rows, t = P.score(spec)
        A(f"### {s['name']}: {t:g} points\n")
        A(tbl(["Type", "Item", "Points"], [[c, l, f"{p:+g}"] for c, l, p in rows]))
        A("")
    A("## Scorecard for all 49 spells\n")
    A(tbl(["Spell", "Net cost", "Left", "Conc.", "Comp.", "Classes"],
          [[n, f"{t:g}", f"{P.BUDGET - t:g}", "yes" if s["concentration"] else "", "".join(s["components"]), len(s["classes"])] for t, n, k, s, rows in scored]))
    A("\nFull line items for any spell: `python tools/pointbuy.py score <spell-file-name>`, for example `score hunters-mark`. The same data is in `data/spell-scores.csv` and `data/point-buy.json`.\n")
    A("## Known limits of this model\n")
    A("- Damage is valued by average roll. It does not model how monsters resist or how often a save fails.")
    A("- Hard control effects (Hideous Laughter scores 34, Sleep 90) may be priced unevenly. This is my judgment, not tested at a table. Adjust the condition costs if your group disagrees.")
    A("- Spell level is fixed at 1. For other levels, change the budget yourself. I have no tested numbers for that.")
    A("- A limit only refunds points if it matters. DMs should reject a limit that never comes up.")
    A("- Utility spells such as Identify score near zero because they have no combat value. Their low score is not a mistake. Raise their duration or area if you want a stronger version.\n")
    open(os.path.join(P.ROOT, "docs", "spell-point-buy.md"), "w").write("\n".join(L) + "\n")
