import re, glob, os, json, subprocess

def board(tok):
    m = re.fullmatch(r'(\d+)([LR])', tok.strip())
    if not m: return None
    n, side = int(m.group(1)), m.group(2)
    return 40-n if side=='L' else n           # board 39 = left gutter

def parse_pdf(path):
    txt = subprocess.run(['pdftotext','-layout',path,'-'],capture_output=True,text=True).stdout
    lines = txt.split('\n')
    o = {'file': os.path.basename(path)}
    head = '\n'.join(lines[:8])
    def grab(label, pat=r'([\d.]+)'):
        m = re.search(label+r'\s*:?\s*'+pat, head)
        return m.group(1) if m else None
    o['name']    = lines[0].strip() or lines[1].strip()
    o['distance']= float(grab('DISTANCE'))
    o['volume']  = float(grab('VOLUME'))
    o['ratio']   = grab('RATIO', r'([\d.]+:\d+)')
    o['dropBrush']=float(grab('DROP BRUSH') or 0)
    fwd_m = re.search(r'FORWARD:\s*([\d.]+)', head)
    rev_m = re.search(r'REVERSE:\s*([\d.]+)', head)
    o['fwdVol'] = float(fwd_m.group(1)) if fwd_m else None
    o['revVol'] = float(rev_m.group(1)) if rev_m else None

    ROW = re.compile(
      r'^\s*(\d+)\s+(\d+[LR])\s+(\d+[LR])\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+'
      r'(.+?)\s+([\d.]+)\s*(?:→|->)\s*([\d.]+)\s+([\d,]+)\s*$')
    fwd, rev, cur = [], [], None
    for ln in lines:
        if 'FORWARD LOADS DATA' in ln: cur = fwd; continue
        if 'REVERSE LOADS DATA' in ln: cur = rev; continue
        if cur is None: continue
        m = ROW.match(ln)
        if not m: continue
        b0, b1 = board(m.group(2)), board(m.group(3))
        cur.append({'start':m.group(2),'stop':m.group(3),
                    'b0':min(b0,b1),'b1':max(b0,b1),
                    'loads':int(m.group(4)),'mics':int(m.group(5)),
                    'speed':int(m.group(6)),
                    'd0':float(m.group(9)),'d1':float(m.group(10)),
                    'toil':int(m.group(11).replace(',',''))})
    o['fwd'], o['rev'] = fwd, rev
    return o

def check(o):
    bad, tot = [], 0
    for tag, rows in (('F',o['fwd']),('R',o['rev'])):
        for i,r in enumerate(rows,1):
            calc = r['loads']*r['mics']*(r['b1']-r['b0']+1)
            tot += calc
            if calc != r['toil']: bad.append(f"{tag}{i} calc {calc} vs sheet {r['toil']}")
    return tot, bad

results=[]
for f in sorted(glob.glob('/mnt/project/*.pdf')):
    try: o=parse_pdf(f)
    except Exception as e:
        print(f'{os.path.basename(f):28s} PARSE FAIL {e}'); continue
    tot,bad = check(o)
    vol_ok = abs(tot/1000 - o['volume']) < 0.02
    print(f"{o['name'][:22]:24s} {o['distance']:>5.0f}ft  sheet {o['volume']:6.2f}mL  "
          f"recon {tot/1000:6.2f}mL  rows F{len(o['fwd'])}/R{len(o['rev'])}  "
          f"{'OK' if vol_ok and not bad else '<< ' + (';'.join(bad[:2]) if bad else 'VOL DIFF')}")
    o['reconTotal']=tot
    results.append(o)
json.dump(results, open('db_pdf.json','w'))
print(f'\nparsed {len(results)} pattern sheets from PDF')
