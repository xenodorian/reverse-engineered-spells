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
