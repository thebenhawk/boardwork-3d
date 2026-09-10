import json, re, subprocess, os

pdfs = json.load(open('db_pdf.json'))
tsv  = json.load(open('db_tsv.json'))

def clean(n):
    n = n.replace("'", "").strip()
    n = re.sub(r'^(26|2026|25|2025)\s+', '', n)
    n = re.sub(r'\s*\(\d{4}\)$', '', n)
    return ' '.join(w.capitalize() if w.isalpha() else w for w in n.split())

DB = {}

# --- 1. PDF load-table patterns (exact, row-validated) ---
for o in pdfs:
    rows = []
    for tag, rs in (('F', o['fwd']), ('R', o['rev'])):
        for r in rs:
            if r['loads'] == 0: continue
            d0, d1 = min(r['d0'], r['d1']), max(r['d0'], r['d1'])
            if d1 <= d0: d0, d1 = d0, d0 + 0.5      # prime dump at the foul line
            rows.append([r['b0'], r['b1'], r['loads'], r['mics'], round(d0,2), round(d1,2)])
    DB[clean(o['name'])] = {
        'src':'loads', 'sheet':'PDF', 'distance':o['distance'], 'volume':o['volume'],
        'ratio':o['ratio'], 'dropBrush':o['dropBrush'],
        'fwdVol':o['fwdVol'], 'revVol':o['revVol'], 'rows':rows}

# --- 2. Regional 37 (transcribed earlier, verified exact) ---
def bd(t):
    n=int(t[:-1]); return 40-n if t[-1]=='L' else n
reg_rows=[]
for s,e,l,m,d0,d1 in [("2L","2R",3,50,0,4),("2L","6R",1,50,4,6),("7L","7R",3,50,6,12),
    ("4L","9R",2,50,12,16),("11L","10R",3,50,16,23),("13L","12R",2,50,23,28),
    ("11L","11R",2,50,23,29),("9L","8R",2,50,18,23),("7L","7R",2,50,13,18),
    ("6L","6R",1,50,11,13),("2L","2R",3,50,5,11)]:
    reg_rows.append([min(bd(s),bd(e)), max(bd(s),bd(e)), l, m, d0, d1])
DB['Regional 37'] = {'src':'loads','sheet':'PDF','distance':37,'volume':32.65,
    'ratio':'3.08:1','dropBrush':30,'fwdVol':18.65,'revVol':14.0,'rows':reg_rows}

# --- 3. Badger 50 (machine .txt only - no sheet to validate against) ---
L = open('/mnt/project/26_BADGER_50.txt', encoding='utf-8', errors='replace').read().splitlines()
def blk(a,b): return [x for x in L[a:b] if x.strip()]
bad_rows=[]
for st, sp, ld, mc, ds in [(blk(151,166), blk(166,181), blk(44,59), blk(255,271), blk(136,151)),
                           (blk(181,196), blk(196,211), blk(105,120), blk(271,286), blk(211,227))]:
    ends=[float(x) for x in ds]
    prev = 0.0 if ends[0] < ends[-1] else ends[0]
    seq  = ends[1:] if ends[0] >= ends[-1] else ends
    for i, e in enumerate(seq):
        if i >= len(ld): break
        n=int(ld[i])
        d0,d1 = min(prev,e), max(prev,e)
        if n>0 and d1>d0:
            bad_rows.append([min(bd(st[i]),bd(sp[i])), max(bd(st[i]),bd(sp[i])),
                             n, int(mc[i]), round(d0,2), round(d1,2)])
        prev = e
badvol = sum(r[2]*r[3]*(r[1]-r[0]+1) for r in bad_rows)/1000
DB['Badger 50'] = {'src':'loads','sheet':'TXT','distance':50,'volume':round(badvol,2),
    'ratio':None,'dropBrush':None,'fwdVol':None,'revVol':None,'rows':bad_rows,
    'note':'machine file only - volume derived from loads, not sheet-verified'}

# --- 4. Wolf 34 from the zone/board units matrix (its PDF has no load table) ---
w = [v for k,v in tsv.items() if 'WOLF' in k.upper()][0]
DB['Wolf 34'] = {'src':'zones','sheet':'TSV','distance':w['zoneEnd'][-1],
    'volume':round(w['volume'],3),'ratio':None,'dropBrush':None,
    'fwdVol':None,'revVol':None,
    'boards':w['boards'],'zoneEnd':w['zoneEnd'],
    'zoneVol':[round(x,5) for x in w['zoneVol']],'zoneUnits':w['zoneUnits']}

print(f"{'PATTERN':16s} {'SRC':6s} {'DIST':>5s} {'VOL':>7s} {'ROWS':>5s}  RATIO")
for k in sorted(DB):
    d=DB[k]
    n = len(d['rows']) if d['src']=='loads' else f"{len(d['zoneUnits'])}z"
    print(f"{k:16s} {d['sheet']:6s} {d['distance']:>4.0f}f {d['volume']:>6.2f}mL {str(n):>5s}  {d['ratio'] or '-'}")
json.dump(DB, open('patterns.json','w'))
print(f"\n{len(DB)} patterns in database")
