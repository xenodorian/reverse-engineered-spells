"""Pricing tables and scoring for the spell point-buy system.

Price of an item = base price x category multiplier. Multipliers, level budgets, floors, and
magnitude caps come from data/calibration.json, which tools/fit.py writes. Without that file,
every multiplier is 1 and the L2 values are placeholders.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL_PATH = os.path.join(ROOT, "data", "calibration.json")

EXP = 0.4                       # convexity: price grows with magnitude^(1+EXP)
L1_FLOOR = 50                   # a level 1 spell's effects must total at least this
CANTRIP_CEIL = 49               # a cantrip's effects must total less than the L1 floor
LIMIT_CAP = 0.5                 # limit refunds may not exceed this share of the effect cost
UPCAST_SHARE = 0.5              # an upcast increment costs this share of buying it outright
UPCAST_MAX = 1.0                # increase per slot level, as a share of the base amount (damage, healing, temp HP)
UPCAST_TARGETS = 1              # extra targets per slot level
EFFECT_CATS = {"dmg", "heal", "buff", "cond", "util", "area"}

# id: (label, base price, unit, convex reference or None, category, tier)
# tier 0 = usable by cantrips and above, 1 = level 1 and above, 2 = level 2 and above
def _i(label, base, cat, tier, unit="flat", ref=None):
    return (label, base, unit, ref, cat, tier)

ITEMS = {
    # damage and delivery
    "dmg":            _i("Damage dealt", 5, "dmg", 1, "per avg damage", 10.5),
    "dmg_recurring":  _i("Repeat damage on later turns", 5, "dmg", 1, "per avg damage", 10.5),
    "dmg_rider":      _i("Extra damage on each weapon hit", 16, "dmg", 1, "per avg damage", 3.5),
    "zone_damage":    _i("Damage for each 5 ft moved in the area", 6, "dmg", 2, "per avg damage", 5),
    "miss_half":      _i("Half damage on a miss", 8, "dmg", 2),
    "rel_attack":     _i("Delivered by attack roll", 0, "dmg", 0),
    "rel_save_half":  _i("Delivered by save, half on success", 5, "dmg", 1),
    "rel_auto":       _i("Hits automatically", 12, "dmg", 1),
    "c_dmg":          _i("Cantrip damage (average 6.5 or less)", 2.7, "dmg", 0, "per avg damage", 5.5),
    # healing
    "heal":           _i("Hit points restored (modifier assumed +3)", 5, "heal", 1, "per avg HP", 7.5),
    "temp_hp":        _i("Temporary hit points", 4, "heal", 1, "per HP", 6.5),
    "temp_hp_recurring": _i("Temporary hit points renewed each turn", 8, "heal", 1, "per HP per turn"),
    # buffs and debuffs
    "ac_bonus":       _i("Armor Class bonus", 16, "buff", 1, "per +1 AC", 3),
    "die_bonus":      _i("d4 bonus to attacks and saves", 34, "buff", 1, "per target"),
    "advantage_vs_target": _i("Attacks against target have advantage", 29, "buff", 1),
    "advantage_next": _i("Advantage on one next attack", 21, "buff", 1),
    "protect_types":  _i("Disadvantage vs six creature types plus charm and fear immunity", 47, "buff", 1),
    "immune_frightened": _i("Immune to frightened", 10, "buff", 1),
    "speed_bonus":    _i("Walking speed bonus", 2, "buff", 1, "per foot"),
    "extra_dash":     _i("Dash as bonus action each turn", 34, "buff", 1),
    "jump_triple":    _i("Triple jump distance", 8, "buff", 1),
    "fall_immunity":  _i("Negate falling damage and slow fall", 16, "buff", 1),
    "magic_missile_immune": _i("Immune to one named spell", 5, "buff", 1),
    "blur":           _i("Attackers have disadvantage against you", 75, "buff", 2),
    "invisible":      _i("Invisible until you attack or cast", 100, "buff", 2),
    "mirror":         _i("Three duplicates that absorb attacks", 80, "buff", 2),
    "teleport":       _i("Teleport up to 30 ft", 55, "buff", 2),
    "magic_weapon":   _i("Weapon becomes magical, +1 to hit and damage", 55, "buff", 2),
    "ward_bond":      _i("Resist all damage, +1 AC and saves for one ally", 90, "buff", 2),
    "enhance":        _i("Advantage on one ability's checks plus a perk", 40, "buff", 2),
    "resize":         _i("Grow or shrink a creature with combat benefits", 55, "buff", 2),
    "stealth_aura":   _i("+10 Stealth and untrackable for a group", 60, "buff", 2),
    # conditions and control
    "cond_prone":      _i("Prone", 10, "cond", 1),
    "cond_charmed":    _i("Charmed", 31, "cond", 1),
    "cond_frightened": _i("Frightened", 31, "cond", 1),
    "cond_blinded":    _i("Blinded", 31, "cond", 1),
    "cond_restrained": _i("Restrained", 36, "cond", 1),
    "cond_incapacitated": _i("Incapacitated", 72, "cond", 1),
    "cond_unconscious": _i("Unconscious", 48, "cond", 1),
    "cond_command":    _i("Forced to obey a one word order", 29, "cond", 1),
    "cond_paralyzed":  _i("Paralyzed", 95, "cond", 2),
    "cond_enfeeble":   _i("Strength weapon damage halved", 40, "cond", 2),
    "cond_suggestion": _i("Follows a reasonable suggestion", 70, "cond", 2),
    "cond_crown":      _i("Charmed and forced to attack a chosen creature", 80, "cond", 2),
    "no_save":         _i("Condition with no save or roll", 15, "cond", 1),
    "forced_move":     _i("Forced movement", 5, "cond", 1),
    "difficult_terrain": _i("Difficult terrain", 10, "cond", 1),
    "heavy_obscure":   _i("Heavily obscured area", 26, "cond", 1),
    "util_outline":    _i("Outlines target, negates invisibility", 10, "cond", 1),
    "util_ignite":     _i("Ignites loose flammables", 3, "cond", 0),
    "util_wind":       _i("Scatters gas and snuffs flames", 12, "cond", 2),
    "util_hidden":     _i("Hazard is hard to see", 10, "cond", 2),
    # utility
    "util_detect":     _i("Sense a category within 30 ft", 26, "util", 1),
    "util_detect_aura": _i("Learn aura or school of what you sense", 10, "util", 1),
    "util_lore":       _i("Reveal properties or lore", 33, "util", 1, "per item"),
    "util_language":   _i("Understand any language", 26, "util", 1),
    "util_speak":      _i("Speak with a creature type", 23, "util", 1),
    "util_create_water": _i("Create or destroy water", 13, "util", 1),
    "util_purify":     _i("Purify food and drink", 10, "util", 1),
    "util_food":       _i("Day of food", 13, "util", 1),
    "util_alarm":      _i("Alert when an area is entered", 18, "util", 1),
    "util_ward":       _i("Ward that redirects attackers", 47, "util", 1),
    "util_illusion_image": _i("Create a visual illusion", 47, "util", 1),
    "util_disguise":   _i("Change your appearance", 47, "util", 1),
    "util_script":     _i("Hidden writing", 26, "util", 1),
    "util_servant":    _i("Invisible helper that does chores", 42, "util", 1),
    "util_familiar":   _i("Summon a loyal scout and helper", 52, "util", 1),
    "util_mark_track": _i("Advantage to track a marked target", 8, "util", 1),
    "util_mark_move":  _i("Move effect to a new target", 5, "util", 1),
    "persist":         _i("Effect lasts until dismissed", 16, "util", 1),
    "util_alter_self": _i("Reshape your body: gills, new face, or claws", 55, "util", 2),
    "util_messenger":  _i("Tiny beast carries a message", 30, "util", 2),
    "util_lock":       _i("Magically lock a door or container", 30, "util", 2),
    "util_magic_aura": _i("Falsify what detection magic reads", 30, "util", 2),
    "util_augury":     _i("Learn weal or woe of a plan", 30, "util", 2),
    "util_calm":       _i("Suppress charm and fear or pacify hostility", 60, "util", 2),
    "util_flame":      _i("Permanent heatless flame", 12, "util", 2),
    "util_darkness":   _i("Magical darkness", 45, "util", 2),
    "util_darkvision": _i("Darkvision 60 ft", 26, "util", 2),
    "util_thoughts":   _i("Read surface thoughts or probe a mind", 50, "util", 2),
    "util_enthrall":   _i("Hold attention, others unnoticed", 30, "util", 2),
    "util_find_traps": _i("Sense traps in sight", 26, "util", 2),
    "util_repose":     _i("Preserve a corpse", 26, "util", 2),
    "util_knock":      _i("Open a lock or bar", 30, "util", 2),
    "util_cure":       _i("End a disease or a condition", 50, "util", 2),
    "util_levitate":   _i("Float a creature or object 20 ft", 40, "util", 2),
    "util_locate_life": _i("Locate nearby animals or plants", 30, "util", 2),
    "util_locate":     _i("Locate a familiar or named object", 40, "util", 2),
    "util_mouth":      _i("Stored spoken message with a trigger", 30, "util", 2),
    "util_poison_prot": _i("Neutralize poison, advantage and resistance", 40, "util", 2),
    "util_rope":       _i("Hidden extradimensional refuge for eight", 70, "util", 2),
    "util_see_invis":  _i("See invisible and ethereal", 50, "util", 2),
    "util_climb":      _i("Climb walls and ceilings", 30, "util", 2),
    "util_silence":    _i("Zone with no sound", 60, "util", 2),
    "util_truth":      _i("Creatures cannot speak lies", 50, "util", 2),
    # cantrip-scale effects
    "c_slow10":        _i("Target speed reduced 10 ft until your next turn", 6, "cond", 0),
    "c_no_heal":       _i("Target cannot regain HP until your next turn", 3, "cond", 0),
    "c_no_reactions":  _i("Target cannot take reactions until its next turn", 8, "cond", 0),
    "c_disadv_next":   _i("Target has disadvantage on its next attack roll", 8, "cond", 0),
    "c_adv_self":      _i("Advantage on your next attack against one target", 10, "buff", 0),
    "c_ignore_cover":  _i("Target gets no cover bonus to the save", 3, "cond", 0),
    "c_d4_check":      _i("d4 on one ability check", 14, "buff", 0),
    "c_d4_save":       _i("d4 on one saving throw", 14, "buff", 0),
    "c_light":         _i("Create light", 3, "util", 0),
    "c_lights4":       _i("Four movable lights", 12, "util", 0),
    "c_hand":          _i("Spectral hand, 10 lb, 30 ft", 10, "util", 0),
    "c_mend":          _i("Repair one small break", 12, "util", 0),
    "c_message":       _i("Whispered message to one creature", 8, "util", 0),
    "c_illusion_min":  _i("Small image or sound", 10, "util", 0),
    "c_trick":         _i("Several minor magical tricks", 5, "util", 0),
    "c_nature":        _i("Minor nature effects", 14, "util", 0),
    "c_wonder":        _i("Minor wonders", 10, "util", 0),
    "c_stabilize":     _i("Stabilize a dying creature", 12, "util", 0),
    "c_weapon":        _i("Enchant a club or staff (spell modifier, d8, magical)", 13, "buff", 0),
    "c_throw":         _i("Hurl the effect 30 ft", 2, "util", 0),
    # targets and areas
    "target_extra":    _i("Each additional target", 10, "area", 0, "per extra target", 2),
    "split_targets":   _i("Split effect among several targets", 10, "area", 1),
    "area_cube5":      _i("5 ft cube", 4, "area", 0),
    "area_radius5":    _i("5 ft radius", 8, "area", 2),
    "area_square10":   _i("10 ft square", 13, "area", 1),
    "area_radius10":   _i("10 ft radius", 20, "area", 2),
    "area_cone15":     _i("15 ft cone", 18, "area", 1),
    "area_cube15":     _i("15 ft cube", 18, "area", 1),
    "area_radius15":   _i("15 ft radius", 28, "area", 2),
    "area_square20":   _i("20 ft square", 23, "area", 1),
    "area_cube20":     _i("20 ft cube", 23, "area", 1),
    "area_radius20":   _i("20 ft radius", 26, "area", 1),
    "area_radius30":   _i("30 ft radius", 31, "area", 1),
    "area_line60":     _i("60 ft line", 30, "area", 2),
}
# Items counted toward the control cap (strong conditions).
CONTROL = {"cond_prone", "cond_charmed", "cond_frightened", "cond_blinded", "cond_restrained",
           "cond_incapacitated", "cond_unconscious", "cond_command", "cond_paralyzed",
           "cond_enfeeble", "cond_suggestion", "cond_crown"}

# id: (label, refund)   Refunds from limits are negative.
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
    "lim_cosmetic":       ("Cosmetic or trivial effects only", -6),
    "lim_expend":         ("Effect ends when used", -8),
    "lim_range_break":    ("Breaks if the target leaves range", -2),
    "lim_shared_damage":  ("You take the damage the target takes", -14),
}

CASTING = [("1 action", 0), ("1 bonus action", 8), ("1 reaction", 10), ("1 minute", -4), ("10 minutes", -8), ("1 hour", -12)]
RANGE = {"Self": 0, "Touch": 0, "10 feet": 2, "30 feet": 3, "60 feet": 5, "90 feet": 7, "120 feet": 8, "150 feet": 9}
DURATION = {"Instantaneous": 0, "1 round": 3, "1 minute": 10, "10 minutes": 16, "1 hour": 22,
            "8 hours": 28, "24 hours": 32, "10 days": 36, "Until dispelled": 40}
CONC = -10
RITUAL = 5
SCALING = {0: 3, 1: 5, 2: 8}
COMP = {"V": -2, "S": -2, "M": -3}
GP_TIERS = [(10, -8), (50, -12), (100, -18), (250, -22), (10**9, -26)]
CONSUMED_MULT = 1.5
CLASS_AVAIL = [(1, -4), (3, -2), (5, 0), (99, 3)]

# multiplier groups: item categories plus the delivery and refund groups
CATS = ["dmg", "heal", "buff", "cond", "util", "area", "range", "cast", "dur", "comp", "limit", "conc", "extra", "avail"]
DEFAULTS = {
    "mult": {c: 1.0 for c in CATS},
    "budgets": {"0": 25, "1": 100, "2": 200},
    "l2_floor": 100,
    "caps": {},
    "control_cap": {"0": 0, "1": 999, "2": 999},
}
MULT = dict(DEFAULTS["mult"])
BUDGETS = {0: 25, 1: 100, 2: 200}
L2_FLOOR = 100
CAPS = {}
CONTROL_CAP = {0: 0, 1: 999, 2: 999}

def load_calibration(path=CAL_PATH):
    global BUDGETS, L2_FLOOR, CAPS, CONTROL_CAP
    cal = DEFAULTS
    if os.path.exists(path):
        cal = json.load(open(path))
    MULT.update(cal["mult"])
    BUDGETS = {int(k): v for k, v in cal["budgets"].items()}
    L2_FLOOR = cal["l2_floor"]
    CAPS = {k: {int(l): v for l, v in d.items()} for k, d in cal["caps"].items()}
    CONTROL_CAP = {int(k): v for k, v in cal["control_cap"].items()}
load_calibration()

def floor(level):
    return {0: 0, 1: L1_FLOOR, 2: L2_FLOOR}[level]

def ceiling(level):
    return {0: CANTRIP_CEIL, 1: L2_FLOOR - 1, 2: 10**9}[level]

def price(item, q=1):
    label, base, unit, ref, cat, tier = ITEMS[item]
    m = MULT[cat]
    if ref:
        return base * q * (q / ref) ** EXP * m
    if unit == "flat":
        return base * m
    return base * q * m

def cap_for(item, level):
    d = CAPS.get(item)
    if not d:
        return None
    ok = [l for l in d if l <= level]
    return d[max(ok)] if ok else None

def lookup(prefixes, text):
    for k, v in prefixes:
        if text.startswith(k):
            return v
    raise KeyError(text)

def gp_refund(gp, consumed):
    for cap, v in GP_TIERS:
        if gp <= cap:
            return v * (CONSUMED_MULT if consumed else 1) * MULT["comp"]

def score(spec, enforce=True):
    """Returns (rows, total). rows are (type, label, points). With enforce=False the cap and tier
    checks are skipped, which tools/fit.py uses while measuring the existing spells."""
    level = spec.get("level", 1)
    rows = []
    def add(cat, label, pts):
        rows.append((cat, label, round(pts, 1)))
    effect_total = 0
    control_total = 0
    for item, q in spec["lines"]:
        if item in ITEMS:
            label, base, unit, ref, cat, tier = ITEMS[item]
            if enforce:
                if tier > level:
                    raise ValueError(f"{item} is a level {tier} effect and cannot be used in a level {level} spell")
                if unit == "flat" and q != 1:
                    raise ValueError(f"{item} is a flat item and can be taken once")
                split = item == "dmg" and any(i == "split_targets" for i, v in spec["lines"])
                cp = cap_for("dmg_split" if split else item, level)
                if cp is not None and q > cp + 1e-9:
                    raise ValueError(f"{item} is capped at {cp:g} for level {level} spells (you asked for {q:g})")
            cost = price(item, q)
            qs = "" if unit == "flat" else f" x{q:g}"
            if cat in EFFECT_CATS:
                effect_total += cost
            if item in CONTROL:
                control_total += cost
            add("Effect", label + qs, cost)
        elif item in LIMITS:
            add("Limit", LIMITS[item][0], LIMITS[item][1] * MULT["limit"])
        else:
            raise KeyError(item)
    if enforce and control_total > CONTROL_CAP[level] + 1e-9:
        raise ValueError(f"control effects total {control_total:.0f}, over the level {level} control cap of {CONTROL_CAP[level]:g}")
    fl = floor(level)
    if fl and effect_total < fl:
        add("Floor", f"Level {level} effect floor (effects must total {fl})", fl - effect_total)
        effect_total = fl
    if enforce and effect_total > ceiling(level):
        raise ValueError(f"effects total {effect_total:g}, which is level {level + 1} strength (ceiling {ceiling(level):g})")
    limit_sum = sum(r[2] for r in rows if r[0] == "Limit")
    cap = -LIMIT_CAP * effect_total
    if limit_sum < cap:
        add("Cap", f"Limit refunds capped at {int(LIMIT_CAP * 100)}% of effect cost", cap - limit_sum)
    r = spec["range"].split(" (")[0]
    add("Delivery", f"Range: {spec['range']}", RANGE[r] * MULT["range"])
    add("Delivery", f"Casting time: {spec['casting_time'].split(',')[0]}", lookup(CASTING, spec["casting_time"]) * MULT["cast"])
    add("Duration", f"Duration: {spec['duration']}", DURATION[spec["duration"]] * MULT["dur"])
    if spec["concentration"]:
        add("Refund", "Concentration", CONC * MULT["conc"])
    if spec["ritual"]:
        add("Delivery", "Ritual casting", RITUAL * MULT["extra"])
    if spec["scaling"]:
        up = spec.get("upcast")
        if up and level >= 1:
            item, inc = up
            base_q = sum(q for i, q in spec["lines"] if i == item)
            if enforce:
                if item == "target_extra":
                    if inc > UPCAST_TARGETS + 1e-9:
                        raise ValueError(f"upcasting may add at most {UPCAST_TARGETS} target per slot level")
                elif item in ("dmg", "dmg_recurring", "heal", "temp_hp"):
                    if base_q and inc > UPCAST_MAX * base_q + 1e-9:
                        raise ValueError(f"upcast increase {inc:g} is over {int(UPCAST_MAX * 100)}% of the base {base_q:g} per slot level")
                else:
                    raise ValueError(f"{item} cannot be an upcast increase")
            add("Delivery", f"Upcasting: +{inc:g} {ITEMS[item][0].lower()} per slot level", price(item, inc) * UPCAST_SHARE * MULT["extra"])
        else:
            add("Delivery", "Scales with level" if level == 0 else "Scales with higher slots", SCALING[level] * MULT["extra"])
    for c in spec["components"]:
        if c == "M":
            gp = spec.get("material_gp", 0)
            if gp:
                tag = ", consumed" if spec.get("consumed") else ""
                add("Refund", f"Material worth {gp} gp{tag}", gp_refund(gp, spec.get("consumed")))
            else:
                add("Refund", "Material component (no cost)", COMP["M"] * MULT["comp"])
        else:
            add("Refund", f"{c} component", COMP[c] * MULT["comp"])
    n = spec["class_count"]
    add("Availability", f"On {n} class list{'s' if n != 1 else ''}", next(v for k, v in CLASS_AVAIL if n <= k) * MULT["avail"])
    return rows, round(sum(r[2] for r in rows), 1)
