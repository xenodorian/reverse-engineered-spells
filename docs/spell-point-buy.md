# Spell Point Buy

A point budget system for building cantrips, 1st-level spells, and 2nd-level spells. A cantrip gets **25 points**, a 1st-level spell **100**, and a 2nd-level spell **150**. Effects, range, and duration cost points. Components and limits give points back. A spell is legal if it passes every rule below and its net cost is at or under its budget.

> This is a homebrew tool. Prices are my own design, calibrated against the 24 cantrips, 49 level 1 spells, and 53 level 2 spells in `spells/`. They are not official. The spell files were written from memory and are not checked against the books, and the DMG guidance in `docs/creating-a-spell.md` is also from memory. Why level 2 is 150 and how the curve was chosen is in `docs/spell-scaling-analysis.md`. Playtest before trusting any score.

## Budgets and clearances

| Level | Budget | Effects must total | Magnitude caps | Strong conditions total at most |
|---|---|---|---|---|
| Cantrip | 25 | 49 or less | yes | no strong conditions |
| Level 1 | 100 | 50 to 99 | yes | 82 |
| Level 2 | 150 | 100 or more | yes | 95 |

"Effects" means the capability lines only: damage, healing, buffs, conditions, utility, targets, and area. Range, casting time, duration, and refunds are not counted.

## Rules

| Rule | What it does |
|---|---|
| Effect floor | A level 1 spell's effects must total at least 50. A level 2 spell's must total at least 100. A smaller total is topped up with a floor line, so anything a level 1 spell does costs 50 or more at its strength, and anything level 2 costs at least a whole level 1 budget. |
| Effect ceiling | Cantrip effects must total 49 or less. Level 1 effects must total 99 or less. The calculator rejects anything above, because it would be the next level's strength. |
| Items by level | Each item has a minimum level, shown in the tables. A spell can only use items at or below its level. |
| Magnitude caps | Damage, healing, temporary HP, extra targets, AC, and other scalable items cannot exceed the highest value used at that level in the existing spells, carried up from lower levels. Damage has separate caps for touch spells, for spells that split across targets, and for cantrips that add a rider, because those get more or less damage than a plain ranged hit. |
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

1. **Pick the level.** Budgets are cantrip 25, level 1 100, level 2 150.
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
| Cantrip | 20 to 25 | Strong cantrip. Reliable damage or a flexible effect. |
| Cantrip | Under 20 | Minor or niche. Room to add range or a rider. |
| Level 1 | Over 100 | Over budget. |
| Level 1 | 90 to 100 | Premium. Among the best first-level spells. |
| Level 1 | 60 to 89 | Standard. Solid, reliable spells. |
| Level 1 | Under 60 | Utility or situational. Headroom to spend on range, duration, or targets. |
| Level 2 | Over 150 | Over budget. |
| Level 2 | 130 to 150 | Premium. |
| Level 2 | 105 to 129 | Standard. |
| Level 2 | Under 105 | Utility or situational. |

## What the existing spells show

Counted from the spell files, and used to set the refund sizes below.

| Pattern | Cantrips (24) | Level 1 (49) | Level 2 (53) |
|---|---|---|---|
| Verbal component | 22 of 24 | 48 of 49 | 53 of 53 |
| Somatic component | 21 of 24 | 44 of 49 | 46 of 53 |
| Material component | 7 of 24 | 26 of 49 | 34 of 53 |
| Material with a gold cost | 0 of 24 | 3 of 49 | 5 of 53 |
| Concentration | 4 of 24 | 17 of 49 | 26 of 53 |
| Ritual | 0 of 24 | 10 of 49 | 6 of 53 |
| Has an at-higher-levels clause | 10 of 24 | 22 of 49 | 16 of 53 |
| Cast as an action | 22 of 24 | 36 of 49 | 46 of 53 |
| Cast as a bonus action or reaction | 1 of 24 | 9 of 49 | 4 of 53 |
| Cast time of a minute or more | 1 of 24 | 4 of 49 | 3 of 53 |
| Instantaneous duration | 11 of 24 | 12 of 49 | 10 of 53 |
| Average classes per spell | 2.4 | 2.6 | 2.6 |
| Spells on exactly one class list | 8 of 24 | 9 of 49 | 8 of 53 |
| Average net cost, concentration spells | 14 | 75 | 119 |
| Average net cost, other spells | 19 | 74 | 122 |
| Average net cost, spells with a material | 18 | 76 | 122 |
| Average net cost, spells with no material | 18 | 74 | 116 |

Takeaways: nearly every spell has a verbal component, most have a somatic one, and about half have a material. Materials are common, so a mundane material refunds little. Gold-cost materials are rare and start at level 1, so they refund heavily. Spells with materials do not score higher than spells without in this set, so the data does not by itself show that materials mark stronger spells. The larger refund for gold-cost materials follows the design rule that costly components limit power, not a trend in these files. Concentration spells are the long-duration ones, so the concentration refund offsets part of the duration cost.

## Price tables (points you spend)

Prices are base price times a calibrated category multiplier. "Points" is the price of one use. Items marked with a reference amount use the convex curve, and the price shown is at that reference amount. Use the curve table below for other amounts.

### Damage and delivery

| Item | Points | Unit | Available from |
|---|---|---|---|
| Damage dealt | 43.7 | per avg damage (at 10.5) | Level 1+ |
| Repeat damage on later turns | 43.7 | per avg damage (at 10.5) | Level 1+ |
| Extra damage on each weapon hit | 46.6 | per avg damage (at 3.5) | Level 1+ |
| Damage for each 5 ft moved in the area | 25 | per avg damage (at 5) | Level 2+ |
| Half damage on a miss | 6.7 | flat | Level 2+ |
| Delivered by attack roll | 0 | flat | Cantrip+ |
| Delivered by save, half on success | 4.2 | flat | Level 1+ |
| Hits automatically | 10 | flat | Level 1+ |
| Cantrip damage (average 6.5 or less) | 11 | per avg damage (at 5.5) | Cantrip+ |

### Healing

| Item | Points | Unit | Available from |
|---|---|---|---|
| Hit points restored (modifier assumed +3) | 29.2 | per avg HP (at 7.5) | Level 1+ |
| Temporary hit points | 20.3 | per HP (at 6.5) | Level 1+ |
| Temporary hit points renewed each turn | 6.2 | per HP per turn | Level 1+ |

### Buffs and debuffs

| Item | Points | Unit | Available from |
|---|---|---|---|
| Armor Class bonus | 42.9 | per +1 AC (at 3) | Level 1+ |
| d4 bonus to attacks and saves | 30.4 | per target | Level 1+ |
| Attacks against target have advantage | 25.9 | flat | Level 1+ |
| Advantage on one next attack | 18.8 | flat | Level 1+ |
| Disadvantage vs six creature types plus charm and fear immunity | 42 | flat | Level 1+ |
| Immune to frightened | 8.9 | flat | Level 1+ |
| Walking speed bonus | 1.8 | per foot | Level 1+ |
| Dash as bonus action each turn | 30.4 | flat | Level 1+ |
| Triple jump distance | 7.1 | flat | Level 1+ |
| Negate falling damage and slow fall | 14.3 | flat | Level 1+ |
| Immune to one named spell | 4.5 | flat | Level 1+ |
| Attackers have disadvantage against you | 67 | flat | Level 2+ |
| Invisible until you attack or cast | 89.3 | flat | Level 2+ |
| Three duplicates that absorb attacks | 71.4 | flat | Level 2+ |
| Teleport up to 30 ft | 49.1 | flat | Level 2+ |
| Weapon becomes magical, +1 to hit and damage | 49.1 | flat | Level 2+ |
| Resist all damage, +1 AC and saves for one ally | 80.4 | flat | Level 2+ |
| Advantage on one ability's checks plus a perk | 35.7 | flat | Level 2+ |
| Grow or shrink a creature with combat benefits | 49.1 | flat | Level 2+ |
| +10 Stealth and untrackable for a group | 53.6 | flat | Level 2+ |
| Advantage on your next attack against one target | 8.9 | flat | Cantrip+ |
| d4 on one ability check | 12.5 | flat | Cantrip+ |
| d4 on one saving throw | 12.5 | flat | Cantrip+ |
| Enchant a club or staff (spell modifier, d8, magical) | 11.6 | flat | Cantrip+ |

### Conditions and control

| Item | Points | Unit | Available from |
|---|---|---|---|
| Prone | 10 | flat | Level 1+ |
| Charmed | 31 | flat | Level 1+ |
| Frightened | 31 | flat | Level 1+ |
| Blinded | 31 | flat | Level 1+ |
| Restrained | 36 | flat | Level 1+ |
| Incapacitated | 72 | flat | Level 1+ |
| Asleep (wakes on damage or a shake) | 48 | flat | Level 1+ |
| Forced to obey a one word order | 29 | flat | Level 1+ |
| Paralyzed | 95 | flat | Level 2+ |
| Strength weapon damage halved | 40 | flat | Level 2+ |
| Follows a reasonable suggestion | 70 | flat | Level 2+ |
| Charmed and forced to attack a chosen creature | 80 | flat | Level 2+ |
| Condition with no save or roll | 15 | flat | Level 1+ |
| Forced movement | 5 | flat | Level 1+ |
| Difficult terrain | 10 | flat | Level 1+ |
| Heavily obscured area | 26 | flat | Level 1+ |
| Outlines target, negates invisibility | 10 | flat | Level 1+ |
| Ignites loose flammables | 3 | flat | Cantrip+ |
| Scatters gas and snuffs flames | 12 | flat | Level 2+ |
| Hazard is hard to see | 10 | flat | Level 2+ |
| Target speed reduced 10 ft until your next turn | 6 | flat | Cantrip+ |
| Target cannot regain HP until your next turn | 3 | flat | Cantrip+ |
| Target cannot take reactions until its next turn | 8 | flat | Cantrip+ |
| Target has disadvantage on its next attack roll | 8 | flat | Cantrip+ |
| Target gets no cover bonus to the save | 3 | flat | Cantrip+ |

### Utility

| Item | Points | Unit | Available from |
|---|---|---|---|
| Sense a category within 30 ft | 35.9 | flat | Level 1+ |
| Learn aura or school of what you sense | 13.8 | flat | Level 1+ |
| Reveal properties or lore | 45.5 | per item | Level 1+ |
| Understand any language | 35.9 | flat | Level 1+ |
| Speak with a creature type | 31.7 | flat | Level 1+ |
| Create or destroy water | 17.9 | flat | Level 1+ |
| Purify food and drink | 13.8 | flat | Level 1+ |
| Day of food | 17.9 | flat | Level 1+ |
| Alert when an area is entered | 24.8 | flat | Level 1+ |
| Ward that redirects attackers | 64.8 | flat | Level 1+ |
| Create a visual illusion | 64.8 | flat | Level 1+ |
| Change your appearance | 64.8 | flat | Level 1+ |
| Hidden writing | 35.9 | flat | Level 1+ |
| Invisible helper that does chores | 57.9 | flat | Level 1+ |
| Summon a loyal scout and helper | 71.7 | flat | Level 1+ |
| Advantage to track a marked target | 8.3 | flat | Level 1+ |
| Move effect to a new target | 4.1 | flat | Level 1+ |
| Effect lasts until dismissed | 22.1 | flat | Level 1+ |
| Reshape your body: gills, new face, or claws | 75.8 | flat | Level 2+ |
| Tiny beast carries a message | 41.4 | flat | Level 2+ |
| Magically lock a door or container | 41.4 | flat | Level 2+ |
| Falsify what detection magic reads | 41.4 | flat | Level 2+ |
| Learn weal or woe of a plan | 41.4 | flat | Level 2+ |
| Suppress charm and fear or pacify hostility | 82.7 | flat | Level 2+ |
| Permanent heatless flame | 16.5 | flat | Level 2+ |
| Magical darkness | 62.1 | flat | Level 2+ |
| Darkvision 60 ft | 35.9 | flat | Level 2+ |
| Read surface thoughts or probe a mind | 69 | flat | Level 2+ |
| Hold attention, others unnoticed | 41.4 | flat | Level 2+ |
| Sense traps in sight | 35.9 | flat | Level 2+ |
| Preserve a corpse | 35.9 | flat | Level 2+ |
| Open a lock or bar | 41.4 | flat | Level 2+ |
| End a disease or a condition | 69 | flat | Level 2+ |
| Float a creature or object 20 ft | 55.2 | flat | Level 2+ |
| Locate nearby animals or plants | 41.4 | flat | Level 2+ |
| Locate a familiar or named object | 55.2 | flat | Level 2+ |
| Stored spoken message with a trigger | 41.4 | flat | Level 2+ |
| Neutralize poison, advantage and resistance | 55.2 | flat | Level 2+ |
| Hidden extradimensional refuge for eight | 96.5 | flat | Level 2+ |
| See invisible and ethereal | 69 | flat | Level 2+ |
| Climb walls and ceilings | 41.4 | flat | Level 2+ |
| Zone with no sound | 82.7 | flat | Level 2+ |
| Creatures cannot speak lies | 69 | flat | Level 2+ |
| Create light | 4.1 | flat | Cantrip+ |
| Four movable lights | 16.5 | flat | Cantrip+ |
| Spectral hand, 10 lb, 30 ft | 13.8 | flat | Cantrip+ |
| Repair one small break | 16.5 | flat | Cantrip+ |
| Whispered message to one creature | 11 | flat | Cantrip+ |
| Small image or sound | 13.8 | flat | Cantrip+ |
| Several minor magical tricks | 6.9 | flat | Cantrip+ |
| Minor nature effects | 19.3 | flat | Cantrip+ |
| Minor wonders | 13.8 | flat | Cantrip+ |
| Stabilize a dying creature | 16.5 | flat | Cantrip+ |

### Targets and area

| Item | Points | Unit | Available from |
|---|---|---|---|
| Each additional target (a share of the per-target effects) | see rules | per extra target | Cantrip+ |
| Split effect among several targets | 6.2 | flat | Level 1+ |
| 5 ft cube | 2.8 | flat | Cantrip+ |
| 5 ft radius | 5 | flat | Level 2+ |
| 10 ft square | 5.6 | flat | Level 1+ |
| 15 ft cone | 5.9 | flat | Level 1+ |
| 15 ft cube | 8.4 | flat | Level 1+ |
| 10 ft radius | 9.9 | flat | Level 2+ |
| 20 ft square | 11.2 | flat | Level 1+ |
| 20 ft cube | 11.2 | flat | Level 1+ |
| 60 ft line | 13.6 | flat | Level 2+ |
| 15 ft radius | 14.8 | flat | Level 2+ |
| 20 ft radius | 19.8 | flat | Level 1+ |
| 30 ft radius | 29.7 | flat | Level 1+ |

### Convex price curves

Price for an amount `q` is `base x q x (q / reference)^0.4 x category multiplier`.

| Average damage | Level 1 or 2 damage price | Healing price at the same amount |
|---|---|---|
| 4.5 | 13.4 | 14.3 |
| 7 | 24.8 | 26.6 |
| 10.5 | 43.7 | 46.8 |
| 14 | 65.4 | 70.1 |
| 16.5 | 82.3 | 88.2 |
| 21 | 115.4 | 123.6 |

Cantrip damage (`c_dmg`) uses its own lower base and is capped at an average of 6.5.

### Range

| Range | Points |
|---|---|
| Self | 0 |
| Touch | 0 |
| 10 feet | 2 |
| 30 feet | 3 |
| 60 feet | 5 |
| 90 feet | 7 |
| 120 feet | 8 |
| 150 feet | 8.9 |

### Casting time

| Casting time | Points |
|---|---|
| 1 action | 0 |
| 1 bonus action | 7.6 |
| 1 reaction | 9.5 |
| 1 minute | -3.8 |
| 10 minutes | -7.6 |
| 1 hour | -11.4 |

A longer casting time is a refund. A bonus action or reaction costs more because it stacks with your other actions.

### Duration

| Duration | Points |
|---|---|
| Instantaneous | 0 |
| 1 round | 3.9 |
| 1 minute | 12.9 |
| 10 minutes | 20.6 |
| 1 hour | 28.3 |
| 8 hours | 36 |
| 24 hours | 41.2 |
| 10 days | 46.3 |
| Until dispelled | 51.4 |

### Other costs

| Item | Points |
|---|---|
| Ritual casting (cast without a slot) | 6 |
| Flat upcast charge, level 1 (no listed increase) | 6 |
| Flat upcast charge, level 2 (no listed increase) | 9.7 |

Cantrips are scored at the base tier only. Extra dice at levels 5, 11, and 17 are covered by the cantrip scaling share. Listed upcast increases (see the rules) replace the flat charge.

## Refund tables (points you get back)

### Components

| Component | Refund |
|---|---|
| Verbal | -0.8 |
| Somatic | -0.8 |
| Material, no stated cost | -1.1 |

Materials with a stated gold cost replace the plain material refund:

| Cost of material | Refund, kept | Refund, consumed |
|---|---|---|
| 1 to 10 gp | -3 | -4.5 |
| 11 to 50 gp | -4.5 | -6.8 |
| 51 to 100 gp | -6.8 | -10.1 |
| 101 to 250 gp | -8.2 | -12.4 |
| over 250 gp | -9.8 | -14.6 |

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

### Concentration and class availability

| Item | Points |
|---|---|
| Concentration | -5 |
| On 1 class list | -2.5 |
| On 2 or 3 class lists | -1.2 |
| On 4 or 5 class lists | 0 |
| On 6 or more class lists | +1.9 |

Use concentration only if the spell lasts a minute or more.

## Worked examples

### Fire Bolt: 24.5 of 25 points

| Type | Item | Points |
|---|---|---|
| Effect | Cantrip damage (average 6.5 or less) x5.5 | +11 |
| Effect | Delivered by attack roll | +0 |
| Effect | Ignites loose flammables | +3 |
| Delivery | Range: 120 feet | +8 |
| Delivery | Casting time: 1 action | +0 |
| Duration | Duration: Instantaneous (x0.67 for a weak effect) | +0 |
| Delivery | Scales with character level | +5.3 |
| Refund | V component | -0.8 |
| Refund | S component | -0.8 |
| Availability | On 2 class lists | -1.2 |

### Magic Missile: 70.8 of 100 points

| Type | Item | Points |
|---|---|---|
| Effect | Damage dealt x10.5 | +43.7 |
| Effect | Hits automatically | +10 |
| Effect | Split effect among several targets | +6.2 |
| Delivery | Range: 120 feet | +8 |
| Delivery | Casting time: 1 action | +0 |
| Duration | Duration: Instantaneous | +0 |
| Delivery | Upcasting: +3.5 damage dealt per slot level | +5.7 |
| Refund | V component | -0.8 |
| Refund | S component | -0.8 |
| Availability | On 2 class lists | -1.2 |

### Hold Person: 140.5 of 150 points

| Type | Item | Points |
|---|---|---|
| Effect | Paralyzed | +95 |
| Limit | Target repeats the save | -3 |
| Limit | Restricted to a creature type or trait | -3 |
| Floor | Level 2 effect floor (effects must total 100) | +5 |
| Delivery | Range: 60 feet | +5 |
| Delivery | Casting time: 1 action | +0 |
| Duration | Duration: 1 minute | +12.9 |
| Refund | Concentration | -5 |
| Delivery | Upcasting: +1 target per slot level | +34.4 |
| Refund | V component | -0.8 |
| Refund | S component | -0.8 |
| Refund | Material component (no cost) | -1.1 |
| Availability | On 6 class lists | +1.9 |

## Scorecard: 24 cantrips

| Spell | Net cost | Left | Effects | Conc. | Comp. | Classes |
|---|---|---|---|---|---|---|
| Dancing Lights | 24.7 | 0.3 | 16.5 | yes | VSM | 3 |
| Produce Flame | 24.7 | 0.3 | 12.4 |  | VS | 1 |
| Fire Bolt | 24.5 | 0.5 | 14 |  | VS | 2 |
| Mage Hand | 23.8 | 1.2 | 13.8 |  | VS | 4 |
| Chill Touch | 23 | 2 | 11.3 |  | VS | 3 |
| Minor Illusion | 22.3 | 2.7 | 16.6 |  | SM | 4 |
| Shillelagh | 22.3 | 2.7 | 11.6 |  | VSM | 1 |
| Prestidigitation | 20.5 | 4.5 | 6.9 |  | VS | 4 |
| Ray of Frost | 20.5 | 4.5 | 14.3 |  | VS | 2 |
| Eldritch Blast | 20.2 | 4.8 | 11 |  | VS | 1 |
| Thaumaturgy | 19.1 | 5.9 | 13.8 |  | V | 1 |
| Poison Spray | 19 | 6 | 13.9 |  | VS | 4 |
| Light | 17.8 | 7.2 | 4.1 |  | VM | 4 |
| Message | 17.6 | 7.4 | 11 |  | VSM | 3 |
| Shocking Grasp | 17.5 | 7.5 | 16.3 |  | VS | 2 |
| Druidcraft | 15.2 | 9.8 | 19.3 |  | VS | 1 |
| Sacred Flame | 14.2 | 10.8 | 11.3 |  | VS | 1 |
| Vicious Mockery | 13.1 | 11.9 | 11.6 |  | V | 1 |
| Acid Splash | 12.9 | 12.1 | 9.9 |  | VS | 2 |
| Spare the Dying | 12.4 | 12.6 | 16.5 |  | VS | 1 |
| Guidance | 11.6 | 13.4 | 12.5 | yes | VS | 2 |
| Resistance | 10.5 | 14.5 | 12.5 | yes | VSM | 2 |
| Mending | 10 | 15 | 16.5 |  | VSM | 5 |
| True Strike | 8.5 | 16.5 | 8.9 | yes | S | 4 |

## Scorecard: 49 level 1 spells

| Spell | Net cost | Left | Effects | Conc. | Comp. | Classes |
|---|---|---|---|---|---|---|
| Detect Magic | 99.8 | 0.2 | 79.4 | yes | VS | 7 |
| Shield | 99.7 | 0.3 | 92.1 |  | VS | 2 |
| Sleep | 99.7 | 0.3 | 82.8 |  | VSM | 3 |
| Hunter's Mark | 99.6 | 0.4 | 59 | yes | V | 1 |
| Guiding Bolt | 97.7 | 2.3 | 84.2 |  | VS | 1 |
| Animal Friendship | 94.4 | 5.6 | 50 |  | VSM | 3 |
| Illusory Script | 90.5 | 9.5 | 50 |  | SM | 3 |
| Inflict Wounds | 88.9 | 11.1 | 82.3 |  | VS | 1 |
| Unseen Servant | 88.3 | 11.7 | 57.9 |  | VSM | 3 |
| Disguise Self | 87.3 | 12.7 | 64.8 |  | VS | 3 |
| Fog Cloud | 85.7 | 14.3 | 50 | yes | VS | 4 |
| Silent Image | 85.4 | 14.6 | 73.2 | yes | VSM | 3 |
| Alarm | 84.3 | 15.7 | 50 |  | VSM | 2 |
| Charm Person | 83.9 | 16.1 | 50 |  | VS | 5 |
| Detect Poison and Disease | 83 | 17 | 65.6 | yes | VSM | 4 |
| Hideous Laughter | 83 | 17 | 82 | yes | VSM | 2 |
| False Life | 82.9 | 17.1 | 50 |  | VSM | 2 |
| Find Familiar | 81.8 | 18.2 | 93.8 |  | VSM | 1 |
| Longstrider | 81 | 19 | 50 |  | VSM | 4 |
| Identify | 80.6 | 19.4 | 91 |  | VSM | 2 |
| Mage Armor | 79.1 | 20.9 | 50 |  | VSM | 2 |
| Sanctuary | 79 | 21 | 64.8 |  | VSM | 1 |
| Comprehend Languages | 78.6 | 21.4 | 50 |  | VSM | 4 |
| Detect Evil and Good | 76.9 | 23.1 | 65.6 | yes | VS | 2 |
| Bless | 75.5 | 24.5 | 60.8 | yes | VSM | 2 |
| Bane | 75 | 25 | 60.8 | yes | VSM | 2 |
| Shield of Faith | 74.3 | 25.7 | 50 | yes | VSM | 2 |
| Feather Fall | 71.3 | 28.7 | 50 |  | VM | 3 |
| Magic Missile | 70.8 | 29.2 | 59.9 |  | VS | 2 |
| Expeditious Retreat | 70.4 | 29.6 | 50 | yes | VS | 3 |
| Hellish Rebuke | 69 | 31 | 50.9 |  | VS | 1 |
| Speak with Animals | 68.8 | 31.2 | 50 |  | VS | 3 |
| Witch Bolt | 65.3 | 34.7 | 49.9 | yes | VSM | 3 |
| Entangle | 65 | 35 | 57.2 | yes | VS | 1 |
| Command | 64.4 | 35.6 | 50 |  | V | 2 |
| Healing Word | 63.4 | 36.6 | 50 |  | V | 3 |
| Grease | 62.7 | 37.3 | 50 |  | VSM | 1 |
| Divine Favor | 61.4 | 38.6 | 50 | yes | VS | 1 |
| Protection from Evil and Good | 61.4 | 38.6 | 50 | yes | VSM | 4 |
| Faerie Fire | 60.9 | 39.1 | 50 | yes | V | 2 |
| Jump | 60.2 | 39.8 | 50 |  | VSM | 4 |
| Burning Hands | 59.7 | 40.3 | 56.8 |  | VS | 2 |
| Heroism | 59.1 | 40.9 | 50 | yes | VS | 2 |
| Thunderwave | 58.3 | 41.7 | 52.8 |  | VS | 4 |
| Cure Wounds | 56 | 44 | 50 |  | VS | 5 |
| Color Spray | 52.8 | 47.2 | 51.9 |  | VSM | 2 |
| Purify Food and Drink | 52.2 | 47.8 | 50 |  | VS | 3 |
| Create or Destroy Water | 52.1 | 47.9 | 50 |  | VSM | 2 |
| Goodberry | 41.6 | 58.4 | 50 |  | VSM | 2 |

## Scorecard: 53 level 2 spells

| Spell | Net cost | Left | Effects | Conc. | Comp. | Classes |
|---|---|---|---|---|---|---|
| Animal Messenger | 150 | 0 | 100 |  | VSM | 3 |
| Magic Mouth | 146.4 | 3.6 | 100.1 |  | VSM | 2 |
| Gentle Repose | 145.4 | 4.6 | 100 |  | VSM | 2 |
| Aid | 143.5 | 6.5 | 99.9 |  | VSM | 2 |
| Invisibility | 143.4 | 6.6 | 100 | yes | VSM | 4 |
| Scorching Ray | 141.8 | 8.2 | 121.6 |  | VS | 2 |
| Arcane Lock | 140.6 | 9.4 | 100.1 |  | VSM | 1 |
| Hold Person | 140.5 | 9.5 | 100 | yes | VSM | 6 |
| Continual Flame | 138.8 | 11.2 | 100 |  | VSM | 2 |
| Magic Weapon | 137.8 | 12.2 | 100 | yes | VS | 2 |
| Arcanist's Magic Aura | 133 | 17 | 100 |  | VSM | 1 |
| Darkvision | 131.8 | 18.2 | 100 |  | VSM | 4 |
| Enhance Ability | 131.4 | 18.6 | 100 | yes | VSM | 4 |
| Silence | 129.3 | 20.7 | 102.5 | yes | VS | 3 |
| Prayer of Healing | 128.1 | 21.9 | 127.1 |  | V | 2 |
| Protection from Poison | 126.7 | 23.3 | 100 |  | VS | 4 |
| Suggestion | 126 | 24 | 100 | yes | VM | 4 |
| Spiritual Weapon | 124.5 | 25.5 | 100 |  | VS | 1 |
| See Invisibility | 124.4 | 25.6 | 100 |  | VSM | 3 |
| Moonbeam | 124 | 26 | 102.6 | yes | VSM | 1 |
| Blindness/Deafness | 123.3 | 26.7 | 100 |  | V | 4 |
| Zone of Truth | 122.8 | 27.2 | 100 |  | VS | 3 |
| Spike Growth | 120.6 | 29.4 | 100 | yes | VSM | 2 |
| Alter Self | 120.5 | 29.5 | 100 | yes | VS | 2 |
| Rope Trick | 120.1 | 29.9 | 100 |  | VSM | 1 |
| Flame Blade | 120 | 30 | 99.9 | yes | VSM | 1 |
| Pass without Trace | 119.4 | 30.6 | 100 | yes | VSM | 2 |
| Web | 119.4 | 30.6 | 100 | yes | VSM | 2 |
| Barkskin | 117.9 | 32.1 | 100 | yes | VSM | 2 |
| Spider Climb | 117.9 | 32.1 | 100 | yes | VSM | 3 |
| Darkness | 117.5 | 32.5 | 100 | yes | VM | 3 |
| Levitate | 116.7 | 33.3 | 100 | yes | VSM | 2 |
| Flaming Sphere | 114.8 | 35.2 | 100.1 | yes | VSM | 2 |
| Enthrall | 113.1 | 36.9 | 100 |  | VS | 2 |
| Locate Object | 111.8 | 38.2 | 100 | yes | VSM | 6 |
| Acid Arrow | 111.1 | 38.9 | 100 |  | VSM | 1 |
| Calm Emotions | 111.1 | 38.9 | 102.5 | yes | VS | 2 |
| Mirror Image | 110.1 | 39.9 | 100 |  | VS | 3 |
| Warding Bond | 110.1 | 39.9 | 100 |  | VSM | 2 |
| Heat Metal | 109.9 | 40.1 | 99.9 | yes | VSM | 2 |
| Shatter | 109.5 | 40.5 | 100.1 |  | VSM | 4 |
| Enlarge/Reduce | 108.2 | 41.8 | 100 | yes | VSM | 4 |
| Ray of Enfeeblement | 107.1 | 42.9 | 100 | yes | VS | 2 |
| Blur | 105.9 | 44.1 | 100 | yes | V | 2 |
| Misty Step | 105.6 | 44.4 | 100 |  | V | 3 |
| Crown of Madness | 104.2 | 45.8 | 100 | yes | VS | 4 |
| Gust of Wind | 104 | 46 | 100 | yes | VSM | 3 |
| Find Traps | 102.2 | 47.8 | 100 |  | VS | 3 |
| Detect Thoughts | 102 | 48 | 100 | yes | VSM | 3 |
| Locate Animals or Plants | 99.1 | 50.9 | 100 |  | VSM | 3 |
| Knock | 99 | 51 | 100 |  | V | 3 |
| Lesser Restoration | 98.4 | 51.6 | 100 |  | VS | 5 |
| Augury | 88.6 | 61.4 | 100 |  | VSM | 1 |

Full line items for any spell: `python tools/pointbuy.py score <spell-file-name>`, for example `score fire-bolt`. The same data is in `data/spell-scores.csv` and `data/point-buy.json`. Recalibrate after any change to prices or builds with `python tools/pointbuy.py fit`, then `report`.

## Known limits of this model

- Damage is valued by average roll. It does not model how monsters resist or how often a save fails.
- Typical level 1 spells score in the 70s, not 100. The budget is a ceiling set by the strongest spells. See `docs/spell-scaling-analysis.md`.
- Hard control effects are priced by my judgment of how much a lost turn is worth. Not tested at a table. Adjust the condition costs if your group disagrees.
- A few level 2 spells (Web, Barkskin, Blindness/Deafness, Aid) pass as level 1 spells under these rules. See the stress test in the analysis.
- Run `python tools/pointbuy.py check` after any change. It runs the logic checks and the exploit probes and exits non-zero on a failure.
- A limit only refunds points if it matters. DMs should reject a limit that never comes up.
- Utility spells score low because they have little combat value. That is not a mistake. Raise their duration or area for a stronger version.
- Levels 3 to 9 are not modeled.

