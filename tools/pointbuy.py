#!/usr/bin/env python3
"""Spell point-buy calculator for the 1st-level spell set in this repo.

Usage:
  python tools/pointbuy.py report            rewrite docs/spell-point-buy.md and data/point-buy.json
  python tools/pointbuy.py score <slug>      itemized score for one spell, e.g. magic-missile
  python tools/pointbuy.py calc <file.json>  itemized score for a new spell (see examples/new-spell.json)

Positive numbers cost points. Negative numbers refund points. Budget is 100.
"""
import glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUDGET = 100

# ---- Effect costs: id -> (label, points, unit). unit "flat" or text for per-unit cost.
EFFECTS = {
    # damage and healing
    "dmg":            ("Damage dealt", 5, "per avg damage"),
    "dmg_rider":      ("Extra damage on each weapon hit", 16, "per avg damage"),
    "dmg_recurring":  ("Repeat damage on later turns", 5, "per avg damage"),
    "heal":           ("Hit points restored (modifier assumed +3)", 5, "per avg HP"),
    "temp_hp":        ("Temporary hit points", 4, "per HP"),
    "temp_hp_recurring": ("Temporary hit points renewed each turn", 8, "per HP per turn"),
    # reliability of a damaging effect
    "rel_attack":     ("Delivered by attack roll", 0, "flat"),
    "rel_save_half":  ("Delivered by save, half on success", 5, "flat"),
    "rel_auto":       ("Hits automatically", 12, "flat"),
    "no_save":        ("Condition with no save or roll", 15, "flat"),
    # offense, defense, movement
    "ac_bonus":       ("Armor Class bonus", 16, "per +1 AC"),
    "die_bonus":      ("d4 bonus to attacks and saves", 34, "per target"),
    "advantage_vs_target": ("Attacks against target have advantage", 29, "flat"),
    "advantage_next": ("Advantage on one next attack", 21, "flat"),
    "protect_types":  ("Disadvantage vs six creature types plus charm and fear immunity", 47, "flat"),
    "immune_frightened": ("Immune to frightened", 10, "flat"),
    "speed_bonus":    ("Walking speed bonus", 2, "per foot"),
    "extra_dash":     ("Dash as bonus action each turn", 34, "flat"),
    "jump_triple":    ("Triple jump distance", 8, "flat"),
    "fall_immunity":  ("Negate falling damage and slow fall", 16, "flat"),
    "magic_missile_immune": ("Immune to one named spell", 5, "flat"),
    # conditions, per target on a failed save
    "cond_prone":      ("Prone", 10, "flat"),
    "cond_charmed":    ("Charmed", 31, "flat"),
    "cond_frightened": ("Frightened", 31, "flat"),
    "cond_blinded":    ("Blinded", 31, "flat"),
    "cond_restrained": ("Restrained", 36, "flat"),
    "cond_incapacitated": ("Incapacitated", 42, "flat"),
    "cond_unconscious": ("Unconscious", 52, "flat"),
    "cond_command":    ("Forced to obey a one word order", 29, "flat"),
    "forced_move":     ("Forced movement up to 10 ft", 5, "flat"),
    "difficult_terrain": ("Difficult terrain", 10, "flat"),
    "heavy_obscure":   ("Heavily obscured area", 26, "flat"),
    "util_outline":    ("Outlines target, negates invisibility", 10, "flat"),
    "util_ignite":     ("Ignites loose flammables", 3, "flat"),
    # utility
    "util_detect":     ("Sense a category within 30 ft", 26, "flat"),
    "util_detect_aura": ("Learn aura or school of what you sense", 10, "flat"),
    "util_lore":       ("Reveal properties or lore", 21, "per item"),
    "util_language":   ("Understand any language", 26, "flat"),
    "util_speak":      ("Speak with a creature type", 23, "flat"),
    "util_create_water": ("Create or destroy water", 13, "flat"),
    "util_purify":     ("Purify food and drink", 10, "flat"),
    "util_food":       ("Day of food", 13, "flat"),
    "util_alarm":      ("Alert when an area is entered", 18, "flat"),
    "util_ward":       ("Ward that redirects attackers", 47, "flat"),
    "util_illusion_image": ("Create a visual illusion", 47, "flat"),
    "util_disguise":   ("Change your appearance", 47, "flat"),
    "util_script":     ("Hidden writing", 26, "flat"),
    "util_servant":    ("Invisible helper that does chores", 42, "flat"),
    "util_familiar":   ("Summon a loyal scout and helper", 73, "flat"),
    "util_mark_track": ("Advantage to track a marked target", 8, "flat"),
    "util_mark_move":  ("Move effect to a new target", 5, "flat"),
    "persist":         ("Effect lasts until dismissed", 21, "flat"),
    # targeting extras
    "target_extra":    ("Each additional target", 10, "per target"),
    "split_targets":   ("Split effect among several targets", 10, "flat"),
    # areas
    "area_square10":   ("10 ft square", 13, "flat"),
    "area_square20":   ("20 ft square", 23, "flat"),
    "area_cone15":     ("15 ft cone", 18, "flat"),
    "area_cube15":     ("15 ft cube", 18, "flat"),
    "area_cube20":     ("20 ft cube", 23, "flat"),
    "area_radius20":   ("20 ft radius", 26, "flat"),
    "area_radius30":   ("30 ft radius", 31, "flat"),
}

# ---- Refunds from limits. Negative numbers refund points.
LIMITS = {
    "lim_willing":        ("Willing target only", -3),
    "lim_type":           ("Restricted to a creature type or trait", -6),
    "lim_exclude":        ("Excludes a creature type (undead, constructs, low Int)", -2),
    "lim_end_on_harm":    ("Ends if you or allies harm the target", -8),
    "lim_ends_on_attack": ("Ends if the target attacks or casts", -8),
    "lim_wake_on_damage": ("Ends on damage or a shake", -6),
    "lim_repeat_save":    ("Target repeats the save", -6),
    "lim_save_adv":       ("Target gets advantage on the save in some cases", -4),
    "lim_aware":          ("Target knows it was affected afterward", -4),
    "lim_escape_check":   ("Target can use an action to escape", -6),
    "lim_hp_pool":        ("Effect capped by a hit point pool", -10),
    "lim_harmless_only":  ("Target refuses harmful orders", -4),
    "lim_trigger":        ("Narrow reaction trigger", -6),
    "lim_fragile":        ("Effect is easy to kill or dispel", -4),
    "lim_decay":          ("Effect decays or expires early", -3),
    "lim_slow_heal":      ("Benefit delivered one piece at a time", -6),
    "lim_no_combat":      ("No direct combat use", -6),
    "lim_physical_reveal": ("Revealed by touch or an Investigation check", -6),
    "lim_armor":          ("Ends if armor is worn", -3),
    "lim_sensory":        ("Limited to one sense", -3),
    "lim_save_negates":   ("Save negates the whole effect", -4),
    "lim_maintain_action": ("Action each turn to keep it going", -8),
    "lim_barrier":        ("Blocked by thin barriers", -3),
    "lim_dm":             ("Result depends on creature reactions", -4),
    "lim_loud":           ("Loud, reveals your position", -2),
    "lim_range_break":    ("Breaks if the target leaves range", -2),
}

CASTING = [("1 action", 0), ("1 bonus action", 8), ("1 reaction", 10), ("1 minute", -4), ("10 minutes", -8), ("1 hour", -12)]
RANGE = {"Self": 0, "Touch": 0, "10 feet": 2, "30 feet": 3, "60 feet": 5, "90 feet": 7, "120 feet": 8}
DURATION = {"Instantaneous": 0, "1 round": 3, "1 minute": 10, "10 minutes": 16, "1 hour": 22,
            "8 hours": 28, "24 hours": 32, "10 days": 36}
CONC = -10
RITUAL = 5
SCALING = 5
COMP = {"V": -2, "S": -2, "M": -3}
# material with a stated gold cost: (max gp, refund)
GP_TIERS = [(10, -8), (50, -12), (100, -18), (250, -22), (10**9, -26)]
CONSUMED_MULT = 1.5
CLASS_AVAIL = [(1, -4), (3, -2), (5, 0), (99, 3)]  # up to N classes

# ---- Builds: effect lines and limits per spell. Everything else is derived from the spell file.
# Format: slug -> (lines, material_gp, consumed)
B = {
 "alarm": ([("util_alarm",1),("area_cube20",1),("lim_no_combat",1)],0,False),
 "animal-friendship": ([("cond_charmed",1),("lim_type",1),("lim_end_on_harm",1)],0,False),
 "bane": ([("die_bonus",3),("lim_save_negates",1)],0,False),
 "bless": ([("die_bonus",3),("lim_willing",1)],0,False),
 "burning-hands": ([("dmg",10.5),("rel_save_half",1),("area_cone15",1),("util_ignite",1)],0,False),
 "charm-person": ([("cond_charmed",1),("lim_type",1),("lim_aware",1),("lim_save_adv",1)],0,False),
 "color-spray": ([("cond_blinded",1),("area_cone15",1),("no_save",1),("lim_hp_pool",1)],0,False),
 "command": ([("cond_command",1),("lim_exclude",1),("lim_harmless_only",1)],0,False),
 "comprehend-languages": ([("util_language",1),("lim_no_combat",1)],0,False),
 "create-or-destroy-water": ([("util_create_water",1),("area_cube20",1),("lim_no_combat",1)],0,False),
 "cure-wounds": ([("heal",7.5),("lim_exclude",1)],0,False),
 "detect-evil-and-good": ([("util_detect",1),("area_radius30",1),("lim_barrier",1)],0,False),
 "detect-magic": ([("util_detect",1),("util_detect_aura",1),("area_radius30",1),("lim_barrier",1)],0,False),
 "detect-poison-and-disease": ([("util_detect",1),("area_radius30",1),("lim_barrier",1)],0,False),
 "disguise-self": ([("util_disguise",1),("lim_physical_reveal",1)],0,False),
 "divine-favor": ([("dmg_rider",2.5)],0,False),
 "entangle": ([("cond_restrained",1),("area_square20",1),("difficult_terrain",1),("lim_escape_check",1)],0,False),
 "expeditious-retreat": ([("extra_dash",1)],0,False),
 "faerie-fire": ([("advantage_vs_target",1),("util_outline",1),("area_cube20",1)],0,False),
 "false-life": ([("temp_hp",6.5)],0,False),
 "feather-fall": ([("fall_immunity",1),("target_extra",4),("lim_trigger",1)],0,False),
 "find-familiar": ([("util_familiar",1),("persist",1)],10,True),
 "fog-cloud": ([("heavy_obscure",1),("area_radius20",1)],0,False),
 "goodberry": ([("heal",10),("util_food",1),("lim_decay",1),("lim_slow_heal",1)],0,False),
 "grease": ([("cond_prone",1),("area_square10",1),("difficult_terrain",1)],0,False),
 "guiding-bolt": ([("dmg",14),("rel_attack",1),("advantage_next",1)],0,False),
 "healing-word": ([("heal",5.5),("lim_exclude",1)],0,False),
 "hellish-rebuke": ([("dmg",11),("rel_save_half",1),("lim_trigger",1)],0,False),
 "heroism": ([("temp_hp_recurring",3),("immune_frightened",1),("lim_willing",1)],0,False),
 "hideous-laughter": ([("cond_prone",1),("cond_incapacitated",1),("lim_repeat_save",1),("lim_exclude",1),("lim_save_adv",1)],0,False),
 "hunters-mark": ([("dmg_rider",3.5),("util_mark_track",1),("util_mark_move",1)],0,False),
 "identify": ([("util_lore",2),("lim_no_combat",1)],100,False),
 "illusory-script": ([("util_script",1),("lim_no_combat",1)],10,False),
 "inflict-wounds": ([("dmg",16.5),("rel_attack",1)],0,False),
 "jump": ([("jump_triple",1)],0,False),
 "longstrider": ([("speed_bonus",10)],0,False),
 "mage-armor": ([("ac_bonus",3),("lim_armor",1),("lim_willing",1)],0,False),
 "magic-missile": ([("dmg",10.5),("rel_auto",1),("split_targets",1)],0,False),
 "protection-from-evil-and-good": ([("protect_types",1),("lim_willing",1)],0,False),
 "purify-food-and-drink": ([("util_purify",1),("lim_no_combat",1)],0,False),
 "sanctuary": ([("util_ward",1),("lim_ends_on_attack",1)],0,False),
 "shield": ([("ac_bonus",5),("magic_missile_immune",1),("lim_trigger",1)],0,False),
 "shield-of-faith": ([("ac_bonus",2)],0,False),
 "silent-image": ([("util_illusion_image",1),("area_cube15",1),("lim_physical_reveal",1),("lim_sensory",1)],0,False),
 "sleep": ([("cond_unconscious",1),("area_radius20",1),("no_save",1),("lim_hp_pool",1),("lim_wake_on_damage",1)],0,False),
 "speak-with-animals": ([("util_speak",1),("lim_dm",1),("lim_no_combat",1)],0,False),
 "thunderwave": ([("dmg",9),("rel_save_half",1),("area_cube15",1),("forced_move",1),("lim_loud",1)],0,False),
 "unseen-servant": ([("util_servant",1),("lim_fragile",1),("lim_no_combat",1)],0,False),
 "witch-bolt": ([("dmg",6.5),("rel_attack",1),("dmg_recurring",6.5),("lim_maintain_action",1),("lim_range_break",1)],0,False),
}

def lookup(prefixes, text):
    for k, v in prefixes:
        if text.startswith(k):
            return v
    raise KeyError(text)

def gp_refund(gp, consumed):
    for cap, v in GP_TIERS:
        if gp <= cap:
            return round(v * (CONSUMED_MULT if consumed else 1))

def score(spec):
    """spec: dict with casting_time, range, duration, components, material_gp, consumed,
    concentration, ritual, scaling, class_count, lines. Returns (rows, total)."""
    rows = []
    def add(cat, label, pts):
        rows.append((cat, label, round(pts, 1)))
    for item, q in spec["lines"]:
        if item in EFFECTS:
            label, pts, unit = EFFECTS[item]
            qs = "" if unit == "flat" else f" x{q:g}"
            add("Effect", label + qs, pts * (1 if unit == "flat" else q))
        elif item in LIMITS:
            add("Limit", LIMITS[item][0], LIMITS[item][1])
        else:
            raise KeyError(item)
    r = spec["range"].split(" (")[0]
    add("Delivery", f"Range: {spec['range']}", RANGE[r])
    ct = lookup(CASTING, spec["casting_time"])
    add("Delivery", f"Casting time: {spec['casting_time'].split(',')[0]}", ct)
    add("Duration", f"Duration: {spec['duration']}", DURATION[spec["duration"]])
    if spec["concentration"]:
        add("Refund", "Concentration", CONC)
    if spec["ritual"]:
        add("Delivery", "Ritual casting", RITUAL)
    if spec["scaling"]:
        add("Delivery", "Scales with higher slots", SCALING)
    for c in spec["components"]:
        if c == "M":
            gp = spec.get("material_gp", 0)
            if gp:
                tag = ", consumed" if spec.get("consumed") else ""
                add("Refund", f"Material worth {gp} gp{tag}", gp_refund(gp, spec.get("consumed")))
            else:
                add("Refund", "Material component (no cost)", COMP["M"])
        else:
            add("Refund", f"{c} component", COMP[c])
    n = spec["class_count"]
    pts = next(v for k, v in CLASS_AVAIL if n <= k)
    add("Availability", f"On {n} class list{'s' if n != 1 else ''}", pts)
    return rows, round(sum(r[2] for r in rows), 1)

def load_spells():
    out = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "spells", "level-1", "*.json"))):
        s = json.load(open(p))
        slug = os.path.basename(p)[:-5]
        lines, gp, cons = B[slug]
        out[slug] = (s, {
            "casting_time": s["casting_time"], "range": s["range"], "duration": s["duration"],
            "components": s["components"], "material_gp": gp, "consumed": cons,
            "concentration": s["concentration"], "ritual": s["ritual"],
            "scaling": bool(s["at_higher_levels"]), "class_count": len(s["classes"]), "lines": lines})
    return out

def fmt(rows, total, title):
    w = max(len(r[1]) for r in rows)
    out = [title, "-" * (w + 22)]
    for cat, label, pts in rows:
        out.append(f"{cat:<13}{label:<{w}} {pts:>+7.1f}")
    out.append("-" * (w + 22))
    out.append(f"{'Net cost':<13}{'':<{w}} {total:>7.1f}   (budget {BUDGET}, left {BUDGET - total:+.1f})")
    return "\n".join(out)

def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    if a[0] == "score" and len(a) == 2:
        sp = load_spells()[a[1]]
        rows, t = score(sp[1]); print(fmt(rows, t, sp[0]["name"]))
    elif a[0] == "calc" and len(a) == 2:
        spec = json.load(open(a[1])); spec.setdefault("lines", [])
        spec["lines"] = [tuple(x) if len(x) == 2 else (x[0], 1) for x in spec["lines"]]
        rows, t = score(spec); print(fmt(rows, t, spec.get("name", "New spell")))
    elif a[0] == "report":
        import report; report.write(load_spells())
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
