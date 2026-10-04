# Spell Point Buy

A 100 point budget system for building 1st-level 5e style spells. Every spell gets 100 points. Effects, range, and duration cost points. Components and limits give points back. Ritual casting and upcasting cost a few extra. A spell is legal if its net cost is 100 or less.

> This is a homebrew tool. The numbers are my own design, tuned against the 49 spells in `spells/level-1/` so that the strongest first-level spells land near 100. They are not official. The DMG guidance they lean on was summarized from memory and is unverified (see `docs/creating-a-spell.md`). Playtest before trusting any score.

## How to build a spell in six steps

1. **Pick the effect.** Add up the costs from the Effect tables. Multiply per-unit items by their quantity.
2. **Pick delivery.** Add the cost of range, casting time, and duration. Add area or extra target costs.
3. **Add components.** Components are refunds. Material components with a gold cost refund the most.
4. **Add limits.** Each caveat that really constrains the spell refunds points. Do not claim a limit that never matters.
5. **Add up.** Net cost = effects + delivery + duration - refunds. Stay at or below 100.
6. **Check the band** in the table below, then playtest.

Run the calculator to skip the arithmetic: `python tools/pointbuy.py calc examples/new-spell.json`.

### Reading a score

| Net cost | Meaning |
|---|---|
| Over 100 | Over budget. This is a stronger than first-level spell. Add limits or cut effects. |
| 85 to 100 | Premium. Among the best first-level spells (Guiding Bolt, Bless, Sleep). |
| 55 to 84 | Standard. Solid, reliable spells. |
| Under 55 | Utility or situational. You have headroom: spend the unused points on range, duration, or targets. |

## What the existing spells show

Counted from the 49 spell files, and used to set the refund sizes below.

| Pattern | Count |
|---|---|
| Verbal component | 48 of 49 |
| Somatic component | 44 of 49 |
| Material component | 26 of 49 |
| Material with a gold cost | 3 of 49 |
| Concentration | 17 of 49 |
| Ritual | 10 of 49 |
| Has an at-higher-levels clause | 22 of 49 |
| Cast as an action | 36 of 49 |
| Cast as a bonus action or reaction | 9 of 49 |
| Cast time of a minute or more | 4 of 49 |
| Instantaneous duration | 12 of 49 |
| Average classes per spell | 2.6 |
| Spells on exactly one class list | 9 of 49 |
| Average net cost, concentration spells | 60 |
| Average net cost, other spells | 52 |
| Average net cost, spells with a material | 52 |
| Average net cost, spells with no material | 58 |

Takeaways: nearly every spell has a verbal component, most have a somatic one, and about half have a material. Materials are common, so a mundane material refunds little. Gold-cost materials are rare (3 spells), so they refund heavily. In this small set, spells with materials do not score higher than spells without, so the data does not by itself show that materials mark stronger spells. The larger refund for gold-cost materials follows the design rule that costly components limit power, not a trend in these 49 files. Concentration spells are the long-duration ones, so the concentration refund offsets part of the duration cost.

## Cost tables (points you spend)

### Damage and healing

| Item | Points | Unit |
|---|---|---|
| Damage dealt | 5 | per avg damage |
| Extra damage on each weapon hit | 16 | per avg damage |
| Repeat damage on later turns | 5 | per avg damage |
| Hit points restored (modifier assumed +3) | 5 | per avg HP |
| Temporary hit points | 4 | per HP |
| Temporary hit points renewed each turn | 8 | per HP per turn |

### Delivery of a damaging effect

| Item | Points | Unit |
|---|---|---|
| Delivered by attack roll | 0 | flat |
| Delivered by save, half on success | 5 | flat |
| Hits automatically | 12 | flat |
| Condition with no save or roll | 15 | flat |

### Buffs, debuffs and movement

| Item | Points | Unit |
|---|---|---|
| Armor Class bonus | 16 | per +1 AC |
| d4 bonus to attacks and saves | 34 | per target |
| Attacks against target have advantage | 29 | flat |
| Advantage on one next attack | 21 | flat |
| Disadvantage vs six creature types plus charm and fear immunity | 47 | flat |
| Immune to frightened | 10 | flat |
| Walking speed bonus | 2 | per foot |
| Dash as bonus action each turn | 34 | flat |
| Triple jump distance | 8 | flat |
| Negate falling damage and slow fall | 16 | flat |
| Immune to one named spell | 5 | flat |

### Conditions (per target)

| Item | Points | Unit |
|---|---|---|
| Prone | 10 | flat |
| Charmed | 31 | flat |
| Frightened | 31 | flat |
| Blinded | 31 | flat |
| Restrained | 36 | flat |
| Incapacitated | 42 | flat |
| Unconscious | 52 | flat |
| Forced to obey a one word order | 29 | flat |
| Forced movement up to 10 ft | 5 | flat |
| Difficult terrain | 10 | flat |
| Heavily obscured area | 26 | flat |
| Outlines target, negates invisibility | 10 | flat |
| Ignites loose flammables | 3 | flat |

### Utility

| Item | Points | Unit |
|---|---|---|
| Sense a category within 30 ft | 26 | flat |
| Learn aura or school of what you sense | 10 | flat |
| Reveal properties or lore | 21 | per item |
| Understand any language | 26 | flat |
| Speak with a creature type | 23 | flat |
| Create or destroy water | 13 | flat |
| Purify food and drink | 10 | flat |
| Day of food | 13 | flat |
| Alert when an area is entered | 18 | flat |
| Ward that redirects attackers | 47 | flat |
| Create a visual illusion | 47 | flat |
| Change your appearance | 47 | flat |
| Hidden writing | 26 | flat |
| Invisible helper that does chores | 42 | flat |
| Summon a loyal scout and helper | 73 | flat |
| Advantage to track a marked target | 8 | flat |
| Move effect to a new target | 5 | flat |
| Effect lasts until dismissed | 21 | flat |

### Targets and area

| Item | Points | Unit |
|---|---|---|
| Each additional target | 10 | per target |
| Split effect among several targets | 10 | flat |
| 10 ft square | 13 | flat |
| 20 ft square | 23 | flat |
| 15 ft cone | 18 | flat |
| 15 ft cube | 18 | flat |
| 20 ft cube | 23 | flat |
| 20 ft radius | 26 | flat |
| 30 ft radius | 31 | flat |

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
| Scales with higher slots | +5 |

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

### Magic Missile: 81.5 points

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

### Sleep: 90 points

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

## Scorecard for all 49 spells

| Spell | Net cost | Left | Conc. | Comp. | Classes |
|---|---|---|---|---|---|
| Guiding Bolt | 99 | 1 |  | VS | 1 |
| Bless | 98 | 2 | yes | VSM | 2 |
| Bane | 97 | 3 | yes | VSM | 2 |
| Hunter's Mark | 95 | 5 | yes | V | 1 |
| Sleep | 90 | 10 |  | VSM | 3 |
| Shield | 86 | 14 |  | VS | 2 |
| Magic Missile | 81.5 | 18.5 |  | VS | 2 |
| Inflict Wounds | 79.5 | 20.5 |  | VS | 1 |
| Burning Hands | 77.5 | 22.5 |  | VS | 2 |
| Detect Magic | 74 | 26 | yes | VS | 7 |
| Fog Cloud | 73 | 27 | yes | VS | 4 |
| Thunderwave | 72 | 28 |  | VS | 4 |
| Find Familiar | 69 | 31 |  | VSM | 1 |
| Feather Fall | 68 | 32 |  | VM | 3 |
| Hellish Rebuke | 66 | 34 |  | VS | 1 |
| Faerie Fire | 63 | 37 | yes | V | 2 |
| Entangle | 62 | 38 | yes | VS | 1 |
| Mage Armor | 61 | 39 |  | VSM | 2 |
| Alarm | 58 | 42 |  | VSM | 2 |
| Detect Poison and Disease | 58 | 42 | yes | VSM | 4 |
| Silent Image | 58 | 42 | yes | VSM | 3 |
| Disguise Self | 57 | 43 |  | VS | 3 |
| Unseen Servant | 55 | 45 |  | VSM | 3 |
| Detect Evil and Good | 54 | 46 | yes | VS | 2 |
| Witch Bolt | 54 | 46 | yes | VSM | 3 |
| Color Spray | 53 | 47 |  | VSM | 2 |
| Sanctuary | 49 | 51 |  | VSM | 1 |
| Animal Friendship | 48 | 52 |  | VSM | 3 |
| Goodberry | 45 | 55 |  | VSM | 2 |
| Illusory Script | 45 | 55 |  | SM | 3 |
| False Life | 44 | 56 |  | VSM | 2 |
| Charm Person | 43 | 57 |  | VS | 5 |
| Protection from Evil and Good | 43 | 57 | yes | VSM | 4 |
| Expeditious Retreat | 42 | 58 | yes | VS | 3 |
| Shield of Faith | 42 | 58 | yes | VSM | 2 |
| Comprehend Languages | 40 | 60 |  | VSM | 4 |
| Divine Favor | 40 | 60 | yes | VS | 1 |
| Longstrider | 40 | 60 |  | VSM | 4 |
| Healing Word | 39.5 | 60.5 |  | V | 3 |
| Grease | 37 | 63 |  | VSM | 1 |
| Cure Wounds | 36.5 | 63.5 |  | VS | 5 |
| Hideous Laughter | 34 | 66 | yes | VSM | 2 |
| Command | 32 | 68 |  | V | 2 |
| Heroism | 30 | 70 | yes | VS | 2 |
| Create or Destroy Water | 29 | 71 |  | VSM | 2 |
| Speak with Animals | 28 | 72 |  | VS | 3 |
| Identify | 13 | 87 |  | VSM | 2 |
| Jump | 11 | 89 |  | VSM | 4 |
| Purify Food and Drink | 5 | 95 |  | VS | 3 |

Full line items for any spell: `python tools/pointbuy.py score <spell-file-name>`, for example `score hunters-mark`. The same data is in `data/spell-scores.csv` and `data/point-buy.json`.

## Known limits of this model

- Damage is valued by average roll. It does not model how monsters resist or how often a save fails.
- Hard control effects (Hideous Laughter scores 34, Sleep 90) may be priced unevenly. This is my judgment, not tested at a table. Adjust the condition costs if your group disagrees.
- Spell level is fixed at 1. For other levels, change the budget yourself. I have no tested numbers for that.
- A limit only refunds points if it matters. DMs should reject a limit that never comes up.
- Utility spells such as Identify score near zero because they have no combat value. Their low score is not a mistake. Raise their duration or area if you want a stronger version.

