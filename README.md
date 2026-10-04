# reverse-engineered-spells

Structured data for D&D 5th edition (2014) spells, with mechanics reimplemented in original wording.

## Contents

- `spells/level-1/`: the 49 first-level spells on the SRD 5.1 list, one JSON file each.
- `docs/creating-a-spell.md`: original-wording summary of the 2014 DMG spell creation guidance (unverified against the book).
- `docs/spell-point-buy.md`: 100 point build system with cost and refund tables and a scorecard for all 49 spells.
- `tools/pointbuy.py`: calculator (`report`, `score`, `calc`). Data in `data/`, example in `examples/`.

Fields: name, level, school, casting_time, range, components, material, duration, concentration, ritual, classes, description, at_higher_levels, source.

Notes: Hideous Laughter is listed under its short name (the full name is Tasha's Hideous Laughter). Non-SRD first-level spells are not included.
