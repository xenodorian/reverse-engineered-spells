"""Logic checks for the point-buy system. Run with: python tools/pointbuy.py check

The system has no caps, item levels, floors, or ceilings. The only limit is the price against the budget,
so these checks look at prices: do they rise when they should, do canon spells land near their budget, and
does a clever build fail to get around the price."""
import copy, glob, json, os, re, statistics as st
import pricing as P

AREA_SQFT = {"area_cube5": 25, "area_radius5": 79, "area_square10": 100, "area_cone15": 112, "area_cube15": 225,
             "area_radius10": 314, "area_square20": 400, "area_cube20": 400, "area_line60": 600, "area_radius15": 707,
             "area_radius20": 1257, "area_radius30": 2827, "area_cone30": 450, "area_line100": 500, "area_cube30": 900,
             "area_cube40": 1600, "area_radius40": 5027}
SEVERITY = ["cond_prone", "cond_blinded", "cond_restrained", "cond_asleep", "cond_slow", "cond_incapacitated", "cond_charm_incap", "cond_paralyzed"]
WINDOW = 0.15            # canon spells are expected within this share of the budget, on average

def run(spells):
    results = []
    def check(name, ok, detail=""):
        results.append((name, bool(ok), detail))

    # 1. everything scores
    nets = {l: [] for l in range(4)}
    ratio = {}
    err = []
    for k, (s, spec) in spells.items():
        try:
            rows, t = P.score(spec)
        except (ValueError, KeyError) as e:
            err.append(f"{s['name']}: {e}")
            continue
        nets[spec["level"]].append(t)
        ratio[k] = t / P.BUDGETS[spec["level"]]
    check("Every canon spell scores without error", not err, "; ".join(err[:3]))

    # 2. canon sits near its budget
    for lvl in range(4):
        r = [ratio[k] for k, (s, spec) in spells.items() if spec["level"] == lvl and k in ratio]
        check(f"Level {lvl}: mean canon cost is within {int(WINDOW * 100)}% of the budget of {P.BUDGETS[lvl]}",
              abs(st.mean(r) - 1) <= WINDOW, f"mean {st.mean(r) * 100:.0f}% of budget, range {min(r) * 100:.0f}% to {max(r) * 100:.0f}%")
    check("No canon spell costs more than 150% of its budget", max(ratio.values()) <= 1.50, f"max {max(ratio.values()) * 100:.0f}%")
    check("Budgets rise with level", P.BUDGETS[0] < P.BUDGETS[1] < P.BUDGETS[2] < P.BUDGETS[3])
    mean = {l: st.mean(v) for l, v in nets.items()}
    check("Mean canon cost rises with level", mean[0] < mean[1] < mean[2] < mean[3], ", ".join(f"{mean[l]:.0f}" for l in range(4)))

    # 3. price ordering
    imp = json.load(open(P.CAL_PATH))["fit"].get("item_implied", {})
    spread = [max(v) / max(min(v), 0.5) for v in imp.values() if len(v) > 1]
    check("Items shared by two or three spells: how far apart the spells price them (informational)", True,
          f"median spread {st.median(spread):.1f}x, worst {max(spread):.1f}x over {len(spread)} items" if spread else "none")
    areas = sorted(AREA_SQFT, key=lambda a: AREA_SQFT[a])
    pr = [P.price(a) for a in areas]
    check("A larger area never costs less", all(pr[i] <= pr[i + 1] + 1e-9 for i in range(len(pr) - 1)))
    for label, table in (("Range", P.RANGE), ("Duration", P.DURATION)):
        vals = list(table.values())
        check(f"{label} prices never fall as the value grows", vals == sorted(vals))
    long = [v for k, v in P.CASTING if k in ("1 action", "1 minute", "10 minutes", "1 hour")]
    check("Casting time: longer is cheaper", long == sorted(long, reverse=True))
    check("Gold-cost refunds grow with the cost", [v for c, v in P.GP_TIERS] == sorted([v for c, v in P.GP_TIERS], reverse=True))
    check("A material refunds more than V or S, and a gold-cost one more again", abs(P.COMP["M"]) > abs(P.COMP["V"]) and abs(P.GP_TIERS[0][1]) > abs(P.COMP["M"]))
    check("Damage never gets cheaper as it grows", P.price("dmg", 20) >= 2 * P.price("dmg", 10) - 1e-9, f"convexity exponent {P.EXP:.2f}")
    check("A higher-level spell's effect costs more than a lower-level one in each family",
          P.price("util_dispel") > P.price("util_detect") and P.price("cond_paralyzed") > P.price("cond_charmed"))

    # 4. the price is the only limit: clever builds should fail
    base = {"level": 1, "casting_time": "1 action", "range": "60 feet", "duration": "Instantaneous", "components": ["V", "S"],
            "concentration": False, "ritual": False, "scaling": False, "class_count": 2}
    def net(lines, **kw):
        return P.score(dict(base, lines=lines, **kw), enforce=False)[1]
    check("Probe: 30 average damage in one attack costs more than the level 1 budget", net([("dmg", 30), ("rel_attack", 1)]) > P.BUDGETS[1], f"{net([('dmg', 30), ('rel_attack', 1)]):.0f}")
    check("Probe: 30 average damage costs more than the level 2 budget too", net([("dmg", 30), ("rel_attack", 1)], level=2) > P.BUDGETS[2])
    stack = [("cond_paralyzed", 1), ("cond_incapacitated", 1), ("cond_blinded", 1), ("cond_restrained", 1), ("cond_charmed", 1)]
    check("Probe: stacking five conditions costs far more than the level 3 budget", net(stack, level=3) > 1.5 * P.BUDGETS[3], f"{net(stack, level=3):.0f}")
    lims = [("lim_no_combat", 1), ("lim_type", 1), ("lim_willing", 1), ("lim_dm", 1), ("lim_fragile", 1), ("lim_decay", 1), ("lim_save_negates", 1), ("lim_aware", 1)]
    plain = net([("cond_paralyzed", 1)], components=["V"])
    padded = net([("cond_paralyzed", 1)] + lims, components=["V"])
    check("Probe: claiming eight limits cannot cut an effect's price by more than the refund cap", padded >= plain - P.REFUND_CAP * P.price("cond_paralyzed") - 1e-6, f"{plain:.0f} to {padded:.0f}")
    two = net([("cond_paralyzed", 1), ("target_extra", 1)]) - net([("cond_paralyzed", 1)])
    check("Probe: an extra target costs a real share of the first", two >= 0.4 * P.price("cond_paralyzed"), f"+{two:.0f} against {P.price('cond_paralyzed'):.0f}")
    try:
        net([("lim_type", 1), ("lim_type", 1), ("cond_charmed", 1)])
        dup_ok = False
    except ValueError:
        dup_ok = True
    check("Probe: a limit cannot be claimed twice", dup_ok)
    one = net([("dmg", 10.5), ("rel_save_half", 1), ("area_radius20", 1)])
    two_modes = P.score(dict(base, lines=[], modes=[[("dmg", 10.5), ("rel_save_half", 1), ("area_radius20", 1)]] * 4), enforce=False)[1]
    check("Probe: four identical modes cost more than one", two_modes > one, f"{one:.0f} against {two_modes:.0f}")
    half = net([("util_dispel", 1, 0.5)]); full = net([("util_dispel", 1)])
    check("Probe: a half-strength effect costs less than the full one, and scaling cannot make it free", 0 < half < full)

    # 5. data audit
    cl = {"Bard", "Cleric", "Druid", "Paladin", "Ranger", "Sorcerer", "Warlock", "Wizard"}
    problems = []
    for p in glob.glob(os.path.join(P.ROOT, "spells", "*", "*.json")):
        s = json.load(open(p)); n = s["name"]
        if s["duration"] not in P.DURATION: problems.append(f"{n}: duration")
        if s["range"].split(" (")[0] not in P.RANGE: problems.append(f"{n}: range")
        try: P.lookup(P.CASTING, s["casting_time"])
        except KeyError: problems.append(f"{n}: casting time")
        if not set(s["components"]) <= {"V", "S", "M"} or not s["components"]: problems.append(f"{n}: components")
        if ("M" in s["components"]) != bool(s["material"]): problems.append(f"{n}: material text")
        if s["concentration"] and s["duration"] == "Instantaneous": problems.append(f"{n}: concentration but instantaneous")
        if not s["classes"] or not set(s["classes"]) <= cl: problems.append(f"{n}: classes")
        if re.search("[—–]", json.dumps(s, ensure_ascii=False)): problems.append(f"{n}: dash")
        if os.path.basename(p)[:-5] != re.sub(r"[^a-z0-9]+", "-", n.lower().replace("'", "")).strip("-"): problems.append(f"{n}: file name")
    check("Spell files are well formed", not problems, "; ".join(problems[:5]))
    used = {e[0] for k, (s, spec) in spells.items() for e in spec["lines"]}
    check("Unused price items (kept for builders, informational)", True, ", ".join(sorted(i for i in P.ITEMS if i not in used)) or "none")
    check("Unused limits (kept for builders, informational)", True, ", ".join(sorted(l for l in P.LIMITS if l not in used)) or "none")

    width = max(len(r[0]) for r in results)
    for name, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")
    fails = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(fails)} of {len(results)} checks passed")
    return results
