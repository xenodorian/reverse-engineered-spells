# Spell Scaling Analysis

How much more should a spell be allowed to do as its level goes up? This study uses the 24 cantrips, 49 level 1 spells, 53 level 2 spells, and 43 level 3 spells in this repo, priced with the point-buy system in `docs/spell-point-buy.md`.

> **Verification status.** The spell files were written from memory of the SRD 5.1 lists and are not checked against the books. The 2014 DMG damage table used as a cross-check was also recalled from memory (UNVERIFIED). The level 2 and level 3 lists may miss a few SRD spells or include one that is not in the SRD. The conclusions describe this data set and my pricing, not official design intent. Only levels 0 to 3 are measured. Anything for level 4 and up is an extrapolation.

## Short answer

- **Budgets:** cantrip 25, level 1 100, level 2 150, level 3 250.
- **Level 3 was a held-out test.** Prices were fitted to cantrips, level 1, and level 2 only. Pricing the 43 level 3 spells with those prices, unchanged, the strongest one costs 228. That sets the level 3 budget at 250.
- **The earlier placeholder was wrong at level 3.** The previous version of this study proposed `50 x (level + 1)`, which gives 200. The measured strongest level 3 spell costs 228, so 200 would leave 4 of the 43 level 3 spells over budget. The recalled DMG damage table predicts 250 for level 3 (27.5 over 11 average damage), and the measured budget matches it.
- **Shape:** budgets of 100, 150, 250 for levels 1, 2, 3 grow by 50, then 100. The rise picks up speed, like the DMG table's steps of 5.5 and 11. It is not a doubling each level and not a straight line. Three points cannot prove a curve.
- **Much of each level's cost still comes from the effect floors, not from the spells.** With no floors at all, the mean costs are 63, 81, and 123 for levels 1, 2, and 3. The floors lift them to 74, 118, and 172. The budgets follow the strongest spells, which sit well above any floor, so they barely move. The means and the weak end of each level are floor-driven. Section 2 shows the numbers.
- **Cantrips are a separate track.** A cantrip budget of 25 is one quarter of level 1. Cantrips have no slot cost, so they are priced as a discount tier, not as level 0 of the same line.
- **Budget alone is not safe.** Pricing is convex for damage, healing, and AC. Extra targets cost a share of what each target pays. Every scalable item has a hard cap equal to the strongest value seen at that level. The stress test shows what that buys.

## 1. What the spells look like at each level

| Measure | Cantrips | Level 1 | Level 2 | Level 3 |
|---|---|---|---|---|
| Spells | 24 | 49 | 53 | 43 |
| Spells that deal damage | 10 | 7 | 8 | 6 |
| Mean damage on the first hit (avg) | 4.6 | 11.1 | 11.2 | 19.8 |
| Max damage on the first hit (avg) | 6.5 | 16.5 | 21 | 28 |
| Mean damage including repeats (avg) | 4.6 | 12.1 | 17.4 | 26.6 |
| Max damage including repeats (avg) | 6.5 | 16.5 | 22 | 33 |
| Spells that heal | 0 | 3 | 1 | 1 |
| Max healing on one target (avg) | 0 | 7.5 | 12 | 5.5 |
| Spells with a strong condition | 0 | 8 | 6 | 7 |
| Max targets | 2 | 5 | 6 | 6 |
| Share that need concentration | 17% | 35% | 49% | 42% |
| Share lasting an hour or more | 8% | 24% | 40% | 33% |
| Share that are rituals | 0% | 20% | 11% | 14% |
| Share with a material component | 29% | 53% | 64% | 60% |
| Materials with a gold cost | 0 | 3 | 5 | 5 |
| Mean classes per spell | 2.4 | 2.6 | 2.6 | 2.9 |
| Share with an at-higher-levels clause | 42% | 45% | 30% | 37% |

What stands out:

- **First-hit damage barely moves from level 1 to level 2, then jumps at level 3.** The mean first hit is 11.1, 11.2, and 19.8 at levels 1, 2, and 3. The best first hit is 16.5, 21, and 28. Level 3's top figures are Fireball and Lightning Bolt (8d6 each, area, save for half). The DMG table shows the same pattern: a small step from level 1 to 2, a bigger one to 3.
- **Level 2 gets ahead by repeating and lasting, level 3 by hitting harder and wider.** Damage including repeats averages 12.1, 17.4, and 26.6.
- **Cantrip damage is about 40% of level 1.** Mean first hit 4.6 against 11.1.
- **Concentration and long duration keep rising.** Concentration: 17%, 35%, 49%, 42%.
- **Gold-cost materials start at level 1 and grow:** 0, 3, 5, 5 spells.

## 2. Where the growth comes from

Mean points per spell, by dimension, using the calibrated prices.

| Dimension | Cantrip | Level 1 | Level 2 | Level 3 | L3 / L1 |
|---|---|---|---|---|---|
| Damage | 3.7 | 9.5 | 12.3 | 20.4 | 2.15 |
| Healing | 0.0 | 2.1 | 1.3 | 0.4 | 0.21 |
| Buffs | 1.9 | 7.9 | 11.1 | 17.1 | 2.18 |
| Conditions | 1.3 | 8.0 | 7.7 | 11.5 | 1.44 |
| Utility | 5.7 | 15.3 | 26.6 | 51.0 | 3.34 |
| Targets and area | 0.3 | 6.5 | 4.9 | 7.4 | 1.14 |
| Effect floor top-up | 0.0 | 10.0 | 37.3 | 48.8 | 4.87 |
| Duration | 4.4 | 14.0 | 18.8 | 16.2 | 1.16 |
| Range | 3.8 | 2.8 | 3.0 | 4.1 | 1.49 |
| Casting time | 0.2 | 1.2 | 0.3 | -0.4 | -0.38 |
| Refunds (components, limits, concentration, class lists) | -5.7 | -8.3 | -9.2 | -9.4 | 1.13 |
| Ritual and scaling charges | 1.7 | 4.8 | 4.1 | 5.0 | 1.04 |
| **Net cost** | **17.3** | **73.6** | **118.2** | **172.2** | **2.34** |

Read the last column as the growth in each dimension from level 1 to level 3. Anything near the net ratio grows with the budget. Anything well above it is where higher levels put their extra power. Anything below it is a dimension that should not be allowed to grow as fast.

### How much of each level's cost is the floor?

An effect floor adds points to any spell whose effects fall short of it. The level 1 floor of 50 is yours. The level 2 floor (100) and level 3 floor (150) are mine: each equals the previous level's budget. This table recomputes the means with the floors switched off, using the same prices.

| Floors applied | Cantrip mean | Level 1 mean | Level 2 mean | Level 3 mean | L2 / L1 | L3 / L1 |
|---|---|---|---|---|---|---|
| No floors at all | 17.3 | 62.7 | 80.6 | 123.4 | 1.29 | 1.97 |
| Level 1 floor only (50) | 17.3 | 73.6 | 80.6 | 123.4 | 1.09 | 1.68 |
| All floors, as adopted (50, 100, 150) | 17.3 | 73.6 | 118.2 | 172.2 | 1.61 | 2.34 |

The strongest spell at each level, with no floors, costs 100, 144, and 228. With the floors it is 100, 146, and 228. The budgets follow the strongest spell, so the floors barely move them. The floors do set where the weak end of each level sits: the cheapest level 3 spell costs 146 with floors and 56 without.

Two readings of the no-floor means (63, 81, 123). Either higher-level spells really are only a little stronger on average than lower ones, with a few standouts, or my level 2 and 3 item prices (set by analogy to level 1 items) are too low. I cannot tell which from this data. I kept the floors because they make each level's weak end cost at least the level below's budget. You asked for that clearance between cantrips and level 1, and I extended the idea upward.

## 3. Calibrated prices

Each category of price is multiplied by a factor chosen so that cantrips and level 1 spells cluster near their budgets (targets of 20 and 95 against 25 and 100), with level 2 fitted for spread only. A pull toward the original hand-set prices stops any factor drifting far. Level 3 does not enter the fit.

| Category | Multiplier |
|---|---|
| Damage and hit delivery | 0.84 |
| Healing | 0.78 |
| Buffs | 0.89 |
| Conditions | 1.00 |
| Utility | 1.38 |
| Area and targets | 0.67 |
| Range | 1.12 |
| Casting time | 1.05 |
| Duration | 1.20 |
| Component refunds | 0.57 |
| Limit refunds | 0.51 |
| Concentration refund | 0.48 |
| Ritual and scaling charges | 1.19 |
| Class list availability | 0.57 |

With these prices the mean net cost is 17.3, 73.6, 118.2, and 172.2 for cantrips and levels 1, 2, and 3, with standard deviations of 5.1, 14.2, 13.7, and 19.2.

**What calibration cannot do.** Spells of one level are not equally strong, and my build for each spell is a judgment. The fit narrows the spread. It does not remove it. The level 1 mean is 74 and the median 74, not 100, because the budget is a ceiling set by the strongest spells (Detect Magic 100, Sleep 100, Shield 100) and utility spells sit well under it.

## 4. Which curve?

The budgets are set by one rule: the smallest multiple of 25 that covers the strongest spell at that level, with level 1 anchored at 100 and cantrips at 25. That gives 100, 150, and 250. A rule based on the strongest spell is sensitive to one outlier, so here is the same comparison using the 90th percentile of net cost instead of the maximum:

| Measure | Level 1 | Level 2 | Level 3 | L2 / L1 | L3 / L1 |
|---|---|---|---|---|---|
| Strongest spell | 100 | 146 | 228 | 1.46 | 2.28 |
| 90th percentile | 91 | 139 | 192 | 1.53 | 2.12 |
| Mean | 74 | 118 | 172 | 1.61 | 2.34 |
| Recalled DMG damage table | 11 | 16.5 | 27.5 | 1.50 | 2.50 |
| Budget chosen | 100 | 150 | 250 | 1.50 | 2.50 |

Every measure rises with level and the ratio to level 1 grows faster each level, with the budget at 2.5 times level 1 for level 3. The percentile and mean rows are lower in absolute terms because they include many utility spells. I chose the strongest-spell rule because the budget is a ceiling, not a typical cost.

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

The best fit over levels 1 to 9 is **linear**. Over levels 1 to 3 alone the table is not a straight line: it steps 5.5, then 11.

Budget curves for each hypothesis, with level 1 fixed at 100:

| Level | Follow the DMG table | Linear fit of the table | Geometric x1.5 | 50 x (level + 1) | Double each level | Measured budget |
|---|---|---|---|---|---|---|
| 1 | 100 | 100 | 100 | 100 | 100 | 100 |
| 2 | 150 | 183 | 150 | 150 | 200 | 150 |
| 3 | 250 | 266 | 225 | 200 | 300 | 250 |
| 4 | 300 | 350 | 338 | 250 | 400 | not measured |
| 5 | 400 | 433 | 506 | 300 | 500 | not measured |
| 6 | 500 | 516 | 759 | 350 | 600 | not measured |
| 7 | 550 | 599 | 1139 | 400 | 700 | not measured |
| 8 | 600 | 683 | 1709 | 450 | 800 | not measured |
| 9 | 700 | 766 | 2563 | 500 | 900 | not measured |

**Recommendation.** Use **100, 150, and 250** for levels 1, 2, and 3. For levels 4 to 9, the first column (follow the DMG table) is the best provisional guide, because it matched all three measured budgets: 100, 150, 250. That gives 300, 400, 500, 550, 600, and 700 for levels 4 to 9. It rests on a table I recalled from memory and on no spell data above level 3, so treat it as a placeholder until level 4 spells are added.

The cantrip budget does not sit on any of these lines. Cantrips can be cast without limit, so they get a quarter of level 1. Do not extend that to other levels.

## 5. Floors, ceilings, and clearances

A floor is the lowest effect total a spell of that level may have. A ceiling is the highest. Effect total means damage, healing, buffs, conditions, utility, and area. Range, duration, and refunds are not counted. Cantrips are capped just under the level 1 floor. From level 1 up, effects cannot exceed the level's budget.

| Level | Budget | Effect floor | Effect ceiling | Lowest effect total | Highest effect total | Lowest net | Highest net |
|---|---|---|---|---|---|---|---|
| Cantrip | 25 | none | 49 | 4 | 19 | 8 | 25 |
| Level 1 | 100 | 50 | 100 | 50 | 94 | 40 | 100 |
| Level 2 | 150 | 100 | 150 | 100 | 127 | 85 | 146 |
| Level 3 | 250 | 150 | 250 | 150 | 209 | 146 | 228 |

The cantrip to level 1 gap is the one you asked for: level 1 effects start at 50, cantrip effects stop at 49. From level 2 up each floor is the previous budget (100, 150) and each ceiling is that level's own budget. Adjacent levels therefore meet exactly at a budget with no overlap: level 1 effects top out at 100 and level 2 effects start at 100. Item tiers and magnitude caps add a second layer of separation, which the stress test checks below.

## 6. Stress test: can a player inflate an existing spell?

For every spell the test raises one lever until the spell stops being legal. Lever one raises the main damage, healing, or temporary HP line. Lever two raises every such line together. Lever three adds targets. Lever four re-files the spell one level lower. Each is run with only the budget enforced and with every rule enforced.

| Level | One magnitude, budget only (median / worst) | One magnitude, all rules | All magnitudes together, budget only | All magnitudes together, all rules | Max extra targets, budget only | Max extra targets, all rules |
|---|---|---|---|---|---|---|
| Cantrip | x1.19 / x2.20 | x1.00 / x1.80 | x1.20 / x2.25 | x1.05 / x1.85 | 3 | 1 |
| Level 1 | x1.72 / x3.30 | x1.00 / x2.08 | x1.62 / x4.05 | x1.00 / x1.50 | 23 | 4 |
| Level 2 | x1.81 / x3.20 | x1.26 / x1.93 | x1.60 / x3.25 | x1.05 / x1.60 | 35 | 5 |
| Level 3 | x1.36 / x3.36 | x1.11 / x1.63 | x1.20 / x3.40 | x1.00 / x1.35 | 41 | 5 |

"All magnitudes together" raises every damage, healing, and temporary HP line of a spell by the same factor, which is the realistic way to try to make a spell much stronger. With every rule on, the median spell can grow about 5% and the worst about 85%. With only the budget, the worst grew 4.0 times.

Largest single-line growth under all rules:

| Spell | Level | Lever | Original | Most the rules allow |
|---|---|---|---|---|
| Witch Bolt | 1 | dmg | 6.5 | 13.5 |
| Flaming Sphere | 2 | dmg | 7 | 13.5 |
| Vicious Mockery | 0 | c_dmg | 2.5 | 4.5 |
| Spirit Guardians | 3 | dmg | 13.5 | 22 |
| Acid Splash | 0 | c_dmg | 3.5 | 5.5 |

The rules cut the worst case but do not remove it. A spell with a small number (Vicious Mockery's d4, Healing Word's d4 plus modifier) can still climb to the strongest value that exists at its level. That is the design: no spell can beat the top of its own level, even if it can get close.

Lever four re-files each spell one level lower and records which rule stops it:

| Filed as | Spells | effect tier | magnitude cap | control cap | effect ceiling | budget | allowed |
|---|---|---|---|---|---|---|---|
| Level 1 spell as a cantrip | 49 | 49 | 0 | 0 | 0 | 0 | 0 |
| Level 2 spell as level 1 | 53 | 41 | 8 | 0 | 0 | 0 | 4 |
| Level 3 spell as level 2 | 43 | 38 | 4 | 0 | 0 | 0 | 1 |

**Weak spot at level 2.** Under the current rules, 4 level 2 spells can be filed as level 1: Aid, Barkskin, Blindness/Deafness, Web. Built only from items available one level down, each fits under that level's budget, so my model sees them as the lower level's strength. Either they are underpriced here, or WotC placed them higher for reasons (duration, range, flexibility) that my items do not capture. I did not patch this, because forcing an extra item into each would be a guess.

**Weak spot at level 3.** Under the current rules, 1 level 3 spell can be filed as level 2: Mass Healing Word. Built only from items available one level down, it fits under that level's budget, so my model sees it as the lower level's strength. Either it is underpriced here, or WotC placed it higher for reasons (duration, range, flexibility) that my items do not capture. I did not patch this, because forcing an extra item into it would be a guess.

## 7. Rules that follow from the study

| Rule | Value |
|---|---|
| Budgets | cantrip 25, level 1 100, level 2 150, level 3 250 |
| Effect floor | level 1: 50. level 2: 100. level 3: 150 |
| Effect ceiling | cantrip: 49. level 1 and up: the budget |
| Items by level | Each item has a minimum level. A spell cannot use an item above its level. |
| Magnitude caps | Damage, healing, temporary HP, targets, AC, and similar items cannot exceed the highest value seen at that level, carried up from lower levels. Damage has separate caps for touch spells, area spells, split-target spells, and cantrips that add a rider. Spells cast as a bonus action or reaction have lower caps for damage and healing. |
| Extra targets | Each extra target costs a share of the spell's per-target lines (damage 70%, control 60%, buffs 50%, healing 25%) and counts toward the control cap. |
| Weak effects pay less for duration | A cantrip with effects under 40 points pays between half and all of the duration price. |
| Area price | Follows the square root of the footprint. |
| Control cap | Strong conditions together cost at most 82 at level 1, 95 at level 2, and 95 at level 3. Cantrips have none. |
| Flat items and duplicates | Taken once. Each item and limit is listed once. |
| Convex price | Price grows with magnitude to the power 1.4, so doubling damage more than doubles the price. |
| Limit refunds | Capped at 50% of the effect cost. |
| Upcasting | Each increase per slot level costs 50% of buying it outright. Targets rise by at most 1 per slot level. A damage or healing increase cannot exceed the base amount per slot level. |

## 8. Limits of this study

- Four levels is too few to pick a curve from spell data alone. The DMG table agrees with the measured budgets, but only if my recollection of it is right.
- Every spell's build, and the price of every level 2 and level 3 item, is my judgment. The calibration tunes category multipliers, not individual items. A mispriced item stays mispriced.
- Level 3 was held out of the price fit, so its budget is a measurement. It is also the least checked: the 43 level 3 builds were written once and have had no second pass.
- The budgets follow the strongest spell at each level. One mispriced standout moves a budget by a full step of 25.
- The level 2 and 3 lists and spell text come from memory. Some SRD spells may be missing.
- Caps come from the spells I built, so a mistake in one build moves a cap.
- Upcasting is priced from the first listed increase only. Spells that scale in other ways pay a flat charge.
- Concentration, saves, and monster hit points are not modeled. Damage is an average roll.
