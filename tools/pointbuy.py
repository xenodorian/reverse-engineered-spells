#!/usr/bin/env python3
"""Spell point-buy calculator for cantrips, level 1, and level 2 spells.

Usage:
  python tools/pointbuy.py fit               recalibrate prices and write data/calibration.json
  python tools/pointbuy.py report            rewrite the docs and data files
  python tools/pointbuy.py score <slug>      itemized score for one spell, e.g. magic-missile
  python tools/pointbuy.py calc <file.json>  itemized score for a new spell (see examples/)
  python tools/pointbuy.py check             run the logic checks
  python tools/pointbuy.py stress            try to inflate every spell and show what the rules allow

Positive numbers cost points. Negative numbers refund points.
Budgets: cantrip 25, level 1 100, level 2 from data/calibration.json.
"""
import glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pricing as P
import builds as B

ROOT = P.ROOT
FOLDERS = (("cantrip", B.BC), ("level-1", B.B), ("level-2", B.B2))

def load_spells():
    out = {}
    for folder, table in FOLDERS:
        for p in sorted(glob.glob(os.path.join(ROOT, "spells", folder, "*.json"))):
            s = json.load(open(p))
            slug = os.path.basename(p)[:-5]
            lines, gp, cons = table[slug]
            out[slug] = (s, {
                "level": s["level"], "casting_time": s["casting_time"], "range": s["range"], "duration": s["duration"],
                "components": s["components"], "material_gp": gp, "consumed": cons,
                "concentration": s["concentration"], "ritual": s["ritual"],
                "scaling": bool(s["at_higher_levels"]), "class_count": len(s["classes"]), "lines": lines,
                "upcast": B.UPCAST.get(slug), **({"price_range": B.PRICE_RANGE[slug]} if slug in B.PRICE_RANGE else {})})
    return out

def budget(spec):
    return P.BUDGETS[spec.get("level", 1)]

def fmt(rows, total, title, spec):
    w = max(len(r[1]) for r in rows)
    b = budget(spec)
    out = [title + f" (level {spec.get('level', 1)})", "-" * (w + 22)]
    for cat, label, pts in rows:
        out.append(f"{cat:<13}{label:<{w}} {pts:>+7.1f}")
    out.append("-" * (w + 22))
    out.append(f"{'Net cost':<13}{'':<{w}} {total:>7.1f}   (budget {b}, left {b - total:+.1f})")
    return "\n".join(out)

def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    if a[0] == "score" and len(a) == 2:
        sp = load_spells()[a[1]]
        rows, t = P.score(sp[1], enforce=False); print(fmt(rows, t, sp[0]["name"], sp[1]))
    elif a[0] == "calc" and len(a) == 2:
        spec = json.load(open(a[1])); spec.setdefault("lines", [])
        spec["lines"] = [tuple(x) if len(x) == 2 else (x[0], 1) for x in spec["lines"]]
        if spec.get("upcast"):
            spec["upcast"] = tuple(spec["upcast"])
        try:
            rows, t = P.score(spec)
        except ValueError as e:
            print(f"Rejected: {e}"); sys.exit(1)
        print(fmt(rows, t, spec.get("name", "New spell"), spec))
    elif a[0] == "fit":
        import fit; fit.run(load_spells())
    elif a[0] == "report":
        import report; report.write(load_spells())
    elif a[0] == "check":
        import check; res = check.run(load_spells()); sys.exit(0 if all(r[1] for r in res) else 1)
    elif a[0] == "stress":
        import stress; stress.run(load_spells())
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
