"""Logic checks for the point-buy system. Run with: python tools/pointbuy.py check"""
import copy, glob, json, os, re, sys
import pricing as P

AREA_SQFT = {"area_cube5": 25, "area_radius5": 79, "area_square10": 100, "area_cone15": 112, "area_cube15": 225,
             "area_radius10": 314, "area_square20": 400, "area_cube20": 400, "area_line60": 600, "area_radius15": 707,
             "area_radius20": 1257, "area_radius30": 2827}
SEVERITY = ["cond_prone", "cond_blinded", "cond_restrained", "cond_asleep", "cond_incapacitated", "cond_paralyzed"]

def run(spells):
    results = []
    def check(name, ok, detail=""):
        results.append((name, bool(ok), detail))

    # 1. every spell legal under every rule
    bad = []
    for k, (s, spec) in spells.items():
        try:
            rows, t = P.score(spec)
            if t > P.BUDGETS[spec["level"]] + 1e-9:
                bad.append(f"{s['name']} {t:.1f}")
        except ValueError as e:
            bad.append(f"{s['name']}: {e}")
    check("Every spell is legal under every rule", not bad, "; ".join(bad[:5]))

    # 2. clearance bands
    eff = {0: [], 1: [], 2: []}
    nets = {0: [], 1: [], 2: []}
    for k, (s, spec) in spells.items():
        rows, t = P.score(spec)
        eff[spec["level"]].append(sum(r[2] for r in rows if r[0] in ("Effect", "Floor")))
        nets[spec["level"]].append(t)
    check("Cantrip effects stay under the level 1 floor", max(eff[0]) < P.L1_FLOOR, f"max {max(eff[0]):.1f}")
    check("Level 1 effects sit between the floors", min(eff[1]) >= P.L1_FLOOR - 0.2 and max(eff[1]) < P.L2_FLOOR, f"{min(eff[1]):.1f} to {max(eff[1]):.1f}")
    check("Level 2 effects are at or above the level 2 floor", min(eff[2]) >= P.L2_FLOOR - 0.2, f"min {min(eff[2]):.1f}")
    check("Budgets rise with level", P.BUDGETS[0] < P.BUDGETS[1] < P.BUDGETS[2])
    mean = {l: sum(v) / len(v) for l, v in nets.items()}
    check("Mean net cost rises with level", mean[0] < mean[1] < mean[2], f"{mean[0]:.1f}, {mean[1]:.1f}, {mean[2]:.1f}")

    # 3. price ordering
    cond = [P.price(c) for c in SEVERITY]
    check("Condition prices follow severity", cond == sorted(cond), ", ".join(f"{c[5:]} {p:.0f}" for c, p in zip(SEVERITY, cond)))
    areas = sorted(AREA_SQFT, key=lambda a: AREA_SQFT[a])
    pr = [P.price(a) for a in areas]
    check("A larger area never costs less", all(pr[i] <= pr[i + 1] + 1e-9 for i in range(len(pr) - 1)))
    for label, table in (("Range", P.RANGE), ("Duration", P.DURATION)):
        vals = list(table.values())
        check(f"{label} prices never fall as the value grows", vals == sorted(vals))
    check("Casting time: longer is cheaper", [v for k, v in P.CASTING if k in ("1 action", "1 minute", "10 minutes", "1 hour")] == sorted([v for k, v in P.CASTING if k in ("1 action", "1 minute", "10 minutes", "1 hour")], reverse=True))
    check("Bonus action and reaction cost more than an action", dict(P.CASTING)["1 bonus action"] > 0 and dict(P.CASTING)["1 reaction"] > 0)
    check("Gold-cost refunds grow with the cost", [v for c, v in P.GP_TIERS] == sorted([v for c, v in P.GP_TIERS], reverse=True))
    check("A material refunds more than V or S, and a gold-cost one more again", abs(P.COMP["M"]) > abs(P.COMP["V"]) and abs(P.GP_TIERS[0][1]) > abs(P.COMP["M"]))
    check("Damage price is convex", P.price("dmg", 20) > 2 * P.price("dmg", 10) - 1e-9)
    check("Cantrip damage costs less than level 1 damage at the same amount", P.price("c_dmg", 5.5) < P.price("dmg", 5.5))

    # 4. tiers: no spell uses an item above its level
    over = [f"{s['name']} uses {i}" for k, (s, spec) in spells.items() for i, q in spec["lines"] if i in P.ITEMS and P.ITEMS[i][5] > spec["level"]]
    check("No spell uses an item above its level", not over, "; ".join(over[:3]))

    # 5. exploit probes
    def legal(spec):
        try:
            P.score(spec); return True
        except ValueError:
            return False
    base = {"level": 1, "casting_time": "1 action", "range": "60 feet", "duration": "Instantaneous", "components": ["V", "S"],
            "concentration": False, "ritual": False, "scaling": False, "class_count": 2}
    check("Probe: 30 average damage at level 1 is rejected", not legal(dict(base, lines=[("dmg", 30), ("rel_attack", 1)])))
    check("Probe: a flat item cannot be stacked by listing it twice", not legal(dict(base, lines=[("cond_charmed", 1), ("cond_charmed", 1)])))
    check("Probe: a limit cannot be claimed twice", not legal(dict(base, lines=[("cond_charmed", 1), ("lim_type", 1), ("lim_type", 1)])))
    check("Probe: a level 2 item is rejected at level 1", not legal(dict(base, lines=[("cond_paralyzed", 1)])))
    check("Probe: extra targets need a per-target effect", not legal(dict(base, lines=[("area_radius20", 1), ("heavy_obscure", 1), ("target_extra", 3)])))
    sp, spec = spells["hold-person"]
    extra = dict(spec, lines=list(spec["lines"]) + [("target_extra", 1)])
    check("Probe: an extra paralyzed target on Hold Person is stopped by the control cap", not legal(extra))
    rows, t1 = P.score(spec)
    rows, t2 = P.score(extra, enforce=False)
    check("Probe: an extra paralyzed target costs a real share of the first", (t2 - t1) > 0.3 * P.price("cond_paralyzed"), f"+{t2 - t1:.1f} against {P.price('cond_paralyzed'):.0f} for the first")

    # 6. data audit
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
        if re.search("[\u2014\u2013]", json.dumps(s, ensure_ascii=False)): problems.append(f"{n}: dash")
        if os.path.basename(p)[:-5] != re.sub(r"[^a-z0-9]+", "-", n.lower().replace("'", "")).strip("-"): problems.append(f"{n}: file name")
    check("Spell files are well formed", not problems, "; ".join(problems[:5]))

    # 7. unused items
    used = {i for k, (s, spec) in spells.items() for i, q in spec["lines"]}
    unused = sorted(i for i in P.ITEMS if i not in used)
    check("Unused price items (kept for builders, informational)", True, ", ".join(unused) or "none")
    unused_l = sorted(l for l in P.LIMITS if l not in used)
    check("Unused limits (kept for builders, informational)", True, ", ".join(unused_l) or "none")

    width = max(len(r[0]) for r in results)
    for name, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")
    fails = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(fails)} of {len(results)} checks passed")
    return results
