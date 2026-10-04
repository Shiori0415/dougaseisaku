import re
h=open('kouban_new.html').read()
body=h[h.index('<body'):]
# 見出しの段落
title=re.sub(r'<[^>]+>','',body[:body.index('<table')]).strip()
rows=re.findall(r'<tr[^>]*>.*?</tr>',body,re.S)
W=['93pt','98.2pt','436.5pt','120pt']
STY={'#ff0000':'r','#0000ff':'bb','#38761d':'g'}
out=[]
for ri,r in enumerate(rows):
    tds=re.findall(r'<td[^>]*>(.*?)</td>',r,re.S); cells=[]
    for ci,td in enumerate(tds):
        ps=[]
        for p in re.findall(r'<p[^>]*>(.*?)</p>',td,re.S):
            segs=''
            for st,tx in re.findall(r'<span([^>]*)>(.*?)</span>',p,re.S):
                c=re.search(r'color:(#[0-9a-f]+)',st); b='font-weight:700' in st
                cls=STY.get(c.group(1) if c else '','')
                if ri==0: cls='h'
                elif b and cls!='bb': cls='b'
                segs+=f'<span class="{cls}">{tx}</span>' if cls else tx
            ps.append(f'<p>{segs}</p>')
        cells.append(f'<td class="{"th" if ri==0 else ""}" style="width:{W[ci]}">'+''.join(ps)+'</td>')
    out.append('<tr>'+''.join(cells)+'</tr>')
css=('<style>body{font-family:Arial;font-size:11pt}p{margin:0;line-height:1.0}'
 'table{border-collapse:collapse;margin-left:-12pt}td{border:1pt solid #000000;padding:5pt;vertical-align:top;font-size:11pt}'
 'td.th{background-color:#073763;border-color:#ffffff;border-bottom-color:#000000}'
 '.h{color:#ffffff;font-weight:700}.r{color:#ff0000}.bb{color:#0000ff;font-weight:700}.b{font-weight:700}.g{color:#38761d}'
 'h1{font-size:12pt;font-weight:700;margin:0 0 3pt}</style>')
html=f'<html><head><meta charset="utf-8">{css}</head><body><p><b>{title}</b></p><table>'+''.join(out)+'</table></body></html>'
html=re.sub(r'<span class="([a-z]+)"></span>','',html)
open('kouban_compact.html','w').write(html); print(len(html))
