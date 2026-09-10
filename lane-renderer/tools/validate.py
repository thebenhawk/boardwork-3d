#!/usr/bin/env python3
"""Re-check every pattern in the database against its source sheet."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB = json.load(open(os.path.join(HERE, '..', 'data', 'kegel_patterns.json')))
MAT_IN = 714          # 59.5 ft of one-inch steps

def build(p):
    m = [[0.0]*MAT_IN for _ in range(40)]
    if p['src'] == 'loads':
        for b0, b1, loads, mics, d0, d1 in p['rows']:
            if loads == 0 or d1 <= d0: continue
            per = loads*mics/((d1-d0)*12)
            i0, i1 = round(d0*12), min(MAT_IN, round(d1*12))
            for b in range(b0, b1+1):
                for i in range(i0, i1): m[b][i] += per
    else:
        prev = 0.0
        for z, end in enumerate(p['zoneEnd']):
            if z >= len(p['zoneUnits']): break
            u = p['zoneUnits'][z]; s = sum(u)
            i0, i1 = round(prev*12), min(MAT_IN, round(end*12))
            if s > 0 and i1 > i0:
                vol = p['zoneVol'][z]*1000
                for k, b in enumerate(p['boards']):
                    per = vol*u[k]/s/(i1-i0)
                    for i in range(i0, i1): m[b][i] += per
            prev = end
    return m

fail = 0
print(f"{'PATTERN':15s} {'SHEET':>8s} {'BUILT':>8s} {'PEAK bd':>8s} {'EDGE bd':>8s}  RESULT")
for k in sorted(DB):
    p = DB[k]
    m = build(p)
    tot = sum(sum(r) for r in m)/1000
    bt = [sum(m[b]) for b in range(40)]
    tol = 0.15 if p.get('note') else 0.02
    ok = abs(tot - p['volume']) < tol
    if not ok: fail += 1
    print(f"{k:15s} {p['volume']:>7.2f}mL {tot:>7.2f}mL "
          f"{max(bt[1:40]):>8.0f} {bt[3]:>8.0f}  {'OK' if ok else 'FAIL'}")

    # row-level check for load-based patterns
    if p['src'] == 'loads':
        for b0, b1, loads, mics, d0, d1 in p['rows']:
            if b0 < 1 or b1 > 39 or b0 > b1:
                print(f"   !! bad board range {b0}-{b1}"); fail += 1

print(f"\n{len(DB)} patterns, {fail} failures")
sys.exit(1 if fail else 0)
