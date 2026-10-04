# Spell Scaling Analysis

How much more should a spell be allowed to do as its level goes up? This study uses the 24 cantrips, 49 level 1 spells, and 53 level 2 spells in this repo, priced with the point-buy system in `docs/spell-point-buy.md`.

> **Verification status.** The spell files were written from memory of the SRD 5.1 lists and are not checked against the books. The 2014 DMG damage table used as a cross-check was also recalled from memory (UNVERIFIED). The level 2 list may miss a few SRD spells or include one that is not in the SRD. The conclusions describe this data set and my pricing, not official design intent. Only levels 0 to 2 are measured. Anything for level 3 and up is an extrapolation.

## Short answer

- **Budgets:** cantrip 25, level 1 100, level 2 150.
- **Growth is neither a doubling nor a flat step.** After calibration, level 2 spells cost 1.54 times what level 1 spells cost on average. The level 2 budget is that ratio applied to 100 and rounded to the nearest 25, which gives 150, not 200.
- **Much of that ratio comes from the effect floor, not from the spells.** With no floors, level 2 costs only 1.20 times level 1 under my prices. The floors (level 1 at 50, level 2 at 100) lift it to 1.54. So 150 rests on the floor design and on the DMG damage table, not on the spell data alone. Section 2 shows the numbers.
- **The recalled DMG damage table independently gives 1.50** for level 2 over level 1 average damage. That agrees with 1.50, but it is one data point from memory and covers damage only.
- **Shape:** from level 1 on, the evidence fits a straight line in spell level (about +50 points per level at the start), not an exponential. The data cannot prove that past level 2.
- **Cantrips are a separate track.** A cantrip budget of 25 is one quarter of level 1. Cantrips have no slot cost, so they are priced as a discount tier, not as level 0 of the same line.
- **Budget alone is not safe.** Pricing is convex for damage, healing, and targets, and every scalable item has a hard cap equal to the strongest value seen at that level. Details are in the stress test below.

## 1. What the spells look like at each level

| Measure | Cantrips | Level 1 | Level 2 |
|---|---|---|---|
| Spells | 24 | 49 | 53 |
| Spells that deal damage | 10 | 7 | 8 |
| Mean damage on the first hit (avg) | 4.6 | 11.1 | 11.2 |
| Max damage on the first hit (avg) | 6.5 | 16.5 | 21 |
| Mean damage including repeats (avg) | 4.6 | 12.1 | 17.4 |
| Max damage including repeats (avg) | 6.5 | 16.5 | 22 |
| Spells that heal | 0 | 3 | 1 |
| Max healing on one target (avg) | 0 | 7.5 | 12 |
| Spells with a strong condition | 0 | 8 | 6 |
| Mean targets (1 + extras) | 1 | 1.1 | 1.1 |
| Max targets | 2 | 5 | 6 |
| Share that need concentration | 17% | 35% | 49% |
| Share lasting an hour or more | 8% | 24% | 40% |
| Share that are rituals | 0% | 20% | 11% |
| Share with a material component | 29% | 53% | 64% |
| Materials with a gold cost | 0 | 3 | 5 |
| Mean classes per spell | 2.4 | 2.6 | 2.6 |
| Share with an at-higher-levels clause | 42% | 45% | 30% |

What stands out:

- **Average first-hit damage barely moves from level 1 to level 2.** It is 11.1 at level 1 and 11.2 at level 2. The best first hit rises from 16.5 to 21, and that level 2 figure is three Scorching Ray attacks added together. Damage including repeats rises from 12.1 to 17.4. Level 2 spells get ahead by repeating (Flaming Sphere, Moonbeam, Heat Metal) and by lasting longer, not by hitting harder once.
- **Cantrip damage is about 40% of level 1.** Mean first hit 4.6 against 11.1. The best cantrip hit is 6.5, the best level 1 hit 16.5.
- **Concentration and long duration rise with level.** 17% of cantrips need concentration, against 35% at level 1 and 49% at level 2.
- **Gold-cost materials start at level 1 and become more common.** 0 cantrips, 3 level 1 spells, 5 level 2 spells.

## 2. Where the growth comes from

Mean points per spell, by dimension, using the calibrated prices.

| Dimension | Cantrip | Level 1 | Level 2 | L2 / L1 |
|---|---|---|---|---|
| Damage | 3.7 | 8.5 | 11.0 | 1.29 |
| Healing | 0.0 | 2.2 | 1.4 | 0.63 |
| Buffs | 1.8 | 9.8 | 10.5 | 1.07 |
| Conditions | 1.3 | 8.0 | 7.7 | 0.96 |
| Utility | 5.9 | 16.1 | 27.7 | 1.73 |
| Targets and area | 0.5 | 7.9 | 6.6 | 0.85 |
| Effect floor top-up | 0.0 | 9.4 | 36.3 | 3.88 |
| Duration | 5.6 | 11.3 | 15.2 | 1.35 |
| Range | 3.3 | 2.5 | 2.7 | 1.08 |
| Casting time | 0.2 | 1.5 | 0.4 | 0.27 |
| Refunds (components, limits, concentration, class lists) | -6.0 | -8.9 | -9.6 | 1.08 |
| Ritual and scaling charges | 2.2 | 5.8 | 4.0 | 0.69 |
| **Net cost** | **18.5** | **74.0** | **114.0** | **1.54** |

Read the last column as the growth in each dimension. Anything near the net ratio grows with the budget. Anything well above it is where level 2 puts its extra power. Anything below it is a dimension that should not be allowed to grow as fast.

### How much of the level 2 premium is the floor?

The effect floor adds points to any spell whose effects fall short of it. Level 2 has far more spells under its floor, so the floor drives a large share of the level 2 cost. This table recomputes mean net cost with the floors switched off, using the same calibrated prices.

| Floors applied | Cantrip mean | Level 1 mean | Level 2 mean | L1 / cantrip | L2 / L1 |
|---|---|---|---|---|---|
| No floors | 18.5 | 64.6 | 77.7 | 3.48 | 1.20 |
| Level 1 floor only (50) | 18.5 | 74.0 | 77.7 | 3.99 | 1.05 |
| Both floors, as adopted (50 and 100) | 18.5 | 74.0 | 114.0 | 3.99 | 1.54 |

With no floors, level 2 spells cost about 1.20 times level 1 spells. Two readings fit. Either level 2 spells really are only a little stronger than level 1 spells in raw terms, or my level 2 item prices (set by analogy to level 1 items) are too low. I cannot tell which from this data. The floor rule makes the 1.5 ratio true by construction, and the DMG damage table agrees with 1.5, so I kept it. If you would rather let the spells speak, set the level 2 floor lower and the budget falls toward 105.

## 3. Calibrated prices

Each category of price is multiplied by a factor chosen so that spells of each level cluster near their budget. Level 1 and cantrip targets are fixed (95 and 20 against budgets of 100 and 25). The level 2 target is free. A pull toward the original hand-set prices stops any factor drifting far.

| Category | Multiplier |
|---|---|
| Damage and hit delivery | 0.76 |
| Healing | 0.81 |
| Buffs | 0.85 |
| Conditions | 1.00 |
| Utility | 1.44 |
| Area and targets | 1.00 |
| Range | 1.00 |
| Casting time | 1.33 |
| Duration | 0.97 |
| Component refunds | 0.57 |
| Limit refunds | 0.58 |
| Concentration refund | 0.51 |
| Ritual and scaling charges | 1.73 |
| Class list availability | 0.62 |

Before calibration the mean net cost was 18.5 for cantrips, 74.0 at level 1, and 114.0 at level 2. After: 18.5, 74.0, and 114.0, with standard deviations of 5.5, 13.7, and 12.4.

**What calibration cannot do.** Spells of one level are not equally strong, and my build for each spell is a judgment. The fit narrows the spread. It does not remove it. The level 1 mean is 74 and the median 74, not 100, because the budget is a ceiling set by the strongest spells (Sleep 100, Hunter's Mark 100, Detect Magic 100) and utility spells sit well under it. Moving typical spells up to 100 would push the strongest ones over budget.

## 4. Which curve? Linear, geometric, or power

Two budget points are known: 100 at level 1 and 150 at level 2. Both a straight line (+50 per level) and a geometric curve (x1.5 per level) pass through them, so the spell data alone cannot choose. The recalled DMG damage table spans levels 1 to 9 and can.

Average damage by level, from the table (UNVERIFIED):

| Level | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| Avg damage | 5.5 | 11 | 16.5 | 27.5 | 33 | 44 | 55 | 60.5 | 66 | 77 |
| Share of level 1 | 0.50 | 1.00 | 1.50 | 2.50 | 3.00 | 4.00 | 5.00 | 5.50 | 6.00 | 7.00 |

Fit of that table over levels 1 to 9:

| Model | Form | R squared |
|---|---|---|
| Linear | damage = 1.7 + 8.3 x level | 0.994 |
| Geometric | damage = 11.4 x 1.26^level | 0.931 |
| Power | damage = 10.0 x level^0.92 | 0.989 |

The best fit is **linear**. The linear and power fits are close, and both beat geometric for this table. A geometric curve would overshoot at high levels: a 1.5x step compounds to about 25x by level 9, while the table reaches 7x. (Treat the table as a rough check, since I recalled it and a miss in one entry would shift the fits.)

Budget curves for each hypothesis, with level 1 fixed at 100:

| Level | Follow the DMG table | Linear fit of the table | Geometric x1.5 | 50 x (level + 1) | Double each level (100 x level) |
|---|---|---|---|---|---|
| 1 | 100 | 100 | 100 | 100 | 100 |
| 2 | 150 | 183 | 150 | 150 | 200 |
| 3 | 250 | 266 | 225 | 200 | 300 |
| 4 | 300 | 350 | 338 | 250 | 400 |
| 5 | 400 | 433 | 506 | 300 | 500 |
| 6 | 500 | 516 | 759 | 350 | 600 |
| 7 | 550 | 599 | 1139 | 400 | 700 |
| 8 | 600 | 683 | 1709 | 450 | 800 |
| 9 | 700 | 766 | 2563 | 500 | 900 |

**Recommendation.** Use **100 at level 1 and 150 at level 2**. For level 3 and up, use `50 x (level + 1)` as a provisional placeholder, which gives 200 at level 3 and 250 at level 4. That line matches both known points, grows more slowly than the DMG table at level 3 (200 against 250), and never overshoots the way a geometric curve does. It has no spell data behind it yet. The recalled table suggests a jump at level 3 (damage 27.5 against 16.5), so revisit when level 3 spells are added.

The cantrip budget does not sit on this line. The line would give 50 at level 0. Cantrips use a half-line value (25) because they can be cast without limit. Do not extend that to other levels.

## 5. Clearances between levels

A clearance is the gap between the highest effect total allowed at one level and the lowest allowed at the next. Effect total means damage, healing, conditions, utility, and area only. Range, duration, and refunds are not counted.

| Level | Budget | Effect floor | Effect ceiling | Lowest effect total | Highest effect total | Lowest net | Highest net |
|---|---|---|---|---|---|---|---|
| Cantrip | 25 | none | 49 | 4 | 20 | 8 | 25 |
| Level 1 | 100 | 50 | 99 | 50 | 98 | 40 | 100 |
| Level 2 | 150 | 100 | none | 100 | 131 | 86 | 144 |

The cantrip to level 1 gap is the one you asked for: level 1 effects start at 50, cantrip effects stop at 49. I applied the same idea one step up. A level 2 spell's effects must total at least 100, which is the whole level 1 budget, and level 1 effects stop at 99. The floor top-up is why the cheapest level 2 spells (Augury, Detect Thoughts) still cost 86 or more.

## 6. Stress test: can a player inflate an existing spell?

For every spell the test raises one lever until the spell stops being legal. Lever one raises damage, healing, or temporary HP. Lever two adds targets. Each is run with only the budget enforced and with every rule enforced.

| Level | Spells with a magnitude | Median growth, budget only | Worst, budget only | Median growth, all rules | Worst, all rules | Max extra targets, budget only | Max extra targets, all rules |
|---|---|---|---|---|---|---|---|
| Cantrip | 10 | x1.29 | x2.40 | x1.20 | x2.40 | 1 | 1 |
| Level 1 | 11 | x1.67 | x3.30 | x1.36 | x2.31 | 5 | 4 |
| Level 2 | 10 | x2.01 | x3.70 | x1.54 | x2.36 | 7 | 5 |

Largest growth under all rules:

| Spell | Level | Lever | Original | Most the rules allow |
|---|---|---|---|---|
| Vicious Mockery | 0 | c_dmg | 2.5 | 6 |
| Flaming Sphere | 2 | dmg | 7 | 16.5 |
| Witch Bolt | 1 | dmg | 6.5 | 15 |
| Spiritual Weapon | 2 | dmg | 7.5 | 16.5 |
| Heat Metal | 2 | dmg | 9 | 16.5 |

The rules cut the worst case but do not remove it. A spell with a small number (Vicious Mockery's d4, Healing Word's d4 plus modifier) can still climb to the strongest value that exists at its level. That is the design: no spell can beat the top of its own level, even if it can get close. Raising the cap would mean accepting stronger spells at that level.

Lever three re-files each spell one level lower and records which rule stops it:

| Filed as | Spells | effect tier | magnitude cap | control cap | effect ceiling | budget | allowed |
|---|---|---|---|---|---|---|---|
| Level 1 spell as a cantrip | 49 | 49 | 0 | 0 | 0 | 0 | 0 |
| Level 2 spell as level 1 | 53 | 42 | 7 | 0 | 0 | 0 | 4 |

**Weak spot.** 4 level 2 spells pass as level 1 spells under the current rules: Aid, Barkskin, Blindness/Deafness, Web. Each is built only from level 1 items and priced under 100 when the level 2 floor does not apply. That means my model sees them as level 1 strength spells, which matches how they read (Web is close to Entangle, Barkskin is a +3 AC buff, Blindness/Deafness is a blind-or-deafen with a repeat save, Aid is five temporary HP to three allies). Either those spells are underpriced here, or WotC placed them at level 2 for reasons (duration, range, flexibility) that my items do not capture. I did not patch this, because forcing an extra item into each would be a guess.

## 7. Rules that follow from the study

| Rule | Value |
|---|---|
| Budgets | cantrip 25, level 1 100, level 2 150 |
| Effect floor | level 1: 50. level 2: 100 |
| Effect ceiling | cantrip: 49. level 1: 99 |
| Items by level | Each item has a minimum level. A level 1 spell cannot use a level 2 item. |
| Magnitude caps | Damage, healing, temporary HP, targets, AC, and similar items cannot exceed the highest value seen at that level, carried up from lower levels. Damage from a spell that splits across targets has its own cap. |
| Control cap | Strong conditions together cost at most 82 at level 1 and 95 at level 2. Cantrips have none. |
| Flat items | Taken once. No stacking. |
| Convex price | Price grows with magnitude to the power 1.4, so doubling damage more than doubles the price. |
| Limit refunds | Capped at 50% of the effect cost. |
| Upcasting | Each increase per slot level costs 50% of buying it outright. Targets rise by at most 1 per slot level. A damage or healing increase cannot exceed the base amount per slot level. |

## 8. Limits of this study

- Three levels is too few to pick a curve from spell data alone. The DMG table breaks the tie only if my recollection of it is right.
- Every spell's build, and the price of every level 2 item, is my judgment. The calibration tunes category multipliers, not individual items. A mispriced item stays mispriced.
- The level 2 list and spell text come from memory. Some SRD level 2 spells may be missing.
- Caps come from the spells I built, so a mistake in one build moves a cap.
- Upcasting is priced from the first listed increase only. Spells that scale in other ways (duration, radius, hit point pools) pay a flat charge.
- Concentration, saves, and monster hit points are not modeled. Damage is an average roll.
