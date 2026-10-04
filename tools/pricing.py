"""Pricing tables and scoring for the spell point-buy system.

Price of an item = base price x category multiplier x a convex shape for amounts. Multipliers, the
convexity exponent, per-effect prices for single-use items, and the level budgets come from
data/calibration.json, which tools/fit.py writes.

There are no caps, item levels, floors, or ceilings. A spell is limited only by what its parts cost
against the budget for its level. Only a spell's base-slot power is priced. Upcasting and cantrip
scaling are not part of the cost.
"""
import json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL_PATH = os.path.join(ROOT, "data", "calibration.json")

EXP = 0.4                       # convexity: price grows with magnitude^(1+EXP). fit.py fits it
REFUND_CAP = 0.40               # all refunds together (limits, components, concentration, class lists, slow casting) may not exceed this share of the effect cost. Canon spells at level 1 and up: median 18%, 95th percentile 37%
LEVEL_SCALE = True              # delivery, refunds, and limits are priced as a share of the level budget, so they grow with level
MODE_SHARE = 0.25               # a spell with several modes pays full price for the best one and this share of each other
DURATION_REF = 40               # effects at or above this pay full duration price; weaker effects pay down to half
EFFECT_CATS = {"dmg", "heal", "buff", "cond", "util", "area"}

# id: (label, base price, unit, convex reference or None, category, tier)
# tier 0 = usable by cantrips and above, 1 = level 1 and above, 2 = level 2 and above
def _i(label, base, cat, tier, unit="flat", ref=None):
    return (label, base, unit, ref, cat, tier)

def _area(label, sqft, tier):
    """Area price follows the square root of the footprint, so a bigger area never costs less."""
    return (label, round(0.9 * math.sqrt(sqft), 1), "flat", None, "area", tier)

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
    "c_dmg":          _i("Cantrip damage (average 6.5 or less)", 2.4, "dmg", 0, "per avg damage", 5.5),
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
    "cond_asleep":     _i("Asleep (wakes on damage or a shake)", 48, "cond", 1),
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
    "util_mark_track": _i("Advantage to track a marked target", 6, "util", 1),
    "util_mark_move":  _i("Move effect to a new target", 3, "util", 1),
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
    # level 3 effects
    "cond_slow":       _i("Slowed: half speed, -2 AC and Dex saves, no reactions, one action", 55, "cond", 3),
    "cond_terror":     _i("Frightened, drops what it holds, must flee", 90, "cond", 3),
    "cond_charm_incap": _i("Charmed, incapacitated, speed 0", 90, "cond", 3),
    "cond_curse":      _i("Cursed: disadvantage, lost actions, or extra damage", 75, "cond", 3),
    "cond_retch":      _i("Spends its action retching", 60, "cond", 3),
    "cond_halfspeed":  _i("Speed halved", 25, "cond", 3),
    "haste":           _i("Doubled speed, +2 AC, advantage on Dex saves, extra action", 140, "buff", 3),
    "fly":             _i("Fly speed 60 ft", 95, "buff", 3),
    "blink":           _i("Vanish to the Ethereal Plane on half of turns", 90, "buff", 3),
    "gas_form":        _i("Gaseous form: flies, resists nonmagical damage, cannot attack", 80, "buff", 3),
    "feign":           _i("Appear dead and resist damage", 60, "buff", 3),
    "meld":            _i("Merge into stone and hide", 70, "buff", 3),
    "resist_energy":   _i("Resistance to one damage type", 70, "buff", 3),
    "beacon":          _i("Advantage on Wisdom and death saves, maximum healing received", 70, "buff", 3),
    "circle":          _i("Barrier that keeps out six creature types", 90, "buff", 3),
    "group10":         _i("Applies to up to ten willing creatures", 30, "buff", 3),
    "util_summon_undead": _i("Raise a skeleton or zombie that obeys you", 110, "util", 3),
    "util_summon_animals": _i("Summon fey spirits as beasts that fight for you", 140, "util", 3),
    "util_scry":       _i("See and hear a distant place", 90, "util", 3),
    "util_counter":    _i("Stop a spell as it is cast", 100, "util", 3),
    "util_food_water": _i("Food and water for fifteen creatures", 60, "util", 3),
    "util_daylight":   _i("Bright daylight over a wide area", 70, "util", 3),
    "util_dispel":     _i("End a spell on a target", 100, "util", 3),
    "util_glyph":      _i("Hidden rune that triggers on a condition", 40, "util", 3),
    "util_shelter":    _i("Sealed dome shelter for hours", 80, "util", 3),
    "util_major_image": _i("Illusion with sound, smell, and temperature", 70, "util", 3),
    "util_nondetect":  _i("Hide from divination and scrying", 50, "util", 3),
    "util_steed":      _i("Summon a fast riding steed", 70, "util", 3),
    "util_plant":      _i("Overgrow plants into a thicket", 25, "util", 3),
    "util_uncurse":    _i("End a curse or attunement to a cursed item", 70, "util", 3),
    "util_revive":     _i("Return a recently dead creature to life", 140, "util", 3),
    "util_sending":    _i("Send a short message to anyone you know", 60, "util", 3),
    "util_speak_dead": _i("A corpse answers five questions", 60, "util", 3),
    "util_speak_plants": _i("Talk with plants and command them", 40, "util", 3),
    "util_tongues":    _i("Understand and speak any language", 60, "util", 3),
    "util_lifesteal":  _i("Regain half the damage dealt", 30, "util", 3),
    "util_water_breathing": _i("Breathe underwater", 40, "util", 3),
    "util_water_walk": _i("Walk on liquid surfaces", 30, "util", 3),
    "util_wind_wall":  _i("Wall of wind that stops missiles, gas, and flyers", 55, "util", 3),
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
    # targets and areas
    "target_extra":    _i("Each additional target (a share of the per-target effects)", 0, "area", 0, "per extra target"),
    "split_targets":   _i("Split effect among several targets", 10, "area", 1),
    "area_cube5":      _area("5 ft cube", 25, 0),
    "area_radius5":    _area("5 ft radius", 79, 2),
    "area_square10":   _area("10 ft square", 100, 1),
    "area_cone15":     _area("15 ft cone", 112, 1),
    "area_cube15":     _area("15 ft cube", 225, 1),
    "area_radius10":   _area("10 ft radius", 314, 2),
    "area_square20":   _area("20 ft square", 400, 1),
    "area_cube20":     _area("20 ft cube", 400, 1),
    "area_line60":     _area("60 ft line", 600, 2),
    "area_radius15":   _area("15 ft radius", 707, 2),
    "area_radius20":   _area("20 ft radius", 1257, 1),
    "area_radius30":   _area("30 ft radius", 2827, 1),
    "area_cone30":     _area("30 ft cone", 450, 3),
    "area_line100":    _area("100 ft line", 500, 3),
    "area_cube30":     _area("30 ft cube", 900, 3),
    "area_cube40":     _area("40 ft cube", 1600, 3),
    "area_radius40":   _area("40 ft radius", 5027, 3),
}
# Extra targets cost a share of what the spell already charges per target. The share depends on the
# kind of effect: an extra enemy hit by damage or control is worth more than an extra ally healed.
TARGET_SHARE = {"dmg": 0.7, "heal": 0.25, "buff": 0.5, "cond": 0.6, "util": 0.5}  # util counts only when the spell has no area
C_RIDERS = {"c_slow10", "c_no_heal", "c_no_reactions", "c_disadv_next", "c_ignore_cover"}
NOT_PER_TARGET = {"difficult_terrain", "heavy_obscure", "util_outline", "util_ignite", "util_wind", "util_hidden"}

# Items counted toward the control cap (strong conditions).
CONTROL = {"cond_prone", "cond_charmed", "cond_frightened", "cond_blinded", "cond_restrained",
           "cond_incapacitated", "cond_asleep", "cond_command", "cond_paralyzed",
           "cond_enfeeble", "cond_suggestion", "cond_crown", "cond_slow", "cond_terror", "cond_charm_incap",
           "cond_curse", "cond_retch", "cond_halfspeed"}

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
    "lim_backlash":       ("Target suffers when the spell ends", -15),
}

CASTING = [("1 action", 0), ("1 bonus action", 8), ("1 reaction", 10), ("1 minute", -4), ("10 minutes", -8), ("1 hour", -12)]
RANGE = {"Self": 0, "Touch": 0, "10 feet": 2, "30 feet": 3, "60 feet": 5, "90 feet": 7, "120 feet": 8, "150 feet": 9, "1 mile": 14, "Unlimited": 18}
DURATION = {"Instantaneous": 0, "1 round": 3, "1 minute": 10, "10 minutes": 16, "1 hour": 22,
            "8 hours": 28, "24 hours": 32, "10 days": 36, "Until dispelled": 40}
CONC = -10
RITUAL = 5
COMP = {"V": -2, "S": -2, "M": -3}
GP_TIERS = [(10, -8), (50, -12), (100, -18), (250, -22), (10**9, -26)]
CONSUMED_MULT = 1.5
CLASS_AVAIL = [(1, -4), (3, -2), (5, 0), (99, 3)]

# multiplier groups: item categories plus the delivery and refund groups
CATS = ["dmg", "heal", "buff", "cond", "util", "area", "range", "cast", "dur", "comp", "limit", "conc", "extra", "avail"]
DEFAULTS = {"mult": {c: 1.0 for c in CATS}, "exp": 0.4, "budgets": {"0": 25, "1": 100, "2": 150, "3": 250}, "item_base": {}}
MULT = dict(DEFAULTS["mult"])
BUDGETS = {0: 25, 1: 100, 2: 150, 3: 250}
ITEM_BASE = {}                  # fitted base prices for items that only one spell uses

def load_calibration(path=CAL_PATH):
    global EXP, BUDGETS
    cal = DEFAULTS
    if os.path.exists(path):
        cal = json.load(open(path))
    MULT.update(cal["mult"])
    EXP = cal.get("exp", 0.4)
    BUDGETS = {int(k): v for k, v in cal["budgets"].items()}
    ITEM_BASE.clear(); ITEM_BASE.update(cal.get("item_base", {}))
load_calibration()

def base_of(item):
    return ITEM_BASE.get(item, ITEMS[item][1])

def price(item, q=1):
    label, base, unit, ref, cat, tier = ITEMS[item]
    base = base_of(item)
    m = MULT[cat]
    if ref:
        return base * q * (q / ref) ** EXP * m
    if unit == "flat":
        return base * m
    return base * q * m

def lookup(prefixes, text):
    for k, v in prefixes:
        if text.startswith(k):
            return v
    raise KeyError(text)

def gp_refund(gp, consumed):
    for cap, v in GP_TIERS:
        if gp <= cap:
            return v * (CONSUMED_MULT if consumed else 1) * MULT["comp"]

def eprice(entry):
    """Price of a line (item, quantity) or (item, quantity, scale). A scale below 1 prices a weaker version of
    an effect, for example Dispel Magic that only ends spells of 1st level or lower."""
    item, q = entry[0], entry[1]
    return price(item, q) * (entry[2] if len(entry) > 2 else 1.0)

def per_target_share(spec):
    """Price of one extra target: a share of every per-target line the spell already pays for."""
    total = 0.0
    has_area = any(i in ITEMS and ITEMS[i][4] == "area" and i not in ("target_extra", "split_targets") for i, v in spec["lines"])
    for entry in spec["lines"]:
        item = entry[0]
        if item in ITEMS and item != "target_extra" and item not in NOT_PER_TARGET:
            cat = ITEMS[item][4]
            if cat == "util" and has_area:
                continue
            if cat in TARGET_SHARE:
                total += eprice(entry) * TARGET_SHARE[cat]
    return total

def score(spec, enforce=True):
    """Returns (rows, total). rows are (type, label, points). A spell is only limited by its price: this
    raises an error for an unknown name or a limit listed twice, and for nothing else.
    Only the spell's base-slot power is priced. A listed upcast or cantrip scaling adds nothing."""
    level = spec.get("level", 1)
    rows = []
    def add(cat, label, pts):
        rows.append((cat, label, round(pts, 1)))
    effect_total = 0
    extra_targets = 0
    lines = list(spec["lines"])
    alt_modes = []
    modes = spec.get("modes")
    if modes:
        sums = [sum(eprice(e) for e in m if e[0] in ITEMS) for m in modes]
        best = max(range(len(modes)), key=lambda k: sums[k])
        lines += list(modes[best])
        alt_modes = [m for k, m in enumerate(modes) if k != best]
    spec = dict(spec, lines=lines)
    seen = [e[0] for e in lines if e[0] in LIMITS]
    dup = sorted({i for i in seen if seen.count(i) > 1})
    if dup:
        raise ValueError(f"limit {', '.join(dup)} claimed more than once")
    for entry in lines:
        item, q = entry[0], entry[1]
        if item in ITEMS:
            label, base, unit, ref, cat, tier = ITEMS[item]
            if item == "target_extra":
                extra_targets += q
                continue
            cost = eprice(entry)
            qs = ("" if unit == "flat" else f" x{q:g}") + (f" at {entry[2]:.0%} strength" if len(entry) > 2 and entry[2] != 1 else "")
            if cat in EFFECT_CATS:
                effect_total += cost
            add("Effect", label + qs, cost)
        elif item in LIMITS:
            add("Limit", LIMITS[item][0], LIMITS[item][1] * MULT["limit"])
        else:
            raise KeyError(item)
    for m in alt_modes:
        for entry in m:
            item, q = entry[0], entry[1]
            if item not in ITEMS:
                raise KeyError(item)
            label, base, unit, ref, cat, tier = ITEMS[item]
            cost = eprice(entry) * MODE_SHARE
            qs = ("" if unit == "flat" else f" x{q:g}") + (f" at {entry[2]:.0%} strength" if len(entry) > 2 and entry[2] != 1 else "")
            if cat in EFFECT_CATS:
                effect_total += cost
            add("Effect", f"Alternate mode: {label}{qs}", cost)
    if extra_targets:
        cost = per_target_share(spec) * extra_targets
        if cost <= 0:
            raise ValueError("extra targets need a per-target effect to extend (area spells already hit everyone inside)")
        effect_total += cost
        add("Effect", f"Additional targets x{extra_targets:g}", cost)
    ls = LEVEL_SCALE and BUDGETS.get(level, 100) / 100.0 or 1.0   # everything that is not an effect scales with the level budget
    for r_i, r in enumerate(rows):
        if r[0] == "Limit":
            rows[r_i] = (r[0], r[1], round(r[2] * ls, 1))
    priced = spec.get("price_range", spec["range"])
    r = priced.split(" (")[0]
    label = f"Range: {spec['range']}" + (f", attack reaches {priced}" if priced != spec["range"] else "")
    add("Delivery", label, RANGE[r] * MULT["range"] * ls)
    add("Delivery", f"Casting time: {spec['casting_time'].split(',')[0]}", lookup(CASTING, spec["casting_time"]) * MULT["cast"] * ls)
    dur_factor = 0.5 + 0.5 * min(1.0, effect_total / DURATION_REF)
    dlabel = f"Duration: {spec['duration']}" + (f" (x{dur_factor:.2f} for a weak effect)" if dur_factor < 0.995 else "")
    add("Duration", dlabel, DURATION[spec["duration"]] * MULT["dur"] * dur_factor * ls)
    if spec["concentration"]:
        add("Refund", "Concentration", CONC * MULT["conc"] * ls)
    if spec["ritual"]:
        add("Delivery", "Ritual casting", RITUAL * MULT["extra"] * ls)
    for c in spec["components"]:
        if c == "M":
            gp = spec.get("material_gp", 0)
            if gp:
                tag = ", consumed" if spec.get("consumed") else ""
                add("Refund", f"Material worth {gp} gp{tag}", gp_refund(gp, spec.get("consumed")) * ls)
            else:
                add("Refund", "Material component (no cost)", COMP["M"] * MULT["comp"] * ls)
        else:
            add("Refund", f"{c} component", COMP[c] * MULT["comp"] * ls)
    n = spec["class_count"]
    add("Availability", f"On {n} class list{'s' if n != 1 else ''}", next(v for k, v in CLASS_AVAIL if n <= k) * MULT["avail"] * ls)
    neg = -sum(r[2] for r in rows if r[2] < 0)
    cap = REFUND_CAP * effect_total
    if neg > cap:
        add("Cap", f"Refunds capped at {int(REFUND_CAP * 100)}% of effect cost", neg - cap)
    return rows, round(sum(r[2] for r in rows), 1)
