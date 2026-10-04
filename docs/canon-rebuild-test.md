# Canon Rebuild Test

Can the builder rebuild the canon spells inside its own budget windows? This is a test of the builder, not of canon. It looks for spells that fit only by accident, spells that are complicated to model, and spells close to an edge. The earlier rule that a builder may not beat canon spells is dropped here.

> **Verification status.** The spells and their builds were written from memory and are my own modeling. A pass here means my builds fit my rules. It does not show that the real spells match.

## Short answer

- **All 169 canon builds fit their budget windows**, and they still do after caps were turned off.
- **That result is weaker than it sounds.** 134 of 171 items belong to one spell, so a spell built from one fits by construction.
- **The custom lines work.** Swapping single-use items for custom lines on a 40% ladder keeps 115 of 120 spells legal, and a 20% ladder keeps 118 of 120.
- **Multi-mode spells rebuild with the mode rule.** 8 of 9 stay legal. The largest change in net cost is 24.1 points.
- **The observed caps were hiding fragility.** 14 spells fit only because they set a cap, so the caps are now off.
- **10 spells are within 3 points of budget and 10 are fragile to a 10% price shift.** They are listed in section 5.

## 1. Most canon spells rebuild only because they have their own item

134 of the 171 items that any spell uses belong to exactly one spell. These are canon effects packaged as items (Haste, Fly, Counterspell). A spell built from one of them always fits, because the item was priced from that spell. That says little about whether the builder can build something that is not already an item.

| Level | Mean share of effect price from single-use items | Spells where it is over 70% |
|---|---|---|
| Cantrip | 62% | 13 of 24 |
| Level 1 | 44% | 19 of 49 |
| Level 2 | 68% | 34 of 53 |
| Level 3 | 79% | 30 of 43 |

To make the builder usable beyond canon, this pass adds three custom lines (`custom_util`, `custom_buff`, `custom_cond`). You set the base points by comparing the effect with the items in the price tables. Tests 3 and 4 check that this works.

## 2. Spells that fit only because they set a cap

The previous rules capped each scalable item, and the control total, at the highest value any canon spell used at that level. Leaving each spell out in turn and measuring the caps from the rest, 14 of 169 spells no longer fit. They are the spells that defined a cap, so they could only be built because they were already there.

| Level | Spell | What stopped it |
|---|---|---|
| Cantrip | Poison Spray | c_dmg is capped at 5.5 for level 0 spells (you asked for 6.5) |
| Level 1 | Burning Hands | dmg is capped at 9 for level 1 spells (you asked for 10.5) |
| Level 1 | Cure Wounds | heal is capped at 5 for level 1 spells (you asked for 7.5) |
| Level 1 | Feather Fall | target_extra is capped at 2 for level 1 spells (you asked for 4) |
| Level 1 | Guiding Bolt | dmg is capped at 6.5 for level 1 spells (you asked for 14) |
| Level 1 | Hideous Laughter | control effects total 82, over the level 1 control cap of 48 |
| Level 1 | Hunter's Mark | dmg_rider is capped at 2.5 for level 1 spells (you asked for 3.5) |
| Level 1 | Shield | ac_bonus is capped at 3 for level 1 spells (you asked for 5) |
| Level 2 | Hold Person | control effects total 95, over the level 2 control cap of 82 |
| Level 2 | Moonbeam | dmg_recurring is capped at 10.5 for level 2 spells (you asked for 11) |
| Level 2 | Prayer of Healing | heal is capped at 7.5 for level 2 spells (you asked for 12) |
| Level 2 | Scorching Ray | dmg is capped at 10.5 for level 2 spells (you asked for 21) |
| Level 2 | Shatter | dmg is capped at 11 for level 2 spells (you asked for 13.5) |
| Level 3 | Call Lightning | dmg_recurring is capped at 13.5 for level 3 spells (you asked for 16.5) |

The caps are now reference data only (`data/calibration.json`, `observed_maxima`). With them off, every one of these spells builds. The effect ceiling still bounds any single line, because no effect total can pass the level's budget. At level 1 that stops a single damage line near 19 average, against a canon top of 16.5 (Inflict Wounds).

## 3. Round trip through the custom lines

For every spell, each single-use effect item (utility, buff, and condition items) is swapped for a custom line at the nearest rung of a price ladder, then the spell is re-scored under every rule. A coarse ladder shows how far a designer who only roughly prices an effect can drift.

### Ladder with steps of 39%

120 spells contain a single-use item. After snapping, the mean change in net cost is 1.7 points and the largest is 30.4. 115 of 120 are still legal.

| Spell | Level | Net before | Net after | Budget | Why it failed |
|---|---|---|---|---|---|
| Detect Magic | Level 1 | 100.0 | 101.4 | 100 | over budget |
| Find Familiar | Level 1 | 78.1 | 87.7 | 100 | effects total 103.5, which is level 2 strength (ceiling 100) |
| Hunter's Mark | Level 1 | 99.9 | 100.7 | 100 | custom_util listed more than once. Use the quantity instead, or take a flat item once |
| Shield | Level 1 | 99.9 | 100.4 | 100 | over budget |
| Conjure Animals | Level 3 | 228.2 | 258.6 | 250 | over budget |

### Ladder with steps of 19%

120 spells contain a single-use item. After snapping, the mean change in net cost is 0.7 points and the largest is 18.5. 118 of 120 are still legal.

| Spell | Level | Net before | Net after | Budget | Why it failed |
|---|---|---|---|---|---|
| Hunter's Mark | Level 1 | 99.9 | 101.0 | 100 | custom_util listed more than once. Use the quantity instead, or take a flat item once |
| Sleep | Level 1 | 99.9 | 103.3 | 100 | over budget |

## 4. Spells with several modes

Some spells let the caster pick an option when casting (Alter Self, Bestow Curse). Pricing every option in full would overcharge, because only one is used at a time. The rule added in this pass is: **price the most expensive mode in full, and a quarter of each other mode.** The table rebuilds 9 such spells with that rule.

| Spell | Level | Modes | Net as one lump | Net with modes | Change | Legal |
|---|---|---|---|---|---|---|
| Alter Self | Level 2 | 3 | 118.3 | 118.3 | +0.0 | yes |
| Bestow Curse | Level 3 | 4 | 165.0 | 165.1 | +0.1 | yes |
| Enhance Ability | Level 2 | 6 | 128.4 | 124.3 | -4.1 | yes |
| Glyph of Warding | Level 3 | 2 | 227.1 | 251.2 | +24.1 | no: over budget |
| Create or Destroy Water | Level 1 | 2 | 51.4 | 51.4 | +0.0 | yes |
| Plant Growth | Level 3 | 2 | 156.8 | 156.7 | -0.1 | yes |
| Detect Thoughts | Level 2 | 2 | 100.2 | 100.2 | +0.0 | yes |
| Blindness/Deafness | Level 2 | 2 | 122.4 | 122.4 | +0.0 | yes |
| Calm Emotions | Level 2 | 2 | 112.0 | 120.8 | +8.8 | yes |

## 5. Margins and sensitivity

10 spells are within 3 points of their level's budget:

| Spell | Level | Net | Budget | Left |
|---|---|---|---|---|
| Fire Bolt | Cantrip | 25.0 | 25 | 0.0 |
| Detect Magic | Level 1 | 100.0 | 100 | 0.0 |
| Hunter's Mark | Level 1 | 99.9 | 100 | 0.1 |
| Shield | Level 1 | 99.9 | 100 | 0.1 |
| Sleep | Level 1 | 99.9 | 100 | 0.1 |
| Dancing Lights | Cantrip | 24.2 | 25 | 0.8 |
| Produce Flame | Cantrip | 23.9 | 25 | 1.1 |
| Guiding Bolt | Level 1 | 98.5 | 100 | 1.5 |
| Chill Touch | Cantrip | 23.3 | 25 | 1.7 |
| Mage Hand | Cantrip | 23.1 | 25 | 1.9 |

1 spells hit the limit-refund cap (their caveats are worth more than 50% of their effect cost, so part of the refund is lost): Prestidigitation.

To see how fragile each fit is, every price category was nudged at random by up to 10% (300 trials, prices not re-fitted) and each spell re-scored.

- Spells that stay legal in every trial: 155 of 169.
- Spells legal in under 90% of trials: 10.

| Spell | Level | Share of trials legal |
|---|---|---|
| Shield | Level 1 | 53% |
| Detect Magic | Level 1 | 54% |
| Hunter's Mark | Level 1 | 54% |
| Sleep | Level 1 | 56% |
| Fire Bolt | Cantrip | 57% |
| Guiding Bolt | Level 1 | 63% |
| Scorching Ray | Level 2 | 74% |
| Dancing Lights | Cantrip | 78% |
| Produce Flame | Cantrip | 83% |
| Find Familiar | Level 1 | 86% |

These spells sit on an edge. A small change to one price can push them over, so they are the ones to re-check after any retuning.

