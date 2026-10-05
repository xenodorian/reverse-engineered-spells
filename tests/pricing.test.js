// Checks that the builder's pricing code reproduces every canon total recorded in PRICES.md.
const fs = require('fs');
const path = require('path');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const block = html.split('/* PRICING_START */')[1].split('/* PRICING_END */')[0];
const api = new Function(block + '; return { PRESETS, priceSpell, budgetStatus, defaultState };')();
let failed = 0;
api.PRESETS.forEach(function (p) {
  const total = api.priceSpell(p.state).total;
  const ok = total === p.expected;
  if (!ok) failed++;
  console.log((ok ? 'ok   ' : 'FAIL ') + p.name + ': ' + total + ' (expected ' + p.expected + ')');
});
const st = api.budgetStatus('1', 95);
if (st.kind !== 'good') { failed++; console.log('FAIL budget status'); }
process.exit(failed ? 1 : 0);
