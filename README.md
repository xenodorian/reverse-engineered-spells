# reverse-engineered-spells

Working from scratch. The earlier spell data and point-buy system are archived:

- `archive/spells-v1/`: cantrip to level 3 spell files.
- `archive/point-buy-v1/`: the first point-buy system (tools, data, docs, examples).

The single source of truth for all prices and spell totals is `PRICES.md`.

## Spell builder

`index.html` is a self-contained web app (no install, no dependencies). Open it in any browser to build a spell from the priced parts and see its cost against the level's point window.

- The prices live in two places: `PRICES.md` (the record) and the `PRICES` object in `index.html`. Update both on every price change.
- `node tests/pricing.test.js` checks that the app reproduces every canon total recorded in `PRICES.md`.
