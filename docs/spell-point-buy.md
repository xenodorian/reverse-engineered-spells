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
| Magnitude caps | Damage, healing, temporary HP, extra targets, AC, and other scalable items cannot exceed the highest value used at that level in the existing spells, carried up from lower levels. This stops a spell from buying more damage than any spell of its level has. |
| Control cap | Strong conditions (charmed, blinded, restrained, paralyzed, and so on) together cannot cost more than the cap for the level. |
| Convex price | Damage, healing, extra targets, and AC rise faster than linearly. Price is proportional to amount to the power 1.4, so doubling an amount more than doubles its price. |
| Flat items | A flat item can be taken once. No stacking. |
| Limit refund cap | Refunds from limits cannot exceed 50% of the effect cost. |
| Upcasting | List the increase per slot level. It costs 50% of buying that increase outright. Extra targets rise by at most 1 per slot level. A damage, healing, or temporary HP increase cannot exceed the base amount per slot level. Scaling in other ways pays a flat charge. |

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
| Average net cost, concentration spells | 14 | 77 | 112 |
| Average net cost, other spells | 20 | 72 | 116 |
| Average net cost, spells with a material | 19 | 75 | 114 |
| Average net cost, spells with no material | 18 | 73 | 114 |

Takeaways: nearly every spell has a verbal component, most have a somatic one, and about half have a material. Materials are common, so a mundane material refunds little. Gold-cost materials are rare and start at level 1, so they refund heavily. Spells with materials do not score higher than spells without in this set, so the data does not by itself show that materials mark stronger spells. The larger refund for gold-cost materials follows the design rule that costly components limit power, not a trend in these files. Concentration spells are the long-duration ones, so the concentration refund offsets part of the duration cost.

## Price tables (points you spend)

Prices are base price times a calibrated category multiplier. "Points" is the price of one use. Items marked with a reference amount use the convex curve, and the price shown is at that reference amount. Use the curve table below for other amounts.

### Damage and delivery

| Item | Points | Unit | Available from |
|---|---|---|---|
| Damage dealt | 39.7 | per avg damage (at 10.5) | Level 1+ |
| Repeat damage on later turns | 39.7 | per avg damage (at 10.5) | Level 1+ |
| Extra damage on each weapon hit | 42.3 | per avg damage (at 3.5) | Level 1+ |
| Damage for each 5 ft moved in the area | 22.7 | per avg damage (at 5) | Level 2+ |
| Half damage on a miss | 6 | flat | Level 2+ |
| Delivered by attack roll | 0 | flat | Cantrip+ |
| Delivered by save, half on success | 3.8 | flat | Level 1+ |
| Hits automatically | 9.1 | flat | Level 1+ |
| Cantrip damage (average 6.5 or less) | 11.2 | per avg damage (at 5.5) | Cantrip+ |

### Healing

| Item | Points | Unit | Available from |
|---|---|---|---|
| Hit points restored (modifier assumed +3) | 30.3 | per avg HP (at 7.5) | Level 1+ |
| Temporary hit points | 21 | per HP (at 6.5) | Level 1+ |
| Temporary hit points renewed each turn | 6.5 | per HP per turn | Level 1+ |

### Buffs and debuffs

| Item | Points | Unit | Available from |
|---|---|---|---|
| Armor Class bonus | 40.8 | per +1 AC (at 3) | Level 1+ |
| d4 bonus to attacks and saves | 28.9 | per target | Level 1+ |
| Attacks against target have advantage | 24.6 | flat | Level 1+ |
| Advantage on one next attack | 17.8 | flat | Level 1+ |
| Disadvantage vs six creature types plus charm and fear immunity | 39.9 | flat | Level 1+ |
| Immune to frightened | 8.5 | flat | Level 1+ |
| Walking speed bonus | 1.7 | per foot | Level 1+ |
| Dash as bonus action each turn | 28.9 | flat | Level 1+ |
| Triple jump distance | 6.8 | flat | Level 1+ |
| Negate falling damage and slow fall | 13.6 | flat | Level 1+ |
| Immune to one named spell | 4.2 | flat | Level 1+ |
| Attackers have disadvantage against you | 63.7 | flat | Level 2+ |
| Invisible until you attack or cast | 84.9 | flat | Level 2+ |
| Three duplicates that absorb attacks | 67.9 | flat | Level 2+ |
| Teleport up to 30 ft | 46.7 | flat | Level 2+ |
| Weapon becomes magical, +1 to hit and damage | 46.7 | flat | Level 2+ |
| Resist all damage, +1 AC and saves for one ally | 76.4 | flat | Level 2+ |
| Advantage on one ability's checks plus a perk | 34 | flat | Level 2+ |
| Grow or shrink a creature with combat benefits | 46.7 | flat | Level 2+ |
| +10 Stealth and untrackable for a group | 50.9 | flat | Level 2+ |
| Advantage on your next attack against one target | 8.5 | flat | Cantrip+ |
| d4 on one ability check | 11.9 | flat | Cantrip+ |
| d4 on one saving throw | 11.9 | flat | Cantrip+ |
| Enchant a club or staff (spell modifier, d8, magical) | 11 | flat | Cantrip+ |

### Conditions and control

| Item | Points | Unit | Available from |
|---|---|---|---|
| Prone | 10 | flat | Level 1+ |
| Charmed | 31 | flat | Level 1+ |
| Frightened | 31 | flat | Level 1+ |
| Blinded | 31 | flat | Level 1+ |
| Restrained | 36 | flat | Level 1+ |
| Incapacitated | 72 | flat | Level 1+ |
| Unconscious | 48 | flat | Level 1+ |
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
| Sense a category within 30 ft | 37.4 | flat | Level 1+ |
| Learn aura or school of what you sense | 14.4 | flat | Level 1+ |
| Reveal properties or lore | 47.5 | per item | Level 1+ |
| Understand any language | 37.4 | flat | Level 1+ |
| Speak with a creature type | 33.1 | flat | Level 1+ |
| Create or destroy water | 18.7 | flat | Level 1+ |
| Purify food and drink | 14.4 | flat | Level 1+ |
| Day of food | 18.7 | flat | Level 1+ |
| Alert when an area is entered | 25.9 | flat | Level 1+ |
| Ward that redirects attackers | 67.7 | flat | Level 1+ |
| Create a visual illusion | 67.7 | flat | Level 1+ |
| Change your appearance | 67.7 | flat | Level 1+ |
| Hidden writing | 37.4 | flat | Level 1+ |
| Invisible helper that does chores | 60.5 | flat | Level 1+ |
| Summon a loyal scout and helper | 74.9 | flat | Level 1+ |
| Advantage to track a marked target | 11.5 | flat | Level 1+ |
| Move effect to a new target | 7.2 | flat | Level 1+ |
| Effect lasts until dismissed | 23 | flat | Level 1+ |
| Reshape your body: gills, new face, or claws | 79.2 | flat | Level 2+ |
| Tiny beast carries a message | 43.2 | flat | Level 2+ |
| Magically lock a door or container | 43.2 | flat | Level 2+ |
| Falsify what detection magic reads | 43.2 | flat | Level 2+ |
| Learn weal or woe of a plan | 43.2 | flat | Level 2+ |
| Suppress charm and fear or pacify hostility | 86.4 | flat | Level 2+ |
| Permanent heatless flame | 17.3 | flat | Level 2+ |
| Magical darkness | 64.8 | flat | Level 2+ |
| Darkvision 60 ft | 37.4 | flat | Level 2+ |
| Read surface thoughts or probe a mind | 72 | flat | Level 2+ |
| Hold attention, others unnoticed | 43.2 | flat | Level 2+ |
| Sense traps in sight | 37.4 | flat | Level 2+ |
| Preserve a corpse | 37.4 | flat | Level 2+ |
| Open a lock or bar | 43.2 | flat | Level 2+ |
| End a disease or a condition | 72 | flat | Level 2+ |
| Float a creature or object 20 ft | 57.6 | flat | Level 2+ |
| Locate nearby animals or plants | 43.2 | flat | Level 2+ |
| Locate a familiar or named object | 57.6 | flat | Level 2+ |
| Stored spoken message with a trigger | 43.2 | flat | Level 2+ |
| Neutralize poison, advantage and resistance | 57.6 | flat | Level 2+ |
| Hidden extradimensional refuge for eight | 100.8 | flat | Level 2+ |
| See invisible and ethereal | 72 | flat | Level 2+ |
| Climb walls and ceilings | 43.2 | flat | Level 2+ |
| Zone with no sound | 86.4 | flat | Level 2+ |
| Creatures cannot speak lies | 72 | flat | Level 2+ |
| Create light | 4.3 | flat | Cantrip+ |
| Four movable lights | 17.3 | flat | Cantrip+ |
| Spectral hand, 10 lb, 30 ft | 14.4 | flat | Cantrip+ |
| Repair one small break | 17.3 | flat | Cantrip+ |
| Whispered message to one creature | 11.5 | flat | Cantrip+ |
| Small image or sound | 14.4 | flat | Cantrip+ |
| Several minor magical tricks | 7.2 | flat | Cantrip+ |
| Minor nature effects | 20.2 | flat | Cantrip+ |
| Minor wonders | 14.4 | flat | Cantrip+ |
| Stabilize a dying creature | 17.3 | flat | Cantrip+ |
| Hurl the effect 30 ft | 2.9 | flat | Cantrip+ |

### Targets and area

| Item | Points | Unit | Available from |
|---|---|---|---|
| Each additional target | 20 | per extra target (at 2) | Cantrip+ |
| Split effect among several targets | 10 | flat | Level 1+ |
| 5 ft cube | 4 | flat | Cantrip+ |
| 5 ft radius | 8 | flat | Level 2+ |
| 10 ft square | 13 | flat | Level 1+ |
| 10 ft radius | 20 | flat | Level 2+ |
| 15 ft cone | 18 | flat | Level 1+ |
| 15 ft cube | 18 | flat | Level 1+ |
| 15 ft radius | 28 | flat | Level 2+ |
| 20 ft square | 23 | flat | Level 1+ |
| 20 ft cube | 23 | flat | Level 1+ |
| 20 ft radius | 26 | flat | Level 1+ |
| 30 ft radius | 31 | flat | Level 1+ |
| 60 ft line | 30 | flat | Level 2+ |

### Convex price curves

Price for an amount `q` is `base x q x (q / reference)^0.4 x category multiplier`.

| Average damage | Level 1 or 2 damage price | Healing price at the same amount |
|---|---|---|
| 4.5 | 12.1 | 14.8 |
| 7 | 22.5 | 27.5 |
| 10.5 | 39.7 | 48.6 |
| 14 | 59.4 | 72.7 |
| 16.5 | 74.7 | 91.5 |
| 21 | 104.7 | 128.2 |

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
| 150 feet | 9 |

### Casting time

| Casting time | Points |
|---|---|
| 1 action | 0 |
| 1 bonus action | 10.7 |
| 1 reaction | 13.3 |
| 1 minute | -5.3 |
| 10 minutes | -10.7 |
| 1 hour | -16 |

A longer casting time is a refund. A bonus action or reaction costs more because it stacks with your other actions.

### Duration

| Duration | Points |
|---|---|
| Instantaneous | 0 |
| 1 round | 2.9 |
| 1 minute | 9.7 |
| 10 minutes | 15.5 |
| 1 hour | 21.3 |
| 8 hours | 27.2 |
| 24 hours | 31 |
| 10 days | 34.9 |
| Until dispelled | 38.8 |

### Other costs

| Item | Points |
|---|---|
| Ritual casting (cast without a slot) | 8.7 |
| Flat upcast charge, cantrip scaling with character level | 5.2 |
| Flat upcast charge, level 1 | 8.7 |
| Flat upcast charge, level 2 | 13.9 |

Cantrip scaling is scored at the base tier only. Extra dice at levels 5, 11, and 17 are covered by the flat charge. Listed upcast increases (see the rules) replace the flat charge.

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
| over 250 gp | -14.9 | -22.3 |

A consumed material refunds 1.5 times as much, because the caster pays again on every cast.

### Caveats and limits

| Limit | Refund |
|---|---|
| Willing target only | -1.7 |
| Restricted to a creature type or trait | -3.5 |
| Excludes a creature type (undead, constructs, low Int) | -1.2 |
| Ends if you or allies harm the target | -4.6 |
| Ends if the target attacks or casts | -4.6 |
| Ends on damage or a shake | -3.5 |
| Target repeats the save | -3.5 |
| Target gets advantage on the save in some cases | -2.3 |
| Target knows it was affected afterward | -2.3 |
| Target can use an action to escape | -3.5 |
| Effect capped by a hit point pool | -5.8 |
| Target refuses harmful orders | -2.3 |
| Narrow reaction trigger | -3.5 |
| Effect is easy to kill or dispel | -2.3 |
| Effect decays or expires early | -1.7 |
| Benefit delivered one piece at a time | -3.5 |
| No direct combat use | -3.5 |
| Revealed by touch or an Investigation check | -3.5 |
| Ends if armor is worn | -1.7 |
| Limited to one sense | -1.7 |
| Save negates the whole effect | -2.3 |
| Action each turn to keep it going | -4.6 |
| Blocked by thin barriers | -1.7 |
| Result depends on creature reactions | -2.3 |
| Loud, reveals your position | -1.2 |
| Cosmetic or trivial effects only | -3.5 |
| Effect ends when used | -4.6 |
| Breaks if the target leaves range | -1.2 |
| You take the damage the target takes | -8.1 |

### Concentration and class availability

| Item | Points |
|---|---|
| Concentration | -5.1 |
| On 1 class list | -2.5 |
| On 2 or 3 class lists | -1.2 |
| On 4 or 5 class lists | 0 |
| On 6 or more class lists | +1.9 |

Use concentration only if the spell lasts a minute or more.

## Worked examples

### Fire Bolt: 24 of 25 points

| Type | Item | Points |
|---|---|---|
| Effect | Cantrip damage (average 6.5 or less) x5.5 | +11.2 |
| Effect | Delivered by attack roll | +0 |
| Effect | Ignites loose flammables | +3 |
| Delivery | Range: 120 feet | +8 |
| Delivery | Casting time: 1 action | +0 |
| Duration | Duration: Instantaneous | +0 |
| Delivery | Scales with level | +5.2 |
| Refund | V component | -1.1 |
| Refund | S component | -1.1 |
| Availability | On 2 class lists | -1.2 |

### Magic Missile: 70.8 of 100 points

| Type | Item | Points |
|---|---|---|
| Effect | Damage dealt x10.5 | +39.7 |
| Effect | Hits automatically | +9.1 |
| Effect | Split effect among several targets | +10 |
| Delivery | Range: 120 feet | +8 |
| Delivery | Casting time: 1 action | +0 |
| Duration | Duration: Instantaneous | +0 |
| Delivery | Upcasting: +3.5 damage dealt per slot level | +7.4 |
| Refund | V component | -1.1 |
| Refund | S component | -1.1 |
| Availability | On 2 class lists | -1.2 |

### Hold Person: 107.2 of 150 points

| Type | Item | Points |
|---|---|---|
| Effect | Paralyzed | +95 |
| Limit | Target repeats the save | -3.5 |
| Limit | Restricted to a creature type or trait | -3.5 |
| Floor | Level 2 effect floor (effects must total 100) | +5 |
| Delivery | Range: 60 feet | +5 |
| Delivery | Casting time: 1 action | +0 |
| Duration | Duration: 1 minute | +9.7 |
| Refund | Concentration | -5.1 |
| Delivery | Upcasting: +1 each additional target per slot level | +6.6 |
| Refund | V component | -1.1 |
| Refund | S component | -1.1 |
| Refund | Material component (no cost) | -1.7 |
| Availability | On 6 class lists | +1.9 |

## Scorecard: 24 cantrips

| Spell | Net cost | Left | Effects | Conc. | Comp. | Classes |
|---|---|---|---|---|---|---|
| Shillelagh | 25 | 0 | 11 |  | VSM | 1 |
| Mage Hand | 24.9 | 0.1 | 14.4 |  | VS | 4 |
| Dancing Lights | 24.8 | 0.2 | 17.3 | yes | VSM | 3 |
| Prestidigitation | 24.7 | 0.3 | 7.2 |  | VS | 4 |
| Chill Touch | 24.2 | 0.8 | 11.5 |  | VS | 3 |
| Produce Flame | 24.2 | 0.8 | 12.8 |  | VS | 1 |
| Fire Bolt | 24 | 1 | 14.2 |  | VS | 2 |
| Minor Illusion | 23.1 | 1.9 | 18.4 |  | SM | 4 |
| Light | 22.8 | 2.2 | 4.3 |  | VM | 4 |
| Ray of Frost | 21.3 | 3.7 | 14.5 |  | VS | 2 |
| Thaumaturgy | 20 | 5 | 14.4 |  | V | 1 |
| Eldritch Blast | 19.7 | 5.3 | 11.2 |  | VS | 1 |
| Shocking Grasp | 18.3 | 6.7 | 16.5 |  | VS | 2 |
| Acid Splash | 18.1 | 6.9 | 13.6 |  | VS | 2 |
| Message | 17.3 | 7.7 | 11.5 |  | VSM | 3 |
| Poison Spray | 16.9 | 8.1 | 14.2 |  | VS | 4 |
| Vicious Mockery | 16 | 9 | 11.7 |  | V | 1 |
| Druidcraft | 15 | 10 | 20.2 |  | VS | 1 |
| Sacred Flame | 14.7 | 10.3 | 11.5 |  | VS | 1 |
| Spare the Dying | 12.6 | 12.4 | 17.3 |  | VS | 1 |
| Guidance | 11.4 | 13.6 | 11.9 | yes | VS | 2 |
| Resistance | 9.7 | 15.3 | 11.9 | yes | VSM | 2 |
| True Strike | 8.2 | 16.8 | 8.5 | yes | S | 4 |
| Mending | 8.1 | 16.9 | 17.3 |  | VSM | 5 |

## Scorecard: 49 level 1 spells

| Spell | Net cost | Left | Effects | Conc. | Comp. | Classes |
|---|---|---|---|---|---|---|
| Hunter's Mark | 100 | 0 | 61 | yes | V | 1 |
| Sleep | 100 | 0 | 89 |  | VSM | 3 |
| Detect Magic | 99.9 | 0.1 | 82.8 | yes | VS | 7 |
| Shield | 96.8 | 3.2 | 87.5 |  | VS | 2 |
| Bless | 94 | 6 | 86.6 | yes | VSM | 2 |
| Bane | 93.4 | 6.6 | 86.6 | yes | VSM | 2 |
| Guiding Bolt | 90.8 | 9.2 | 77.2 |  | VS | 1 |
| Silent Image | 90.8 | 9.2 | 85.7 | yes | VSM | 3 |
| Feather Fall | 86.9 | 13.1 | 66.4 |  | VM | 3 |
| Unseen Servant | 84.6 | 15.4 | 60.5 |  | VSM | 3 |
| Inflict Wounds | 83.9 | 16.1 | 74.7 |  | VS | 1 |
| Fog Cloud | 82.7 | 17.3 | 52 | yes | VS | 4 |
| Disguise Self | 82.1 | 17.9 | 67.7 |  | VS | 3 |
| Detect Poison and Disease | 81.9 | 18.1 | 68.4 | yes | VSM | 4 |
| Identify | 81.2 | 18.8 | 95 |  | VSM | 2 |
| Find Familiar | 81 | 19 | 97.9 |  | VSM | 1 |
| Sanctuary | 80.1 | 19.9 | 67.7 |  | VSM | 1 |
| False Life | 78.8 | 21.2 | 50 |  | VSM | 2 |
| Illusory Script | 77.9 | 22.1 | 50 |  | SM | 3 |
| Hideous Laughter | 77.5 | 22.5 | 82 | yes | VSM | 2 |
| Animal Friendship | 77.4 | 22.6 | 50 |  | VSM | 3 |
| Alarm | 75 | 25 | 50 |  | VSM | 2 |
| Hellish Rebuke | 74.1 | 25.9 | 50.1 |  | VS | 1 |
| Longstrider | 74 | 26 | 50 |  | VSM | 4 |
| Detect Evil and Good | 73.7 | 26.3 | 68.4 | yes | VS | 2 |
| Comprehend Languages | 72.6 | 27.4 | 50 |  | VSM | 4 |
| Entangle | 72.4 | 27.6 | 69 | yes | VS | 1 |
| Shield of Faith | 71 | 29 | 50 | yes | VSM | 2 |
| Magic Missile | 70.8 | 29.2 | 58.8 |  | VS | 2 |
| Charm Person | 70.6 | 29.4 | 50 |  | VS | 5 |
| Mage Armor | 68.7 | 31.3 | 50 |  | VSM | 2 |
| Burning Hands | 68.5 | 31.5 | 64.5 |  | VS | 2 |
| Healing Word | 67.8 | 32.2 | 50 |  | V | 3 |
| Expeditious Retreat | 67.7 | 32.3 | 50 | yes | VS | 3 |
| Thunderwave | 65.9 | 34.1 | 58.8 |  | VS | 4 |
| Speak with Animals | 65 | 35 | 50 |  | VS | 3 |
| Faerie Fire | 64.9 | 35.1 | 57.6 | yes | V | 2 |
| Color Spray | 64.7 | 35.3 | 64 |  | VSM | 2 |
| Witch Bolt | 64.3 | 35.7 | 50 | yes | VSM | 3 |
| Divine Favor | 60.6 | 39.4 | 50 | yes | VS | 1 |
| Cure Wounds | 59.5 | 40.5 | 50 |  | VS | 5 |
| Command | 58.7 | 41.3 | 50 |  | V | 2 |
| Grease | 58.3 | 41.7 | 50 |  | VSM | 1 |
| Heroism | 56.1 | 43.9 | 50 | yes | VS | 2 |
| Jump | 55.8 | 44.2 | 50 |  | VSM | 4 |
| Protection from Evil and Good | 54.8 | 45.2 | 50 | yes | VSM | 4 |
| Purify Food and Drink | 53.8 | 46.2 | 50 |  | VS | 3 |
| Create or Destroy Water | 53.1 | 46.9 | 50 |  | VSM | 2 |
| Goodberry | 39.7 | 60.3 | 50 |  | VSM | 2 |

## Scorecard: 53 level 2 spells

| Spell | Net cost | Left | Effects | Conc. | Comp. | Classes |
|---|---|---|---|---|---|---|
| Animal Messenger | 144.5 | 5.5 | 100 |  | VSM | 3 |
| Scorching Ray | 138.8 | 11.2 | 114.7 |  | VS | 2 |
| Aid | 137.7 | 12.3 | 100 |  | VSM | 2 |
| Magic Weapon | 137.4 | 12.6 | 100 | yes | VS | 2 |
| Silence | 136.1 | 13.9 | 112.4 | yes | VS | 3 |
| Gentle Repose | 135 | 15 | 100 |  | VSM | 2 |
| Prayer of Healing | 132.4 | 17.6 | 130.7 |  | V | 2 |
| Magic Mouth | 131.4 | 18.6 | 100 |  | VSM | 2 |
| Spiritual Weapon | 124.7 | 25.3 | 100 |  | VS | 1 |
| Arcane Lock | 123.8 | 26.2 | 100 |  | VSM | 1 |
| Continual Flame | 121.6 | 28.4 | 100 |  | VSM | 2 |
| Darkvision | 121.6 | 28.4 | 100 |  | VSM | 4 |
| Arcanist's Magic Aura | 121.1 | 28.9 | 100 |  | VSM | 1 |
| Moonbeam | 120.2 | 29.8 | 100.1 | yes | VSM | 1 |
| Protection from Poison | 119.1 | 30.9 | 100 |  | VS | 4 |
| Enhance Ability | 118.9 | 31.1 | 100 | yes | VSM | 4 |
| Flame Blade | 117.5 | 32.5 | 100 | yes | VSM | 1 |
| Zone of Truth | 117.1 | 32.9 | 100 |  | VS | 3 |
| Calm Emotions | 116.9 | 33.1 | 112.4 | yes | VS | 2 |
| See Invisibility | 116.2 | 33.8 | 100 |  | VSM | 3 |
| Suggestion | 115.4 | 34.6 | 100 | yes | VM | 4 |
| Blindness/Deafness | 114.7 | 35.3 | 100 |  | V | 4 |
| Invisibility | 114.3 | 35.7 | 100 | yes | VSM | 4 |
| Spike Growth | 114.3 | 35.7 | 100 | yes | VSM | 2 |
| Alter Self | 112.8 | 37.2 | 100 | yes | VS | 2 |
| Acid Arrow | 112.7 | 37.3 | 99.9 |  | VSM | 1 |
| Rope Trick | 112.2 | 37.8 | 100.8 |  | VSM | 1 |
| Flaming Sphere | 111.9 | 38.1 | 100 | yes | VSM | 2 |
| Darkness | 111.4 | 38.6 | 100 | yes | VM | 3 |
| Pass without Trace | 111.1 | 38.9 | 100 | yes | VSM | 2 |
| Shatter | 110.4 | 39.6 | 100 |  | VSM | 4 |
| Levitate | 110.3 | 39.7 | 100 | yes | VSM | 2 |
| Web | 110.3 | 39.7 | 100 | yes | VSM | 2 |
| Barkskin | 109.4 | 40.6 | 100 | yes | VSM | 2 |
| Spider Climb | 109.4 | 40.6 | 100 | yes | VSM | 3 |
| Enthrall | 109 | 41 | 100 |  | VS | 2 |
| Misty Step | 108.4 | 41.6 | 100 |  | V | 3 |
| Hold Person | 107.2 | 42.8 | 100 | yes | VSM | 6 |
| Heat Metal | 107 | 43 | 100.1 | yes | VSM | 2 |
| Mirror Image | 106.3 | 43.7 | 100 |  | VS | 3 |
| Locate Object | 104.9 | 45.1 | 100 | yes | VSM | 6 |
| Enlarge/Reduce | 103.7 | 46.3 | 100 | yes | VSM | 4 |
| Ray of Enfeeblement | 102.7 | 47.3 | 100 | yes | VS | 2 |
| Blur | 102.3 | 47.7 | 100 | yes | V | 2 |
| Find Traps | 101.1 | 48.9 | 100 |  | VS | 3 |
| Locate Animals or Plants | 100.1 | 49.9 | 100 |  | VSM | 3 |
| Gust of Wind | 99.5 | 50.5 | 100 | yes | VSM | 3 |
| Crown of Madness | 98.8 | 51.2 | 100 | yes | VS | 4 |
| Knock | 98 | 52 | 100 |  | V | 3 |
| Lesser Restoration | 97.8 | 52.2 | 100 |  | VS | 5 |
| Warding Bond | 97.8 | 52.2 | 100 |  | VSM | 2 |
| Detect Thoughts | 97.2 | 52.8 | 100 | yes | VSM | 3 |
| Augury | 86 | 64 | 100 |  | VSM | 1 |

Full line items for any spell: `python tools/pointbuy.py score <spell-file-name>`, for example `score fire-bolt`. The same data is in `data/spell-scores.csv` and `data/point-buy.json`. Recalibrate after any change to prices or builds with `python tools/pointbuy.py fit`, then `report`.

## Known limits of this model

- Damage is valued by average roll. It does not model how monsters resist or how often a save fails.
- Typical level 1 spells score in the 70s, not 100. The budget is a ceiling set by the strongest spells. See `docs/spell-scaling-analysis.md`.
- Hard control effects are priced by my judgment of how much a lost turn is worth. Not tested at a table. Adjust the condition costs if your group disagrees.
- A few level 2 spells (Web, Barkskin, Blindness/Deafness, Aid) pass as level 1 spells under these rules. See the stress test in the analysis.
- A limit only refunds points if it matters. DMs should reject a limit that never comes up.
- Utility spells score low because they have little combat value. That is not a mistake. Raise their duration or area for a stronger version.
- Levels 3 to 9 are not modeled.

