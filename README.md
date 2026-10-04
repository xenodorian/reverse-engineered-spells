# reverse-engineered-spells

Structured data for D&D 5th edition (2014) spells, with mechanics reimplemented in original wording.

## Contents

- `spells/cantrip/`: the 24 SRD cantrips, one JSON file each.
- `spells/level-1/`: the 49 first-level spells on the SRD 5.1 list, one JSON file each.
- `spells/level-2/`: the 53 level 2 spells I recalled from the SRD 5.1 list, one JSON file each (list not verified against the SRD).
- `docs/creating-a-spell.md`: original-wording summary of the 2014 DMG spell creation guidance (unverified against the book).
- `docs/spell-point-buy.md`: point-buy system (cantrip 25, level 1 100, level 2 150) with rules, price and refund tables, and scorecards.
- `docs/spell-scaling-analysis.md`: how the budget scales across cantrips, level 1, and level 2, the calibration, and a stress test of the rules.
- `docs/revision-log.md`: what the second logic pass found and changed.
- `tools/`: `pointbuy.py` is the calculator (`fit`, `report`, `score`, `calc`, `stress`, `check`). Prices are in `pricing.py`, per-spell builds in `builds.py`. Data in `data/`, examples in `examples/`.

Fields: name, level, school, casting_time, range, components, material, duration, concentration, ritual, classes, description, at_higher_levels, source.

Notes: Hideous Laughter is listed under its short name (the full name is Tasha's Hideous Laughter). Non-SRD first-level spells are not included.
