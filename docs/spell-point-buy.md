# Spell Point Buy

A point budget system for building cantrips and 1st-level spells. A cantrip gets **25 points**. A 1st-level spell gets **100 points**. Effects, range, and duration cost points. Components and limits give points back. A spell is legal if its net cost is at or under its budget.

> This is a homebrew tool. The numbers are my own design, tuned against the 24 cantrips in `spells/cantrip/` and the 49 level 1 spells in `spells/level-1/`. They are not official. The DMG guidance they lean on was summarized from memory and is unverified (see `docs/creating-a-spell.md`). The spell files themselves were also written from memory and are not checked against the books. Playtest before trusting any score.

## The cantrip and level 1 clearance rules

Two rules keep a firm gap between the tiers. "Effects" means the capability lines only: damage, healing, conditions, utility, targets, and area. Range, casting time, duration, and refunds are not counted.

| Rule | Applies to | What it does |
|---|---|---|
| Level 1 floor | Level 1 spells | Effects must total at least 50. If they total less, you pay the gap as a "Level 1 effect floor" line. So anything a level 1 spell does costs 50 or more at its level 1 strength. |
| Cantrip ceiling | Cantrips | Effects must total 49 or less. The calculator rejects a cantrip above that, because it would be level 1 strength. |
| Cantrip tier items | Cantrips | A cantrip can only use the cantrip-scale effects and the shared items in the tables below. Level 1 effect items are blocked. |
| Cantrip damage cap | Cantrips | Cantrip damage tops out at an average of 6.5 (1d12). Level 1 damage starts at about 10. |
| Limit refund cap | Both | Refunds from limits cannot exceed 50% of the effect cost. This stops a trivial effect from being bought for free by stacking caveats. |

Result on the current spells: the highest cantrip effect total is 21.5. 25 of the 49 level 1 spells needed the floor top-up: Alarm, Animal Friendship, Charm Person, Command, Comprehend Languages, Create or Destroy Water, Cure Wounds, Disguise Self, Divine Favor, Expeditious Retreat, False Life, Grease, Healing Word, Heroism, Identify, Illusory Script, Jump, Longstrider, Mage Armor, Protection from Evil and Good, Purify Food and Drink, Sanctuary, Shield of Faith, Speak with Animals, Unseen Servant.

## How to build a spell in six steps

1. **Pick the level.** Cantrip budget is 25. Level 1 budget is 100.
2. **Pick the effect.** Add up the costs from the effect tables. Multiply per-unit items by their quantity. Check the floor or ceiling rule.
3. **Pick delivery.** Add the cost of range, casting time, and duration. Add area or extra target costs.
4. **Add components.** Components are refunds. Material components with a gold cost refund the most.
5. **Add limits.** Each caveat that really constrains the spell refunds points, up to the cap. Do not claim a limit that never matters.
6. **Add up.** Net cost = effects + delivery + duration - refunds. Stay at or below budget, then playtest.

Skip the arithmetic with the calculator: `python tools/pointbuy.py calc examples/new-spell.json` or `examples/new-cantrip.json`. Set `"level": 0` for a cantrip.

### Reading a score

| Tier | Net cost | Meaning |
|---|---|---|
| Level 1 | Over 100 | Over budget. Add limits or cut effects. |
| Level 1 | 85 to 100 | Premium. Among the best first-level spells (Guiding Bolt, Bless, Sleep). |
| Level 1 | 55 to 84 | Standard. Solid, reliable spells. |
| Level 1 | Under 55 | Utility or situational. You have headroom: spend unused points on range, duration, or targets. |
| Cantrip | Over 25 | Over budget. |
| Cantrip | 20 to 25 | Strong cantrip. Reliable damage or a flexible effect (Fire Bolt, Shillelagh). |
| Cantrip | Under 20 | Minor or niche. Room to add range or a rider. |

## What the existing spells show

Counted from the spell files, and used to set the refund sizes below.

| Pattern | Cantrips (24) | Level 1 (49) |
|---|---|---|
| Verbal component | 22 of 24 | 48 of 49 |
| Somatic component | 21 of 24 | 44 of 49 |
| Material component | 7 of 24 | 26 of 49 |
| Material with a gold cost | 0 of 24 | 3 of 49 |
| Concentration | 4 of 24 | 17 of 49 |
| Ritual | 0 of 24 | 10 of 49 |
| Has an at-higher-levels clause | 10 of 24 | 22 of 49 |
| Cast as an action | 22 of 24 | 36 of 49 |
| Cast as a bonus action or reaction | 1 of 24 | 9 of 49 |
| Cast time of a minute or more | 1 of 24 | 4 of 49 |
| Instantaneous duration | 11 of 24 | 12 of 49 |
| Average classes per spell | 2.4 | 2.6 |
| Spells on exactly one class list | 8 of 24 | 9 of 49 |
| Average net cost, concentration spells | 6 | 65 |
| Average net cost, other spells | 17 | 63 |
| Average net cost, spells with a material | 13 | 62 |
| Average net cost, spells with no material | 16 | 66 |

Takeaways: nearly every spell has a verbal component, most have a somatic one, and about half have a material. Materials are common, so a mundane material refunds little. Gold-cost materials are rare (3 level 1 spells, no cantrips), so they refund heavily. Spells with materials do not score higher than spells without in this set, so the data does not by itself show that materials mark stronger spells. The larger refund for gold-cost materials follows the design rule that costly components limit power, not a trend in these files. Concentration spells are the long-duration ones, so the concentration refund offsets part of the duration cost. Cantrips never use rituals and rarely use concentration. About half of damage cantrips scale with character level, which is why scaling has its own cantrip price.

## Cost tables (points you spend)

### Level 1 effects

These are level 1 only, except the items marked shared, which cantrips may also use.

#### Damage and healing

| Item | Points | Unit | Cantrips? |
|---|---|---|---|
| Damage dealt | 5 | per avg damage | no |
| Extra damage on each weapon hit | 16 | per avg damage | no |
| Repeat damage on later turns | 5 | per avg damage | no |
| Hit points restored (modifier assumed +3) | 5 | per avg HP | no |
| Temporary hit points | 4 | per HP | no |
| Temporary hit points renewed each turn | 8 | per HP per turn | no |

#### Delivery of a damaging effect

| Item | Points | Unit | Cantrips? |
|---|---|---|---|
| Delivered by attack roll | 0 | flat | shared |
| Delivered by save, half on success | 5 | flat | no |
| Hits automatically | 12 | flat | no |
| Condition with no save or roll | 15 | flat | no |

#### Buffs, debuffs and movement

| Item | Points | Unit | Cantrips? |
|---|---|---|---|
| Armor Class bonus | 16 | per +1 AC | no |
| d4 bonus to attacks and saves | 34 | per target | no |
| Attacks against target have advantage | 29 | flat | no |
| Advantage on one next attack | 21 | flat | no |
| Disadvantage vs six creature types plus charm and fear immunity | 47 | flat | no |
| Immune to frightened | 10 | flat | no |
| Walking speed bonus | 2 | per foot | no |
| Dash as bonus action each turn | 34 | flat | no |
| Triple jump distance | 8 | flat | no |
| Negate falling damage and slow fall | 16 | flat | no |
| Immune to one named spell | 5 | flat | no |

#### Conditions (per target)

| Item | Points | Unit | Cantrips? |
|---|---|---|---|
| Prone | 10 | flat | no |
| Charmed | 31 | flat | no |
| Frightened | 31 | flat | no |
| Blinded | 31 | flat | no |
| Restrained | 36 | flat | no |
| Incapacitated | 72 | flat | no |
| Unconscious | 52 | flat | no |
| Forced to obey a one word order | 29 | flat | no |
| Forced movement up to 10 ft | 5 | flat | no |
| Difficult terrain | 10 | flat | no |
| Heavily obscured area | 26 | flat | no |
| Outlines target, negates invisibility | 10 | flat | no |
| Ignites loose flammables | 3 | flat | shared |

#### Utility

| Item | Points | Unit | Cantrips? |
|---|---|---|---|
| Sense a category within 30 ft | 26 | flat | no |
| Learn aura or school of what you sense | 10 | flat | no |
| Reveal properties or lore | 21 | per item | no |
| Understand any language | 26 | flat | no |
| Speak with a creature type | 23 | flat | no |
| Create or destroy water | 13 | flat | no |
| Purify food and drink | 10 | flat | no |
| Day of food | 13 | flat | no |
| Alert when an area is entered | 18 | flat | no |
| Ward that redirects attackers | 47 | flat | no |
| Create a visual illusion | 47 | flat | no |
| Change your appearance | 47 | flat | no |
| Hidden writing | 26 | flat | no |
| Invisible helper that does chores | 42 | flat | no |
| Summon a loyal scout and helper | 73 | flat | no |
| Advantage to track a marked target | 8 | flat | no |
| Move effect to a new target | 5 | flat | no |
| Effect lasts until dismissed | 21 | flat | no |

#### Targets and area

| Item | Points | Unit | Cantrips? |
|---|---|---|---|
| Each additional target | 10 | per target | shared |
| Split effect among several targets | 10 | flat | no |
| 10 ft square | 13 | flat | no |
| 20 ft square | 23 | flat | no |
| 15 ft cone | 18 | flat | no |
| 15 ft cube | 18 | flat | no |
| 20 ft cube | 23 | flat | no |
| 20 ft radius | 26 | flat | no |
| 30 ft radius | 31 | flat | no |

### Cantrip effects

Weaker versions of level 1 effects. Cantrips are limited to these and the shared items. Level 1 spells may use them too.

#### Damage and rider effects

| Item | Points | Unit |
|---|---|---|
| Cantrip damage (average 6.5 or less) (max 6.5) | 3 | per avg damage |
| Target speed reduced 10 ft until your next turn | 6 | flat |
| Target cannot regain HP until your next turn | 3 | flat |
| Target cannot take reactions until its next turn | 8 | flat |
| Target has disadvantage on its next attack roll | 8 | flat |
| Advantage on your next attack against one target | 10 | flat |
| Target gets no cover bonus to the save | 3 | flat |

#### Boosts

| Item | Points | Unit |
|---|---|---|
| d4 on one ability check | 14 | flat |
| d4 on one saving throw | 14 | flat |
| Enchant a club or staff (spell modifier, d8, magical) | 18 | flat |

#### Utility

| Item | Points | Unit |
|---|---|---|
| Create light | 4 | flat |
| Four movable lights | 12 | flat |
| Spectral hand, 10 lb, 30 ft | 14 | flat |
| Repair one small break | 12 | flat |
| Whispered message to one creature | 8 | flat |
| Small image or sound | 14 | flat |
| Several minor magical tricks | 10 | flat |
| Minor nature effects | 14 | flat |
| Minor wonders | 10 | flat |
| Stabilize a dying creature | 12 | flat |
| Hurl the effect 30 ft | 3 | flat |

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

### Casting time

| Casting time | Points |
|---|---|
| 1 action | +0 |
| 1 bonus action | +8 |
| 1 reaction | +10 |
| 1 minute | -4 |
| 10 minutes | -8 |
| 1 hour | -12 |

A longer casting time is a refund. A bonus action or reaction costs more because it stacks with your other actions.

### Duration

| Duration | Points |
|---|---|
| Instantaneous | 0 |
| 1 round | 3 |
| 1 minute | 10 |
| 10 minutes | 16 |
| 1 hour | 22 |
| 8 hours | 28 |
| 24 hours | 32 |
| 10 days | 36 |

### Other costs

| Item | Points |
|---|---|
| Ritual casting (cast without a slot) | +5 |
| Scales with higher slots (level 1) | +5 |
| Scales with character level (cantrip) | +3 |

Cantrip scaling is scored at the base tier only. Extra dice at levels 5, 11, and 17 are covered by the scaling charge.

## Refund tables (points you get back)

### Components

| Component | Refund |
|---|---|
| Verbal | -2 |
| Somatic | -2 |
| Material, no stated cost | -3 |

Materials with a stated gold cost replace the plain material refund:

| Cost of material | Refund, kept | Refund, consumed |
|---|---|---|
| 1 to 10 gp | -8 | -12 |
| 11 to 50 gp | -12 | -18 |
| 51 to 100 gp | -18 | -27 |
| 101 to 250 gp | -22 | -33 |
| over 250 gp | -26 | -39 |

A consumed material refunds 1.5 times as much, because the caster pays again on every cast.

### Caveats and limits

| Limit | Refund |
|---|---|
| Willing target only | -3 |
| Restricted to a creature type or trait | -6 |
| Excludes a creature type (undead, constructs, low Int) | -2 |
| Ends if you or allies harm the target | -8 |
| Ends if the target attacks or casts | -8 |
| Ends on damage or a shake | -6 |
| Target repeats the save | -6 |
| Target gets advantage on the save in some cases | -4 |
| Target knows it was affected afterward | -4 |
| Target can use an action to escape | -6 |
| Effect capped by a hit point pool | -10 |
| Target refuses harmful orders | -4 |
| Narrow reaction trigger | -6 |
| Effect is easy to kill or dispel | -4 |
| Effect decays or expires early | -3 |
| Benefit delivered one piece at a time | -6 |
| No direct combat use | -6 |
| Revealed by touch or an Investigation check | -6 |
| Ends if armor is worn | -3 |
| Limited to one sense | -3 |
| Save negates the whole effect | -4 |
| Action each turn to keep it going | -8 |
| Blocked by thin barriers | -3 |
| Result depends on creature reactions | -4 |
| Loud, reveals your position | -2 |
| Cosmetic or trivial effects only | -6 |
| Effect ends when used | -8 |
| Breaks if the target leaves range | -2 |

### Class availability

| Spell is on this many class lists | Points |
|---|---|
| 1 | -4 |
| 2 or 3 | -2 |
| 4 or 5 | 0 |
| 6 or more | +3 |

Concentration refunds 10 points. Use it only if the spell lasts a minute or more.

## Worked examples

### Fire Bolt: 24.5 of 25 points

| Type | Item | Points |
|---|---|---|
| Effect | Cantrip damage (average 6.5 or less) x5.5 | +16.5 |
| Effect | Delivered by attack roll | +0 |
| Effect | Ignites loose flammables | +3 |
| Delivery | Range: 120 feet | +8 |
| Delivery | Casting time: 1 action | +0 |
| Duration | Duration: Instantaneous | +0 |
| Delivery | Scales with level | +3 |
| Refund | V component | -2 |
| Refund | S component | -2 |
| Availability | On 2 class lists | -2 |

### Magic Missile: 81.5 of 100 points

| Type | Item | Points |
|---|---|---|
| Effect | Damage dealt x10.5 | +52.5 |
| Effect | Hits automatically | +12 |
| Effect | Split effect among several targets | +10 |
| Delivery | Range: 120 feet | +8 |
| Delivery | Casting time: 1 action | +0 |
| Duration | Duration: Instantaneous | +0 |
| Delivery | Scales with higher slots | +5 |
| Refund | V component | -2 |
| Refund | S component | -2 |
| Availability | On 2 class lists | -2 |

### Sleep: 90 of 100 points

| Type | Item | Points |
|---|---|---|
| Effect | Unconscious | +52 |
| Effect | 20 ft radius | +26 |
| Effect | Condition with no save or roll | +15 |
| Limit | Effect capped by a hit point pool | -10 |
| Limit | Ends on damage or a shake | -6 |
| Delivery | Range: 90 feet | +7 |
| Delivery | Casting time: 1 action | +0 |
| Duration | Duration: 1 minute | +10 |
| Delivery | Scales with higher slots | +5 |
| Refund | V component | -2 |
| Refund | S component | -2 |
| Refund | Material component (no cost) | -3 |
| Availability | On 3 class lists | -2 |

## Scorecard: 24 cantrips

| Spell | Net cost | Left | Effects | Conc. | Comp. | Classes |
|---|---|---|---|---|---|---|
| Prestidigitation | 25 | 0 | 10 |  | VS | 4 |
| Shillelagh | 25 | 0 | 18 |  | VSM | 1 |
| Chill Touch | 24.5 | 0.5 | 16.5 |  | VS | 3 |
| Fire Bolt | 24.5 | 0.5 | 19.5 |  | VS | 2 |
| Produce Flame | 23.5 | 1.5 | 20.5 |  | VS | 1 |
| Mage Hand | 23 | 2 | 14 |  | VS | 4 |
| Ray of Frost | 21.5 | 3.5 | 19.5 |  | VS | 2 |
| Light | 21 | 4 | 4 |  | VM | 4 |
| Minor Illusion | 20 | 5 | 18 |  | SM | 4 |
| Eldritch Blast | 19.5 | 5.5 | 16.5 |  | VS | 1 |
| Acid Splash | 18.5 | 6.5 | 20.5 |  | VS | 2 |
| Shocking Grasp | 18.5 | 6.5 | 21.5 |  | VS | 2 |
| Poison Spray | 16.5 | 8.5 | 19.5 |  | VS | 4 |
| Vicious Mockery | 13.5 | 11.5 | 15.5 |  | V | 1 |
| Sacred Flame | 12.5 | 12.5 | 16.5 |  | VS | 1 |
| Thaumaturgy | 12 | 13 | 10 |  | V | 1 |
| Dancing Lights | 11 | 14 | 12 | yes | VSM | 3 |
| Message | 10 | 15 | 8 |  | VSM | 3 |
| Guidance | 5 | 20 | 14 | yes | VS | 2 |
| Spare the Dying | 4 | 21 | 12 |  | VS | 1 |
| True Strike | 4 | 21 | 10 | yes | S | 4 |
| Druidcraft | 3 | 22 | 14 |  | VS | 1 |
| Resistance | 2 | 23 | 14 | yes | VSM | 2 |
| Mending | 1 | 24 | 12 |  | VSM | 5 |

## Scorecard: 49 level 1 spells

| Spell | Net cost | Left | Effects | Conc. | Comp. | Classes |
|---|---|---|---|---|---|---|
| Guiding Bolt | 99 | 1 | 91 |  | VS | 1 |
| Bless | 98 | 2 | 102 | yes | VSM | 2 |
| Bane | 97 | 3 | 102 | yes | VSM | 2 |
| Hunter's Mark | 95 | 5 | 69 | yes | V | 1 |
| Sleep | 90 | 10 | 93 |  | VSM | 3 |
| Shield | 86 | 14 | 85 |  | VS | 2 |
| Magic Missile | 81.5 | 18.5 | 74.5 |  | VS | 2 |
| Inflict Wounds | 79.5 | 20.5 | 82.5 |  | VS | 1 |
| Burning Hands | 77.5 | 22.5 | 78.5 |  | VS | 2 |
| Detect Magic | 74 | 26 | 67 | yes | VS | 7 |
| Fog Cloud | 73 | 27 | 52 | yes | VS | 4 |
| Thunderwave | 72 | 28 | 73 |  | VS | 4 |
| Longstrider | 70 | 30 | 20 |  | VSM | 4 |
| Find Familiar | 69 | 31 | 94 |  | VSM | 1 |
| Illusory Script | 69 | 31 | 26 |  | SM | 3 |
| False Life | 68 | 32 | 26 |  | VSM | 2 |
| Feather Fall | 68 | 32 | 56 |  | VM | 3 |
| Alarm | 67 | 33 | 41 |  | VSM | 2 |
| Animal Friendship | 67 | 33 | 31 |  | VSM | 3 |
| Hellish Rebuke | 66 | 34 | 60 |  | VS | 1 |
| Comprehend Languages | 64 | 36 | 26 |  | VSM | 4 |
| Hideous Laughter | 64 | 36 | 82 | yes | VSM | 2 |
| Faerie Fire | 63 | 37 | 62 | yes | V | 2 |
| Mage Armor | 63 | 37 | 48 |  | VSM | 2 |
| Unseen Servant | 63 | 37 | 42 |  | VSM | 3 |
| Charm Person | 62 | 38 | 31 |  | VS | 5 |
| Entangle | 62 | 38 | 69 | yes | VS | 1 |
| Healing Word | 62 | 38 | 27.5 |  | V | 3 |
| Disguise Self | 60 | 40 | 47 |  | VS | 3 |
| Shield of Faith | 60 | 40 | 32 | yes | VSM | 2 |
| Detect Poison and Disease | 58 | 42 | 57 | yes | VSM | 4 |
| Expeditious Retreat | 58 | 42 | 34 | yes | VS | 3 |
| Silent Image | 58 | 42 | 65 | yes | VSM | 3 |
| Speak with Animals | 55 | 45 | 23 |  | VS | 3 |
| Detect Evil and Good | 54 | 46 | 57 | yes | VS | 2 |
| Grease | 54 | 46 | 33 |  | VSM | 1 |
| Witch Bolt | 54 | 46 | 65 | yes | VSM | 3 |
| Color Spray | 53 | 47 | 64 |  | VSM | 2 |
| Command | 53 | 47 | 29 |  | V | 2 |
| Jump | 53 | 47 | 8 |  | VSM | 4 |
| Sanctuary | 52 | 48 | 47 |  | VSM | 1 |
| Divine Favor | 50 | 50 | 40 | yes | VS | 1 |
| Cure Wounds | 49 | 51 | 37.5 |  | VS | 5 |
| Heroism | 46 | 54 | 34 | yes | VS | 2 |
| Protection from Evil and Good | 46 | 54 | 47 | yes | VSM | 4 |
| Goodberry | 45 | 55 | 63 |  | VSM | 2 |
| Purify Food and Drink | 45 | 55 | 10 |  | VS | 3 |
| Create or Destroy Water | 43 | 57 | 36 |  | VSM | 2 |
| Identify | 21 | 79 | 42 |  | VSM | 2 |

Full line items for any spell: `python tools/pointbuy.py score <spell-file-name>`, for example `score fire-bolt`. The same data is in `data/spell-scores.csv` and `data/point-buy.json`.

## Known limits of this model

- Damage is valued by average roll. It does not model how monsters resist or how often a save fails.
- Hard control effects may be priced unevenly. Incapacitated (72) now costs more than unconscious (52) because Hideous Laughter has no hit point pool and a target that takes damage gets advantage on its repeat save, while Sleep is capped by a pool and ends on damage. That is my judgment, not tested at a table. Adjust the condition costs if your group disagrees.
- The 50 point floor applies to a spell's whole effect package, not to each item. A single level 1 effect item can cost less than 50 as long as the spell's effects total 50 or more. If you wanted every individual item priced at 50 or more, the level 1 budget would need to rise.
- Cantrip scaling is flat priced. A cantrip that scales much harder than the standard dice steps should pay extra.
- Spell level beyond 1 is not modeled.
- A limit only refunds points if it matters. DMs should reject a limit that never comes up.
- Utility spells such as Identify score low because they have little combat value. That is not a mistake. Raise their duration or area for a stronger version.

