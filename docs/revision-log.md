# Revision Log

## Second logic pass

Method: I wrote probes that try to break the rules, ran them against the calibrated model, and fixed what failed. The probes and a set of ordering and data checks are now in `tools/check.py` (`python tools/pointbuy.py check`). All 27 checks pass after the changes below.

### Problems found and fixes

| # | Problem | Evidence | Fix |
|---|---|---|---|
| 1 | Unconscious was priced below incapacitated | 48 against 72, although unconscious is strictly worse for the target | Renamed the item "Asleep (wakes on damage or a shake)", which is what Sleep actually does. Removed the separate wake-on-damage limit from Sleep so it is not counted twice |
| 2 | Area prices did not follow size | A 60 ft line cost more than a 15 ft radius, and a 15 ft radius cost more than a 20 ft radius | Area price now follows the square root of the footprint |
| 3 | Extra targets were nearly free | Five extra targets on Hold Person added 67 points, against 95 for the first. Bless's upcast target cost 6.6 against 29 for a base target | An extra target costs a share of every per-target line (damage 70%, control 60%, buffs 50%, utility 50%, healing 25%). Extra targets count toward the control cap. A spell with nothing per-target cannot take them |
| 4 | The level 1 damage cap came from one outlier | Inflict Wounds (3d10, touch) set a 16.5 cap that every ranged spell could use. The best ranged level 1 hit is 14 | Separate caps for touch (16.5), split-target (10.5 at level 1, 21 at level 2), and plain ranged damage (14). A cantrip with a rider is capped at 4.5 |
| 5 | Cantrip scaling was a flat charge | Scaling a d4 and a d10 cost the same 5.2 | Scaling costs 40% of the cantrip's damage price |
| 6 | Produce Flame's hurl range was not priced | It was priced as Self, which understated its cost | A spell can name the range its attack really reaches. Produce Flame is priced at 30 ft |
| 7 | Duration cost ignored how weak the effect was | Prestidigitation paid 23 points for a one-hour cosmetic trick | A cantrip with effects under 40 points pays between half and all of the duration price |
| 8 | A flat item or limit could be listed twice | Two charmed lines or two copies of one limit were both accepted | Duplicates are rejected |
| 9 | The stress test raised one line at a time | It missed the realistic attack of scaling all damage and healing together | Added a lever that scales every magnitude line together |

Smaller changes made so every spell stayed legal after the above: cantrip damage base price 2.7 to 2.4, Hunter's Mark's tracking and transfer prices trimmed, Goodberry's healing counted as 5 (it is delivered one berry at a time), and Bane and Bless rebuilt as one buff plus two extra targets.

### Result

- All 126 spells are legal under every rule. Mean net cost is 17.7 for cantrips, 74.7 for level 1, and 120.2 for level 2. The strongest spells sit at their budget: Fire Bolt 24.5 of 25, Sleep 99.7 of 100, and the top level 2 spell at 150.
- Cantrips span 8 to 25. Pricing Produce Flame's 30 ft throw and scaling by damage would have pushed some over 25, so the weak-effect duration rule keeps them in budget.
- Scaling every damage and healing line together, the median spell can grow about 5% with all rules on, and the worst about 55% to 85%. With only the budget enforced the worst grew about 3 to 4 times. Detail is in `docs/spell-scaling-analysis.md`.
- The level 2 budget stays at 150. The calibrated level 2 to level 1 ratio moved from 1.54 to 1.61, which still rounds to 150.

### Left alone, on purpose

- Four level 2 spells (Aid, Barkskin, Blindness/Deafness, Web) still pass as level 1 spells. Fixing it would mean inventing extra effect items for them.
- Level 2's 1.5 times growth still depends on the effect floor. With no floors the ratio is about 1.2.
- The utility price multiplier is high (1.44). Many utility prices are my guesses and the fit leans on this one knob to compensate.
- Refunds do not scale with level, so they matter less at level 2.
- `cond_frightened` and `lim_wake_on_damage` are unused by any spell. They stay as options for builders.
- Casting time is a weak lever. A 10-minute cast refunds only about 10 points. Out-of-combat spells such as Prayer of Healing rely on healing being priced low (25% per extra target) instead.

## Level 3 pass

Added 43 level 3 spells from memory of the SRD 5.1 list (`spells/level-3/`), about 40 new level 3 items, and a level 3 budget.

### What was done

- **Level 3 was held out.** Prices are fitted to cantrips, level 1, and level 2 only. The 43 level 3 spells are priced with those prices and the budget is read off the strongest one. The result is 250, with the strongest spell at 228.
- **Level 2 stays at 150.** The fit now holds it there as a constraint and confirms 150 still covers the strongest level 2 spell (146).
- **Floors.** Level 1 stays at 50. Level 2 stays at 100 and level 3 is 150, each equal to the previous level's budget.
- **Ceiling.** From level 1 up, a spell's effects cannot exceed its own level's budget. Before, level 1 was capped at 99 (just under the level 2 floor) and level 2 had no ceiling. Adjacent levels now meet exactly at a budget.
- **Caps.** Damage caps now also have an area key (Fireball and Lightning Bolt set 28 at level 3 without letting a single target reach 28) and a fast-cast key for bonus action and reaction spells. A touch spell that explodes in an area (Glyph of Warding) is classed as area, not touch.
- **Prices fixed on the way.** Slow was priced above paralyzed, then above incapacitated. It is now between asleep and incapacitated. Added an ordering check for it.

### Things I tried and dropped

- **Fitting level 3 into the price fit.** It dragged the damage multiplier from 0.83 down to about 0.45, because Fireball is an outlier among level 3 spells, which cheapened level 1 damage.
- **Floors at half of each level's budget with budgets set by the strongest spell.** The numbers shrank on every pass, because lower floors gave lower costs, which gave lower budgets, which gave lower floors. The loop has no fixed point above zero.
- **Fitting only cantrips and level 1.** Healing is used by only three level 1 spells, so its price ran off to nearly double. Level 2 spread keeps it in check.

### Result

- Budgets are 25, 100, 150, 250 for cantrips and levels 1, 2, 3. They match the recalled DMG table at all three measured levels (ratios 1.5 and 2.5 against level 1). The earlier placeholder of 200 for level 3 would have left 4 level 3 spells over budget.
- All 169 spells are legal under every rule and all 29 logic checks pass.
- Scaling every damage and healing line together, the median spell can grow about 0% to 5% with all rules on, and the worst about 35% to 85% depending on level. With only the budget enforced, the worst grew about 3 to 4 times.
- One level 3 spell (Mass Healing Word) and four level 2 spells can still be filed one level lower. The analysis lists them.

### Open

- Level 3 is the least checked level. Its builds were written once.
- At level 3, 35 of 43 spells rise to the floor of 150, so the weak end of the level is floor-driven. The budget is not, because it follows the strongest spell.
- The budgets follow the strongest spell, so one mispriced standout (Conjure Animals and Glyph of Warding are the top two at 228 and 227) moves a budget by a step of 25.

## Sanity check pass

Numbers in the sections above describe the state at the time of each pass. The current numbers are in `docs/spell-scaling-analysis.md`.

### What was checked

- **Logic checks:** 29 of 29 pass.
- **Reproducibility:** Re-running the fit and the report from a clean state changed no committed file.
- **Hand recomputation:** I rebuilt Fire Bolt and Hold Person by hand from the calibration file. They came out 0.1 and 0.2 points off the calculator (24.9 against 25.0, 138.4 against 138.6). The gap is rounding: each line is rounded to one decimal before the total is added, so a total can drift by a few tenths. The displayed lines always sum to the displayed total.
- **Counts:** 24 cantrips, 49 level 1, 53 level 2, 43 level 3. No duplicate names. All 169 scores are within budget.
- **Examples:** All three example files still run and stay within budget.
- **Spell data review:** I reviewed every spell's concentration, ritual, casting time, and class list against my recollection of the 2014 books. This is a memory check, not a check against the books.
- **Random builds:** 3,000 random legal builds at each of levels 1 to 3 (see below).

### Errors found and fixed

| Error | Fix |
|---|---|
| Prayer of Healing and Warding Bond listed Paladin as a class. As I recall, Paladin gets neither | Both are now Cleric only. The class-list refund changed by a fraction of a point and the budgets did not move |
| `calc` crashed with a stack trace on an unknown item name, and `score` on an unknown spell | Both now print a one-line message |
| The builder guide said to set the level to 0, 1, or 2, and had a stray double space | Corrected |

### Found and left alone

- **Random builds can slightly out-do the existing spells.** Among random legal builds, the highest effect total was 100, 150, and 248 at levels 1, 2, and 3. The strongest existing spells reach 94, 128, and 209. A builder can therefore beat the best existing spell's effect power by about 6%, 17%, and 19%, and its gross cost (effects, delivery, and duration before refunds) by about 15%, 15%, and 6%. The cause is the effect ceiling, which equals the budget. Lowering the ceiling to about 90% of the budget would close most of the gap. I did not change it, because that would change a rule you have already seen.
- **The class lists are from memory.** I am least sure of the lists for spells I know less well. Treat every class list as unverified.
- **The spell lists may be incomplete.** The SRD level 2 and 3 lists were recalled, so a few real SRD spells may be missing.
