import re, glob, os, json

NUM = re.compile(r'^-?\d+(\.\d+)?([eE][-+]?\d+)?$')
def nums(cells, limit=None):
    out=[]
    for c in cells:
        c=c.strip()
        if not c: continue
        if NUM.match(c): out.append(float(c))
        elif out: break          # stop at first non-numeric AFTER numbers start
    return out[:limit] if limit else out

def parse_tsv(path):
    L = open(path, encoding='utf-8', errors='replace').read().split('\n')
    def C(i): return L[i].split('\t')
    def find(pred, lo=0, hi=None):
        for i in range(lo, hi or len(L)):
            if pred(L[i]): return i
        return -1
    o={}
    i=find(lambda s: s.startswith('Pattern Volume'));  o['volume']=nums(C(i))[0]
    i=find(lambda s: 'Pattern Name' in s)
    cs=[c.strip() for c in C(i) if c.strip()]; o['name']=cs[cs.index('Pattern Name')+1]
    i=find(lambda s: s.startswith('Pattern Type'))
    o['type']=[c.strip() for c in C(i) if c.strip()][1]
    i=find(lambda s: s.startswith('Pattern Difficulty'))
    o['difficulty']=[c.strip() for c in C(i) if c.strip()][1] if i>=0 else ''
    i=find(lambda s: s.startswith('Zone End Distance')); o['zoneEnd']=nums(C(i),8)
    i=find(lambda s: s.startswith('Zone Volume'));       o['zoneVol']=nums(C(i),8)

    h=find(lambda s: '\tL1\t' in s or s.startswith('L1\t'))
    hdr=[c.strip() for c in C(h) if re.fullmatch(r'[LRC]\d+', c.strip())]
    boards=[(40-int(c[1:]) if c[0]=='L' else (20 if c[0]=='C' else int(c[1:]))) for c in hdr]

    zones=[]
    for z in range(1,9):
        r=find(lambda s,z=z: s.split('\t')[0].strip()==str(z), h+1, h+14)
        if r<0: break
        v=[c for c in C(r) if c.strip()]
        n=[float(x) for x in v[1:1+len(boards)] if NUM.match(x.strip())]
        if len(n)!=len(boards): break
        zones.append(n)
    o['boards']=boards; o['zoneUnits']=zones
    i=find(lambda s: s.startswith('Outside Track: Middle'))
    o['zoneRatios']=nums(C(i+1),6) if i>=0 else []
    return o

DB={}
for f in sorted(glob.glob('/mnt/project/*.xlsx')):
    try: p=parse_tsv(f)
    except Exception as e:
        print(os.path.basename(f),'FAILED',e); continue
    zs=sum(p['zoneVol'])
    ok = abs(zs-p['volume'])<0.002 and len(p['boards'])==39
    print(f"{p['name']:14s} {p['volume']:6.3f}ml  zones={len(p['zoneUnits'])} ends={p['zoneEnd']}")
    print(f"   zoneVol sum {zs:.4f} vs stated {p['volume']:.4f}  boards={len(p['boards'])}  {'OK' if ok else '<< CHECK'}")
    DB[p['name']]=p
json.dump(DB, open('db_tsv.json','w'))
print('\nparsed', len(DB), 'patterns from TSV')
