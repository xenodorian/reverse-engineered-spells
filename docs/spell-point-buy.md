# Spell Point Buy

A point budget system for building cantrips and spells of levels 1 to 3. A cantrip gets **25 points**, a 1st-level spell **100**, a 2nd-level spell **150**, and a 3rd-level spell **250**. Effects, range, and duration cost points. Components and limits give points back. A spell is legal if it passes every rule below and its net cost is at or under its budget.

> This is a homebrew tool. Prices are my own design, calibrated against the 24 cantrips, 49 level 1 spells, and 53 level 2 spells in `spells/`, with the 43 level 3 spells held out and measured.  They are not official. The spell files were written from memory and are not checked against the books, and the DMG guidance in `docs/creating-a-spell.md` is also from memory. Why the budgets are 150 and 250 at levels 2 and 3, and how the curve was chosen, is in `docs/spell-scaling-analysis.md`. Playtest before trusting any score.

## Budgets and clearances

| Level | Budget | Effects must total | Magnitude caps | Strong conditions total at most |
|---|---|---|---|---|
| Cantrip | 25 | 49 or less | yes | no strong conditions |
| Level 1 | 100 | 50 to 100 | yes | 82 |
| Level 2 | 150 | 100 to 150 | yes | 95 |
| Level 3 | 250 | 150 to 250 | yes | 95 |

"Effects" means the capability lines only: damage, healing, buffs, conditions, utility, targets, and area. Range, casting time, duration, and refunds are not counted.

## Rules

| Rule | What it does |
|---|---|
| Effect floor | A level 1 spell's effects must total at least 50, level 2 at least 100, level 3 at least 150. A smaller total is topped up with a floor line, so anything a level 1 spell does costs 50 or more at its strength, and each later floor equals the previous level's whole budget. |
| Effect ceiling | Cantrip effects must total 49 or less, just under the level 1 floor. From level 1 up, effects cannot exceed the level's budget. |
| Items by level | Each item has a minimum level, shown in the tables. A spell can only use items at or below its level. |
| Magnitude caps | Damage, healing, temporary HP, extra targets, AC, and other scalable items cannot exceed the highest value used at that level in the existing spells, carried up from lower levels. Damage has separate caps for touch spells, area spells, spells that split across targets, and cantrips that add a rider, because those get more or less damage than a plain ranged hit. Spells cast as a bonus action or reaction have their own lower caps for damage and healing. |
| Control cap | Strong conditions (charmed, blinded, restrained, paralyzed, and so on) together cannot cost more than the cap for the level. Extra targets count toward it. |
| Extra targets | Each extra target costs a share of every per-target line the spell already pays for: damage 70%, strong conditions 60%, buffs 50%, utility 50% (only if the spell has no area), healing 25%. A spell with nothing per-target cannot take extra targets, and area spells already hit everyone inside. |
| Convex price | Damage, healing, and AC rise faster than linearly. Price is proportional to amount to the power 1.4, so doubling an amount more than doubles its price. |
| Area price | Price follows the square root of the footprint in square feet, so a larger area never costs less. |
| Duration and weak effects | A cantrip whose effects total under 40 pays between half and all of the duration price, in proportion. A one-hour light is not worth the same as a one-hour invisibility. Level 1 and 2 spells always pay in full because their effects start at the floor. |
| No duplicates | List each item and each limit once. Flat items are taken once. Use the quantity for per-unit items. |
| Limit refund cap | Refunds from limits cannot exceed 50% of the effect cost. |
| Upcasting | List the increase per slot level. It costs 50% of buying that increase outright, and an extra target costs 50% of what a base extra target costs. Extra targets rise by at most 1 per slot level. A damage, healing, or temporary HP increase cannot exceed the base amount per slot level. Scaling in other ways pays a flat charge. |
| Cantrip scaling | A damage cantrip that scales with character level pays 40% of its damage price, so scaling a d10 costs more than scaling a d4. |
| Reach beyond the listed range | A spell that is Self but throws or fires something farther pays for the farther range (Produce Flame hurls 30 feet). |

## How to build a spell in seven steps

1. **Pick the level.** Budgets are cantrip 25, level 1 100, level 2 150, level 3 250.
2. **Pick the effect.** Add the costs from the tables. Multiply per-unit items by their quantity. Check the caps, the control cap, and the floor or ceiling.
3. **Pick delivery.** Add range, casting time, and duration. Add area or extra target costs.
4. **Add upcasting** if the spell scales.
5. **Add components.** Components are refunds. Material components with a gold cost refund the most.
6. **Add limits.** Each caveat that really constrains the spell refunds points, up to the cap. Do not claim a limit that never matters.
7. **Add up.** Net cost = effects + delivery + duration - refunds. Stay at or below budget, then playtest.

Skip the arithmetic with the calculator: `python tools/pointbuy.py calc examples/new-spell.json`. Set `"level"` to 0, 1, or 2. Write quantities as the second value in a line, and an optional `"upcast": ["dmg", 3.5]`.

### Reading a score

| Tier | Net cost | Meaning |
|---|---|---|
| Cantrip | Over 25 | Over budget. |
| Cantrip | 22 to 25 | Premium. Among the strongest spells of the level. |
| Cantrip | 15 to 21 | Standard. |
| Cantrip | Under 15 | Utility or situational. Headroom to spend on range, duration, or targets. |
| Level 1 | Over 100 | Over budget. |
| Level 1 | 90 to 100 | Premium. Among the strongest spells of the level. |
| Level 1 | 60 to 89 | Standard. |
| Level 1 | Under 60 | Utility or situational. Headroom to spend on range, duration, or targets. |
| Level 2 | Over 150 | Over budget. |
| Level 2 | 135 to 150 | Premium. Among the strongest spells of the level. |
| Level 2 | 90 to 134 | Standard. |
| Level 2 | Under 90 | Utility or situational. Headroom to spend on range, duration, or targets. |
| Level 3 | Over 250 | Over budget. |
| Level 3 | 225 to 250 | Premium. Among the strongest spells of the level. |
| Level 3 | 150 to 224 | Standard. |
| Level 3 | Under 150 | Utility or situational. Headroom to spend on range, duration, or targets. |

## What the existing spells show

Counted from the spell files, and used to set the refund sizes below.

| Pattern | Cantrips (24) | Level 1 (49) | Level 2 (53) | Level 3 (43) |
|---|---|---|---|---|
| Verbal component | 22 of 24 | 48 of 49 | 53 of 53 | 41 of 43 |
| Somatic component | 21 of 24 | 44 of 49 | 46 of 53 | 41 of 43 |
| Material component | 7 of 24 | 26 of 49 | 34 of 53 | 26 of 43 |
| Material with a gold cost | 0 of 24 | 3 of 49 | 5 of 53 | 5 of 43 |
| Concentration | 4 of 24 | 17 of 49 | 26 of 53 | 18 of 43 |
| Ritual | 0 of 24 | 10 of 49 | 6 of 53 | 6 of 43 |
| Has an at-higher-levels clause | 10 of 24 | 22 of 49 | 16 of 53 | 16 of 43 |
| Cast as an action | 22 of 24 | 36 of 49 | 46 of 53 | 35 of 43 |
| Cast as a bonus action or reaction | 1 of 24 | 9 of 49 | 4 of 53 | 2 of 43 |
| Cast time of a minute or more | 1 of 24 | 4 of 49 | 3 of 53 | 6 of 43 |
| Instantaneous duration | 11 of 24 | 12 of 49 | 10 of 53 | 10 of 43 |
| Average classes per spell | 2.4 | 2.6 | 2.6 | 2.9 |
| Spells on exactly one class list | 8 of 24 | 9 of 49 | 8 of 53 | 5 of 43 |
| Average net cost, concentration spells | 13 | 75 | 117 | 169 |
| Average net cost, other spells | 18 | 73 | 120 | 174 |
| Average net cost, spells with a material | 17 | 74 | 120 | 173 |
| Average net cost, spells with no material | 18 | 74 | 116 | 171 |

Takeaways: nearly every spell has a verbal component, most have a somatic one, and about half have a material. Materials are common, so a mundane material refunds little. Gold-cost materials are rare and start at level 1, so they refund heavily. Spells with materials do not score higher than spells without in this set, so the data does not by itself show that materials mark stronger spells. The larger refund for gold-cost materials follows the design rule that costly components limit power, not a trend in these files. Concentration spells are the long-duration ones, so the concentration refund offsets part of the duration cost.

## Price tables (points you spend)

Prices are base price times a calibrated category multiplier. "Points" is the price of one use. Items marked with a reference amount use the convex curve, and the price shown is at that reference amount. Use the curve table below for other amounts.

### Damage and delivery

| Item | Points | Unit | Available from |
|---|---|---|---|
| Cantrip damage (average 6.5 or less) | 11.1 | per avg damage (at 5.5) | Cantrip+ |
| Delivered by attack roll | 0 | flat | Cantrip+ |
| Damage dealt | 44.2 | per avg damage (at 10.5) | Level 1+ |
| Repeat damage on later turns | 44.2 | per avg damage (at 10.5) | Level 1+ |
| Extra damage on each weapon hit | 47.1 | per avg damage (at 3.5) | Level 1+ |
| Hits automatically | 10.1 | flat | Level 1+ |
| Delivered by save, half on success | 4.2 | flat | Level 1+ |
| Half damage on a miss | 6.7 | flat | Level 2+ |
| Damage for each 5 ft moved in the area | 25.2 | per avg damage (at 5) | Level 2+ |

### Healing

| Item | Points | Unit | Available from |
|---|---|---|---|
| Hit points restored (modifier assumed +3) | 29.4 | per avg HP (at 7.5) | Level 1+ |
| Temporary hit points | 20.4 | per HP (at 6.5) | Level 1+ |
| Temporary hit points renewed each turn | 6.3 | per HP per turn | Level 1+ |

### Buffs and debuffs

| Item | Points | Unit | Available from |
|---|---|---|---|
| Advantage on your next attack against one target | 8.9 | flat | Cantrip+ |
| d4 on one ability check | 12.5 | flat | Cantrip+ |
| d4 on one saving throw | 12.5 | flat | Cantrip+ |
| Enchant a club or staff (spell modifier, d8, magical) | 11.6 | flat | Cantrip+ |
| Armor Class bonus | 42.9 | per +1 AC (at 3) | Level 1+ |
| Advantage on one next attack | 18.8 | flat | Level 1+ |
| Attacks against target have advantage | 25.9 | flat | Level 1+ |
| d4 bonus to attacks and saves | 30.4 | per target | Level 1+ |
| Dash as bonus action each turn | 30.4 | flat | Level 1+ |
| Negate falling damage and slow fall | 14.3 | flat | Level 1+ |
| Immune to frightened | 8.9 | flat | Level 1+ |
| Triple jump distance | 7.1 | flat | Level 1+ |
| Immune to one named spell | 4.5 | flat | Level 1+ |
| Disadvantage vs six creature types plus charm and fear immunity | 42 | flat | Level 1+ |
| Walking speed bonus | 1.8 | per foot | Level 1+ |
| Attackers have disadvantage against you | 67 | flat | Level 2+ |
| Advantage on one ability's checks plus a perk | 35.7 | flat | Level 2+ |
| Invisible until you attack or cast | 89.3 | flat | Level 2+ |
| Weapon becomes magical, +1 to hit and damage | 49.1 | flat | Level 2+ |
| Three duplicates that absorb attacks | 71.4 | flat | Level 2+ |
| Grow or shrink a creature with combat benefits | 49.1 | flat | Level 2+ |
| +10 Stealth and untrackable for a group | 53.6 | flat | Level 2+ |
| Teleport up to 30 ft | 49.1 | flat | Level 2+ |
| Resist all damage, +1 AC and saves for one ally | 80.4 | flat | Level 2+ |
| Advantage on Wisdom and death saves, maximum healing received | 62.5 | flat | Level 3+ |
| Vanish to the Ethereal Plane on half of turns | 80.4 | flat | Level 3+ |
| Barrier that keeps out six creature types | 80.4 | flat | Level 3+ |
| Appear dead and resist damage | 53.6 | flat | Level 3+ |
| Fly speed 60 ft | 84.8 | flat | Level 3+ |
| Gaseous form: flies, resists nonmagical damage, cannot attack | 71.4 | flat | Level 3+ |
| Applies to up to ten willing creatures | 26.8 | flat | Level 3+ |
| Doubled speed, +2 AC, advantage on Dex saves, extra action | 125 | flat | Level 3+ |
| Merge into stone and hide | 62.5 | flat | Level 3+ |
| Resistance to one damage type | 62.5 | flat | Level 3+ |

### Conditions and control

| Item | Points | Unit | Available from |
|---|---|---|---|
| Target has disadvantage on its next attack roll | 8 | flat | Cantrip+ |
| Target gets no cover bonus to the save | 3 | flat | Cantrip+ |
| Target cannot regain HP until your next turn | 3 | flat | Cantrip+ |
| Target cannot take reactions until its next turn | 8 | flat | Cantrip+ |
| Target speed reduced 10 ft until your next turn | 6 | flat | Cantrip+ |
| Ignites loose flammables | 3 | flat | Cantrip+ |
| Asleep (wakes on damage or a shake) | 48 | flat | Level 1+ |
| Blinded | 31 | flat | Level 1+ |
| Charmed | 31 | flat | Level 1+ |
| Forced to obey a one word order | 29 | flat | Level 1+ |
| Frightened | 31 | flat | Level 1+ |
| Incapacitated | 72 | flat | Level 1+ |
| Prone | 10 | flat | Level 1+ |
| Restrained | 36 | flat | Level 1+ |
| Difficult terrain | 10 | flat | Level 1+ |
| Forced movement | 5 | flat | Level 1+ |
| Heavily obscured area | 26 | flat | Level 1+ |
| Condition with no save or roll | 15 | flat | Level 1+ |
| Outlines target, negates invisibility | 10 | flat | Level 1+ |
| Charmed and forced to attack a chosen creature | 80 | flat | Level 2+ |
| Strength weapon damage halved | 40 | flat | Level 2+ |
| Paralyzed | 95 | flat | Level 2+ |
| Follows a reasonable suggestion | 70 | flat | Level 2+ |
| Hazard is hard to see | 10 | flat | Level 2+ |
| Scatters gas and snuffs flames | 12 | flat | Level 2+ |
| Charmed, incapacitated, speed 0 | 90 | flat | Level 3+ |
| Cursed: disadvantage, lost actions, or extra damage | 75 | flat | Level 3+ |
| Speed halved | 25 | flat | Level 3+ |
| Spends its action retching | 60 | flat | Level 3+ |
| Slowed: half speed, -2 AC and Dex saves, no reactions, one action | 55 | flat | Level 3+ |
| Frightened, drops what it holds, must flee | 90 | flat | Level 3+ |

### Utility

| Item | Points | Unit | Available from |
|---|---|---|---|
| Spectral hand, 10 lb, 30 ft | 13.8 | flat | Cantrip+ |
| Small image or sound | 13.8 | flat | Cantrip+ |
| Create light | 4.1 | flat | Cantrip+ |
| Four movable lights | 16.6 | flat | Cantrip+ |
| Repair one small break | 16.6 | flat | Cantrip+ |
| Whispered message to one creature | 11 | flat | Cantrip+ |
| Minor nature effects | 19.3 | flat | Cantrip+ |
| Stabilize a dying creature | 16.6 | flat | Cantrip+ |
| Several minor magical tricks | 6.9 | flat | Cantrip+ |
| Minor wonders | 13.8 | flat | Cantrip+ |
| Effect lasts until dismissed | 22.1 | flat | Level 1+ |
| Alert when an area is entered | 24.8 | flat | Level 1+ |
| Create or destroy water | 17.9 | flat | Level 1+ |
| Sense a category within 30 ft | 35.9 | flat | Level 1+ |
| Learn aura or school of what you sense | 13.8 | flat | Level 1+ |
| Change your appearance | 64.9 | flat | Level 1+ |
| Summon a loyal scout and helper | 71.8 | flat | Level 1+ |
| Day of food | 17.9 | flat | Level 1+ |
| Create a visual illusion | 64.9 | flat | Level 1+ |
| Understand any language | 35.9 | flat | Level 1+ |
| Reveal properties or lore | 45.5 | per item | Level 1+ |
| Move effect to a new target | 4.1 | flat | Level 1+ |
| Advantage to track a marked target | 8.3 | flat | Level 1+ |
| Purify food and drink | 13.8 | flat | Level 1+ |
| Hidden writing | 35.9 | flat | Level 1+ |
| Invisible helper that does chores | 58 | flat | Level 1+ |
| Speak with a creature type | 31.7 | flat | Level 1+ |
| Ward that redirects attackers | 64.9 | flat | Level 1+ |
| Reshape your body: gills, new face, or claws | 75.9 | flat | Level 2+ |
| Learn weal or woe of a plan | 41.4 | flat | Level 2+ |
| Suppress charm and fear or pacify hostility | 82.8 | flat | Level 2+ |
| Climb walls and ceilings | 41.4 | flat | Level 2+ |
| End a disease or a condition | 69 | flat | Level 2+ |
| Magical darkness | 62.1 | flat | Level 2+ |
| Darkvision 60 ft | 35.9 | flat | Level 2+ |
| Hold attention, others unnoticed | 41.4 | flat | Level 2+ |
| Sense traps in sight | 35.9 | flat | Level 2+ |
| Permanent heatless flame | 16.6 | flat | Level 2+ |
| Open a lock or bar | 41.4 | flat | Level 2+ |
| Float a creature or object 20 ft | 55.2 | flat | Level 2+ |
| Locate a familiar or named object | 55.2 | flat | Level 2+ |
| Locate nearby animals or plants | 41.4 | flat | Level 2+ |
| Magically lock a door or container | 41.4 | flat | Level 2+ |
| Falsify what detection magic reads | 41.4 | flat | Level 2+ |
| Tiny beast carries a message | 41.4 | flat | Level 2+ |
| Stored spoken message with a trigger | 41.4 | flat | Level 2+ |
| Neutralize poison, advantage and resistance | 55.2 | flat | Level 2+ |
| Preserve a corpse | 35.9 | flat | Level 2+ |
| Hidden extradimensional refuge for eight | 96.6 | flat | Level 2+ |
| See invisible and ethereal | 69 | flat | Level 2+ |
| Zone with no sound | 82.8 | flat | Level 2+ |
| Read surface thoughts or probe a mind | 69 | flat | Level 2+ |
| Creatures cannot speak lies | 69 | flat | Level 2+ |
| Stop a spell as it is cast | 138 | flat | Level 3+ |
| Bright daylight over a wide area | 96.6 | flat | Level 3+ |
| End a spell on a target | 138 | flat | Level 3+ |
| Food and water for fifteen creatures | 82.8 | flat | Level 3+ |
| Hidden rune that triggers on a condition | 55.2 | flat | Level 3+ |
| Regain half the damage dealt | 41.4 | flat | Level 3+ |
| Illusion with sound, smell, and temperature | 96.6 | flat | Level 3+ |
| Hide from divination and scrying | 69 | flat | Level 3+ |
| Overgrow plants into a thicket | 34.5 | flat | Level 3+ |
| Return a recently dead creature to life | 193.2 | flat | Level 3+ |
| See and hear a distant place | 124.2 | flat | Level 3+ |
| Send a short message to anyone you know | 82.8 | flat | Level 3+ |
| Sealed dome shelter for hours | 110.4 | flat | Level 3+ |
| A corpse answers five questions | 82.8 | flat | Level 3+ |
| Talk with plants and command them | 55.2 | flat | Level 3+ |
| Summon a fast riding steed | 96.6 | flat | Level 3+ |
| Summon fey spirits as beasts that fight for you | 193.2 | flat | Level 3+ |
| Raise a skeleton or zombie that obeys you | 151.8 | flat | Level 3+ |
| Understand and speak any language | 82.8 | flat | Level 3+ |
| End a curse or attunement to a cursed item | 96.6 | flat | Level 3+ |
| Breathe underwater | 55.2 | flat | Level 3+ |
| Walk on liquid surfaces | 41.4 | flat | Level 3+ |
| Wall of wind that stops missiles, gas, and flyers | 75.9 | flat | Level 3+ |

### Targets and area

| Item | Points | Unit | Available from |
|---|---|---|---|
| 5 ft cube | 3 | flat | Cantrip+ |
| Each additional target (a share of the per-target effects) | see rules | per extra target | Cantrip+ |
| 15 ft cone | 6.3 | flat | Level 1+ |
| 15 ft cube | 9 | flat | Level 1+ |
| 20 ft cube | 12 | flat | Level 1+ |
| 20 ft radius | 21.2 | flat | Level 1+ |
| 30 ft radius | 31.9 | flat | Level 1+ |
| 10 ft square | 6 | flat | Level 1+ |
| 20 ft square | 12 | flat | Level 1+ |
| Split effect among several targets | 6.7 | flat | Level 1+ |
| 60 ft line | 14.7 | flat | Level 2+ |
| 10 ft radius | 10.6 | flat | Level 2+ |
| 15 ft radius | 15.9 | flat | Level 2+ |
| 5 ft radius | 5.3 | flat | Level 2+ |
| 30 ft cone | 12.7 | flat | Level 3+ |
| 30 ft cube | 18 | flat | Level 3+ |
| 40 ft cube | 24 | flat | Level 3+ |
| 100 ft line | 13.4 | flat | Level 3+ |
| 40 ft radius | 42.5 | flat | Level 3+ |

### Convex price curves

Price for an amount `q` is `base x q x (q / reference)^0.4 x category multiplier`.

| Average damage | Level 1 or 2 damage price | Healing price at the same amount |
|---|---|---|
| 4.5 | 13.5 | 14.4 |
| 7 | 25 | 26.7 |
| 10.5 | 44.2 | 47 |
| 14 | 66 | 70.4 |
| 16.5 | 83.1 | 88.5 |
| 21 | 116.5 | 124.1 |

Cantrip damage (`c_dmg`) uses its own lower base and is capped at an average of 6.5.

### Range

| Range | Points |
|---|---|
| Self | 0 |
| Touch | 0 |
| 10 feet | 2.2 |
| 30 feet | 3.4 |
| 60 feet | 5.6 |
| 90 feet | 7.8 |
| 120 feet | 8.9 |
| 150 feet | 10.1 |
| 1 mile | 15.7 |
| Unlimited | 20.1 |

### Casting time

| Casting time | Points |
|---|---|
| 1 action | 0 |
| 1 bonus action | 8.4 |
| 1 reaction | 10.5 |
| 1 minute | -4.2 |
| 10 minutes | -8.4 |
| 1 hour | -12.6 |

A longer casting time is a refund. A bonus action or reaction costs more because it stacks with your other actions.

### Duration

| Duration | Points |
|---|---|
| Instantaneous | 0 |
| 1 round | 3.6 |
| 1 minute | 12 |
| 10 minutes | 19.2 |
| 1 hour | 26.4 |
| 8 hours | 33.6 |
| 24 hours | 38.4 |
| 10 days | 43.2 |
| Until dispelled | 48 |

### Other costs

| Item | Points |
|---|---|
| Ritual casting (cast without a slot) | 6 |
| Flat upcast charge, level 1 (no listed increase) | 6 |
| Flat upcast charge, level 2 (no listed increase) | 9.5 |
| Flat upcast charge, level 3 (no listed increase) | 13.1 |

Cantrips are scored at the base tier only. Extra dice at levels 5, 11, and 17 are covered by the cantrip scaling share. Listed upcast increases (see the rules) replace the flat charge.

## Refund tables (points you get back)

### Components

| Component | Refund |
|---|---|
| Verbal | -1.1 |
| Somatic | -1.1 |
| Material, no stated cost | -1.7 |

Materials with a stated gold cost replace the plain material refund:

| Cost of material | Refund, kept | Refund, consumed |
|---|---|---|
| 1 to 10 gp | -4.6 | -6.9 |
| 11 to 50 gp | -6.9 | -10.3 |
| 51 to 100 gp | -10.3 | -15.5 |
| 101 to 250 gp | -12.6 | -18.9 |
| over 250 gp | -14.9 | -22.4 |

A consumed material refunds 1.5 times as much, because the caster pays again on every cast.

### Caveats and limits

| Limit | Refund |
|---|---|
| Willing target only | -1.5 |
| Restricted to a creature type or trait | -3 |
| Excludes a creature type (undead, constructs, low Int) | -1 |
| Ends if you or allies harm the target | -4.1 |
| Ends if the target attacks or casts | -4.1 |
| Ends on damage or a shake | -3 |
| Target repeats the save | -3 |
| Target gets advantage on the save in some cases | -2 |
| Target knows it was affected afterward | -2 |
| Target can use an action to escape | -3 |
| Effect capped by a hit point pool | -5.1 |
| Target refuses harmful orders | -2 |
| Narrow reaction trigger | -3 |
| Effect is easy to kill or dispel | -2 |
| Effect decays or expires early | -1.5 |
| Benefit delivered one piece at a time | -3 |
| No direct combat use | -3 |
| Revealed by touch or an Investigation check | -3 |
| Ends if armor is worn | -1.5 |
| Limited to one sense | -1.5 |
| Save negates the whole effect | -2 |
| Action each turn to keep it going | -4.1 |
| Blocked by thin barriers | -1.5 |
| Result depends on creature reactions | -2 |
| Loud, reveals your position | -1 |
| Cosmetic or trivial effects only | -3 |
| Effect ends when used | -4.1 |
| Breaks if the target leaves range | -1 |
| You take the damage the target takes | -7.1 |
| Target suffers when the spell ends | -7.6 |

### Concentration and class availability

| Item | Points |
|---|---|
| Concentration | -4.8 |
| On 1 class list | -2.3 |
| On 2 or 3 class lists | -1.1 |
| On 4 or 5 class lists | 0 |
| On 6 or more class lists | +1.7 |

Use concentration only if the spell lasts a minute or more.

## Worked examples

### Fire Bolt: 25 of 25 points

| Type | Item | Points |
|---|---|---|
| Effect | Cantrip damage (average 6.5 or less) x5.5 | +11.1 |
| Effect | Delivered by attack roll | +0 |
| Effect | Ignites loose flammables | +3 |
| Delivery | Range: 120 feet | +8.9 |
| Delivery | Casting time: 1 action | +0 |
| Duration | Duration: Instantaneous (x0.68 for a weak effect) | +0 |
| Delivery | Scales with character level | +5.3 |
| Refund | V component | -1.1 |
| Refund | S component | -1.1 |
| Availability | On 2 class lists | -1.1 |

### Magic Missile: 72.3 of 100 points

| Type | Item | Points |
|---|---|---|
| Effect | Damage dealt x10.5 | +44.2 |
| Effect | Hits automatically | +10.1 |
| Effect | Split effect among several targets | +6.7 |
| Delivery | Range: 120 feet | +8.9 |
| Delivery | Casting time: 1 action | +0 |
| Duration | Duration: Instantaneous | +0 |
| Delivery | Upcasting: +3.5 damage dealt per slot level | +5.7 |
| Refund | V component | -1.1 |
| Refund | S component | -1.1 |
| Availability | On 2 class lists | -1.1 |

### Hold Person: 138.6 of 150 points

| Type | Item | Points |
|---|---|---|
| Effect | Paralyzed | +95 |
| Limit | Target repeats the save | -3 |
| Limit | Restricted to a creature type or trait | -3 |
| Floor | Level 2 effect floor (effects must total 100) | +5 |
| Delivery | Range: 60 feet | +5.6 |
| Delivery | Casting time: 1 action | +0 |
| Duration | Duration: 1 minute | +12 |
| Refund | Concentration | -4.8 |
| Delivery | Upcasting: +1 target per slot level | +34 |
| Refund | V component | -1.1 |
| Refund | S component | -1.1 |
| Refund | Material component (no cost) | -1.7 |
| Availability | On 6 class lists | +1.7 |

### Fireball: 213.5 of 250 points

| Type | Item | Points |
|---|---|---|
| Effect | Damage dealt x28 | +174.3 |
| Effect | Delivered by save, half on success | +4.2 |
| Effect | 20 ft radius | +21.2 |
| Effect | Ignites loose flammables | +3 |
| Delivery | Range: 150 feet | +10.1 |
| Delivery | Casting time: 1 action | +0 |
| Duration | Duration: Instantaneous | +0 |
| Delivery | Upcasting: +3.5 damage dealt per slot level | +5.7 |
| Refund | V component | -1.1 |
| Refund | S component | -1.1 |
| Refund | Material component (no cost) | -1.7 |
| Availability | On 2 class lists | -1.1 |

## Scorecard: 24 cantrips

| Spell | Net cost | Left | Effects | Conc. | Comp. | Classes |
|---|---|---|---|---|---|---|
| Fire Bolt | 25 | 0 | 14.1 |  | VS | 2 |
| Dancing Lights | 24.2 | 0.8 | 16.6 | yes | VSM | 3 |
| Produce Flame | 23.9 | 1.1 | 12.5 |  | VS | 1 |
| Chill Touch | 23.3 | 1.7 | 11.4 |  | VS | 3 |
| Mage Hand | 23.1 | 1.9 | 13.8 |  | VS | 4 |
| Shillelagh | 21.5 | 3.5 | 11.6 |  | VSM | 1 |
| Minor Illusion | 21.4 | 3.6 | 16.8 |  | SM | 4 |
| Eldritch Blast | 20.8 | 4.2 | 11.1 |  | VS | 1 |
| Ray of Frost | 20.7 | 4.3 | 14.4 |  | VS | 2 |
| Prestidigitation | 19 | 6 | 6.9 |  | VS | 4 |
| Thaumaturgy | 18.9 | 6.1 | 13.8 |  | V | 1 |
| Poison Spray | 18.7 | 6.3 | 14 |  | VS | 4 |
| Message | 17.2 | 7.8 | 11 |  | VSM | 3 |
| Shocking Grasp | 17.1 | 7.9 | 16.4 |  | VS | 2 |
| Light | 15.9 | 9.1 | 4.1 |  | VM | 4 |
| Druidcraft | 15.2 | 9.8 | 19.3 |  | VS | 1 |
| Sacred Flame | 14.5 | 10.5 | 11.4 |  | VS | 1 |
| Vicious Mockery | 13.7 | 11.3 | 11.7 |  | V | 1 |
| Acid Splash | 13.1 | 11.9 | 10 |  | VS | 2 |
| Spare the Dying | 12.1 | 12.9 | 16.6 |  | VS | 1 |
| Guidance | 10.8 | 14.2 | 12.5 | yes | VS | 2 |
| Resistance | 9.1 | 15.9 | 12.5 | yes | VSM | 2 |
| True Strike | 8.6 | 16.4 | 8.9 | yes | S | 4 |
| Mending | 8.5 | 16.5 | 16.6 |  | VSM | 5 |

## Scorecard: 49 level 1 spells

| Spell | Net cost | Left | Effects | Conc. | Comp. | Classes |
|---|---|---|---|---|---|---|
| Detect Magic | 100 | 0 | 81.6 | yes | VS | 7 |
| Hunter's Mark | 99.9 | 0.1 | 59.5 | yes | V | 1 |
| Shield | 99.9 | 0.1 | 92.1 |  | VS | 2 |
| Sleep | 99.9 | 0.1 | 84.2 |  | VSM | 3 |
| Guiding Bolt | 98.5 | 1.5 | 84.8 |  | VS | 1 |
| Animal Friendship | 90.8 | 9.2 | 50 |  | VSM | 3 |
| Inflict Wounds | 89.3 | 10.7 | 83.1 |  | VS | 1 |
| Unseen Servant | 86 | 14 | 58 |  | VSM | 3 |
| Illusory Script | 85.2 | 14.8 | 50 |  | SM | 3 |
| Disguise Self | 85 | 15 | 64.9 |  | VS | 3 |
| Silent Image | 84.4 | 15.6 | 73.9 | yes | VSM | 3 |
| Fog Cloud | 84.3 | 15.7 | 50 | yes | VS | 4 |
| Detect Poison and Disease | 82.8 | 17.2 | 67.8 | yes | VSM | 4 |
| Charm Person | 81.7 | 18.3 | 50 |  | VS | 5 |
| Hideous Laughter | 81.6 | 18.4 | 82 | yes | VSM | 2 |
| Alarm | 80.8 | 19.2 | 50 |  | VSM | 2 |
| False Life | 79.8 | 20.2 | 50 |  | VSM | 2 |
| Sanctuary | 78.4 | 21.6 | 64.9 |  | VSM | 1 |
| Find Familiar | 78.1 | 21.9 | 93.9 |  | VSM | 1 |
| Longstrider | 77.8 | 22.2 | 50 |  | VSM | 4 |
| Detect Evil and Good | 77.4 | 22.6 | 67.8 | yes | VS | 2 |
| Identify | 76.3 | 23.7 | 91.1 |  | VSM | 2 |
| Mage Armor | 75.6 | 24.4 | 50 |  | VSM | 2 |
| Comprehend Languages | 75.5 | 24.5 | 50 |  | VSM | 4 |
| Bless | 74 | 26 | 60.8 | yes | VSM | 2 |
| Bane | 73.5 | 26.5 | 60.8 | yes | VSM | 2 |
| Shield of Faith | 73.4 | 26.6 | 50 | yes | VSM | 2 |
| Magic Missile | 72.3 | 27.7 | 61 |  | VS | 2 |
| Feather Fall | 71.2 | 28.8 | 50 |  | VM | 3 |
| Hellish Rebuke | 70.6 | 29.4 | 51.3 |  | VS | 1 |
| Expeditious Retreat | 69.5 | 30.5 | 50 | yes | VS | 3 |
| Speak with Animals | 66.9 | 33.1 | 50 |  | VS | 3 |
| Entangle | 65.5 | 34.5 | 58 | yes | VS | 1 |
| Healing Word | 64.6 | 35.4 | 50 |  | V | 3 |
| Command | 64.4 | 35.6 | 50 |  | V | 2 |
| Witch Bolt | 64.1 | 35.9 | 50.1 | yes | VSM | 3 |
| Grease | 61.4 | 38.6 | 50 |  | VSM | 1 |
| Divine Favor | 61.1 | 38.9 | 50 | yes | VS | 1 |
| Faerie Fire | 60.6 | 39.4 | 50 | yes | V | 2 |
| Burning Hands | 60.1 | 39.9 | 57.7 |  | VS | 2 |
| Protection from Evil and Good | 59 | 41 | 50 | yes | VSM | 4 |
| Thunderwave | 58.6 | 41.4 | 53.8 |  | VS | 4 |
| Jump | 58.1 | 41.9 | 50 |  | VSM | 4 |
| Heroism | 57.9 | 42.1 | 50 | yes | VS | 2 |
| Cure Wounds | 55.4 | 44.6 | 50 |  | VS | 5 |
| Purify Food and Drink | 51.9 | 48.1 | 50 |  | VS | 3 |
| Color Spray | 51.8 | 48.2 | 52.3 |  | VSM | 2 |
| Create or Destroy Water | 51.4 | 48.6 | 50 |  | VSM | 2 |
| Goodberry | 40.4 | 59.6 | 49.9 |  | VSM | 2 |

## Scorecard: 53 level 2 spells

| Spell | Net cost | Left | Effects | Conc. | Comp. | Classes |
|---|---|---|---|---|---|---|
| Animal Messenger | 146.3 | 3.7 | 100 |  | VSM | 3 |
| Scorching Ray | 143.7 | 6.3 | 123.2 |  | VS | 2 |
| Gentle Repose | 141.2 | 8.8 | 100 |  | VSM | 2 |
| Aid | 140.4 | 9.6 | 100 |  | VSM | 2 |
| Invisibility | 140.2 | 9.8 | 100 | yes | VSM | 4 |
| Magic Mouth | 140 | 10 | 100 |  | VSM | 2 |
| Hold Person | 138.6 | 11.4 | 100 | yes | VSM | 6 |
| Magic Weapon | 136.2 | 13.8 | 100 | yes | VS | 2 |
| Arcane Lock | 133.2 | 16.8 | 100 |  | VSM | 1 |
| Continual Flame | 131.5 | 18.5 | 100.1 |  | VSM | 2 |
| Silence | 130 | 20 | 104 | yes | VS | 3 |
| Arcanist's Magic Aura | 129.2 | 20.8 | 100 |  | VSM | 1 |
| Enhance Ability | 128.4 | 21.6 | 100 | yes | VSM | 4 |
| Darkvision | 128.2 | 21.8 | 100 |  | VSM | 4 |
| Prayer of Healing | 128 | 22 | 127.6 |  | V | 2 |
| Spiritual Weapon | 124.6 | 25.4 | 100.1 |  | VS | 1 |
| Moonbeam | 124.3 | 25.7 | 103.7 | yes | VSM | 1 |
| Protection from Poison | 124.2 | 25.8 | 100 |  | VS | 4 |
| Suggestion | 123.3 | 26.7 | 100 | yes | VM | 4 |
| Blindness/Deafness | 122.4 | 27.6 | 100 |  | V | 4 |
| Zone of Truth | 121.5 | 28.5 | 100 |  | VS | 3 |
| See Invisibility | 121.4 | 28.6 | 100 |  | VSM | 3 |
| Spike Growth | 119.4 | 30.6 | 99.9 | yes | VSM | 2 |
| Flame Blade | 118.8 | 31.2 | 100.1 | yes | VSM | 1 |
| Alter Self | 118.3 | 31.7 | 100 | yes | VS | 2 |
| Rope Trick | 117.2 | 32.8 | 100 |  | VSM | 1 |
| Web | 117.2 | 32.8 | 100 | yes | VSM | 2 |
| Pass without Trace | 116.6 | 33.4 | 100 | yes | VSM | 2 |
| Darkness | 116.1 | 33.9 | 100 | yes | VM | 3 |
| Barkskin | 115.1 | 34.9 | 100 | yes | VSM | 2 |
| Spider Climb | 115.1 | 34.9 | 100 | yes | VSM | 3 |
| Levitate | 115 | 35 | 100 | yes | VSM | 2 |
| Flaming Sphere | 113.4 | 36.6 | 99.9 | yes | VSM | 2 |
| Enthrall | 112.3 | 37.7 | 100 |  | VS | 2 |
| Calm Emotions | 112 | 38 | 104 | yes | VS | 2 |
| Acid Arrow | 110.8 | 39.2 | 99.9 |  | VSM | 1 |
| Locate Object | 109.2 | 40.8 | 100 | yes | VSM | 6 |
| Heat Metal | 108.7 | 41.3 | 100 | yes | VSM | 2 |
| Mirror Image | 108.7 | 41.3 | 100 |  | VS | 3 |
| Shatter | 108.7 | 41.3 | 100 |  | VSM | 4 |
| Enlarge/Reduce | 106.7 | 43.3 | 100 | yes | VSM | 4 |
| Ray of Enfeeblement | 106.5 | 43.5 | 100 | yes | VS | 2 |
| Misty Step | 106.2 | 43.8 | 100 |  | V | 3 |
| Blur | 105 | 45 | 100 | yes | V | 2 |
| Warding Bond | 104.2 | 45.8 | 100 |  | VSM | 2 |
| Crown of Madness | 103.8 | 46.2 | 100 | yes | VS | 4 |
| Find Traps | 102.6 | 47.4 | 100 |  | VS | 3 |
| Gust of Wind | 102.2 | 47.8 | 100 | yes | VSM | 3 |
| Detect Thoughts | 100.2 | 49.8 | 100 | yes | VSM | 3 |
| Knock | 99.4 | 50.6 | 100 |  | V | 3 |
| Locate Animals or Plants | 98 | 52 | 100 |  | VSM | 3 |
| Lesser Restoration | 97.8 | 52.2 | 100 |  | VS | 5 |
| Augury | 85.4 | 64.6 | 100 |  | VSM | 1 |

## Scorecard: 43 level 3 spells

| Spell | Net cost | Left | Effects | Conc. | Comp. | Classes |
|---|---|---|---|---|---|---|
| Conjure Animals | 228.2 | 21.8 | 193.2 | yes | VS | 2 |
| Glyph of Warding | 227.1 | 22.9 | 208.9 |  | VSM | 3 |
| Fireball | 213.5 | 36.5 | 202.7 |  | VSM | 2 |
| Call Lightning | 203.2 | 46.8 | 175.7 | yes | VS | 1 |
| Lightning Bolt | 195.6 | 54.4 | 194.9 |  | VSM | 2 |
| Water Breathing | 192.4 | 57.6 | 150 |  | VSM | 4 |
| Phantom Steed | 188.2 | 61.8 | 150 |  | VS | 1 |
| Spirit Guardians | 186.9 | 63.1 | 170.7 | yes | VSM | 1 |
| Meld into Stone | 183.3 | 66.7 | 150 |  | VS | 2 |
| Fly | 183.2 | 66.8 | 150 | yes | VSM | 3 |
| Leomund's Tiny Hut | 180.4 | 69.6 | 150 |  | VSM | 2 |
| Water Walk | 180.4 | 69.6 | 150 |  | VSM | 4 |
| Daylight | 179.8 | 70.2 | 150 |  | VS | 5 |
| Major Image | 179.5 | 70.5 | 150 | yes | VSM | 4 |
| Feign Death | 177 | 73 | 150 |  | VSM | 4 |
| Counterspell | 174 | 76 | 150 |  | S | 3 |
| Tongues | 173.6 | 76.4 | 150 |  | VM | 5 |
| Dispel Magic | 171.5 | 78.5 | 150 |  | VS | 7 |
| Magic Circle | 169.8 | 80.2 | 150 |  | VSM | 4 |
| Protection from Energy | 167.9 | 82.1 | 150 | yes | VS | 5 |
| Revivify | 167.5 | 82.5 | 193.2 |  | VSM | 2 |
| Nondetection | 167 | 83 | 150 |  | VSM | 3 |
| Sending | 165.7 | 84.3 | 150 |  | VSM | 3 |
| Gaseous Form | 165.1 | 84.9 | 150 | yes | VSM | 3 |
| Bestow Curse | 165 | 85 | 150 | yes | VS | 3 |
| Speak with Plants | 163.9 | 86.1 | 150 |  | VS | 3 |
| Mass Healing Word | 163.4 | 86.6 | 150 |  | V | 1 |
| Sleet Storm | 162.3 | 87.7 | 150 | yes | VSM | 3 |
| Speak with Dead | 161.4 | 88.6 | 150 |  | VSM | 2 |
| Wind Wall | 161.1 | 88.9 | 150 | yes | VSM | 2 |
| Hypnotic Pattern | 160.3 | 89.7 | 150 | yes | SM | 4 |
| Blink | 158.7 | 91.3 | 150 |  | VS | 2 |
| Slow | 158.1 | 91.9 | 150 | yes | VSM | 2 |
| Stinking Cloud | 158 | 92 | 150 | yes | VSM | 3 |
| Plant Growth | 156.8 | 93.2 | 150 |  | VS | 3 |
| Clairvoyance | 156.2 | 93.8 | 150 | yes | VSM | 4 |
| Beacon of Hope | 156.1 | 93.9 | 150 | yes | VS | 1 |
| Vampiric Touch | 155.6 | 94.4 | 150.1 | yes | VS | 2 |
| Animate Dead | 154.9 | 95.1 | 151.8 |  | VSM | 2 |
| Fear | 150.3 | 99.7 | 150 | yes | VSM | 4 |
| Remove Curse | 147.8 | 102.2 | 150 |  | VS | 4 |
| Create Food and Water | 147.1 | 102.9 | 150 |  | VS | 2 |
| Haste | 146.5 | 103.5 | 150 | yes | VSM | 2 |

Full line items for any spell: `python tools/pointbuy.py score <spell-file-name>`, for example `score fire-bolt`. The same data is in `data/spell-scores.csv` and `data/point-buy.json`. Recalibrate after any change to prices or builds with `python tools/pointbuy.py fit`, then `report`.

## Known limits of this model

- Damage is valued by average roll. It does not model how monsters resist or how often a save fails.
- Typical spells score well under their budget. The budget is a ceiling set by the strongest spell at each level. See `docs/spell-scaling-analysis.md`.
- Hard control effects are priced by my judgment of how much a lost turn is worth. Not tested at a table. Adjust the condition costs if your group disagrees.
- A few level 2 and level 3 spells pass as one level lower under these rules. The stress test in the analysis lists them.
- The level 3 budget is measured from 43 spells that were written once and have had no second pass. It is the least checked number here.
- Run `python tools/pointbuy.py check` after any change. It runs the logic checks and the exploit probes and exits non-zero on a failure.
- A limit only refunds points if it matters. DMs should reject a limit that never comes up.
- Utility spells score low because they have little combat value. That is not a mistake. Raise their duration or area for a stronger version.
- Levels 4 to 9 are not modeled.

