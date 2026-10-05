// Checks that the builder's pricing code reproduces every canon total recorded in PRICES.md.
const fs = require('fs');
const path = require('path');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const block = html.split('/* PRICING_START */')[1].split('/* PRICING_END */')[0];
const api = new Function(block + '; return { PRESETS, PRICES, priceSpell, budgetStatus, defaultState };')();
let failed = 0;
api.PRESETS.forEach(function (p) {
  const total = api.priceSpell(p.state).total;
  const ok = total === p.expected;
  if (!ok) failed++;
  console.log((ok ? 'ok   ' : 'FAIL ') + p.name + ': ' + total + ' (expected ' + p.expected + ')');
});
// Every preset total must equal the total recorded in PRICES.md.
const md = fs.readFileSync(path.join(__dirname, '..', 'PRICES.md'), 'utf8').split('\n');
const recorded = {};
let sec = null;
md.forEach(function (line) {
  if (/^## Cantrips/.test(line)) sec = 'cantrip';
  else if (/^## Level ([123]) spells/.test(line)) sec = line.match(/^## Level ([123])/)[1];
  else if (/^## /.test(line)) sec = null;
  if (sec && line.charAt(0) === '|') {
    const c = line.split('|').slice(1, -1).map(function (x) { return x.trim(); });
    const total = c[c.length - 1];
    if (/^-?\d+$/.test(total)) recorded[sec + '/' + c[0].replace(/\s*\(.*\)$/, '')] = Number(total);
  }
});
let checked = 0;
api.PRESETS.forEach(function (p) {
  const key = p.level + '/' + p.name;
  if (!(key in recorded)) { failed++; console.log('FAIL not in PRICES.md: ' + key); return; }
  checked++;
  if (recorded[key] !== p.expected) { failed++; console.log('FAIL PRICES.md says ' + recorded[key] + ' for ' + key + ', preset says ' + p.expected); }
  p.state.custom.forEach(function (e) {
    if (e.points > (api.PRICES.effectMax[p.level] || 90)) { failed++; console.log('FAIL effect over its level max: ' + key); }
  });
});
console.log('checked against PRICES.md: ' + checked + ' of ' + api.PRESETS.length + ' presets');
const st = api.budgetStatus('1', 95);
if (st.kind !== 'good') { failed++; console.log('FAIL budget status'); }
const checks = [['cantrip', 50, 'good'], ['cantrip', 51, 'bad'], ['1', 54, 'warn'], ['1', 55, 'good'], ['1', 101, 'bad'], ['2', 104, 'warn'], ['3', 275, 'good'], ['3', 276, 'bad']];
checks.forEach(function (c) {
  const k = api.budgetStatus(c[0], c[1]).kind;
  if (k !== c[2]) { failed++; console.log('FAIL window ' + c[0] + ' at ' + c[1] + ': ' + k); }
});
process.exit(failed ? 1 : 0);
