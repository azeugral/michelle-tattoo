# -*- coding: utf-8 -*-
"""Monta index.html a partir de tools/modelo.html + dados.py, com previa embutida em cada foto. Uso: python tools/montar.py"""
import base64, io, json, sys
from pathlib import Path
from PIL import Image
S = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(S / 'tools'))
import dados

def previa(f):
    i = Image.open(f).convert('RGB').resize((18, 24), Image.LANCZOS)
    b = io.BytesIO(); i.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

def tile(p):
    f = S / f"assets/img/p/{p['id']}.webp"
    return (f'<button class="peca" type="button" data-id="{p["id"]}" aria-label="Abrir {p["leg"]}">'
            f'<span class="peca-q" style="background-image:url({previa(f)})"><img src="assets/img/p/{p["id"]}.webp" alt="{p["leg"]}" width="720" height="960" loading="lazy" draggable="false"></span></button>')

pecas = []
for lado, g in (('e', dados.DELICADO), ('d', dados.DARK)):
    for p in g:
        it = dict(id=p['id'], leg=p['leg'], lado=lado, fotos=[f"assets/img/o/{a}.webp" for a in [p['arq']] + p.get('extra', [])])
        if p['id'] in ('peonia', 'ramo', 'hannya', 'gueixa'): it['video'] = f"assets/video/{p['id']}.mp4"
        pecas.append(it)

h = (S / 'tools/modelo.html').read_text(encoding='utf8')
h = h.replace('{{DELICADO}}', ''.join(tile(p) for p in dados.DELICADO)).replace('{{DARK}}', ''.join(tile(p) for p in dados.DARK))
h = h.replace('{{PECAS}}', json.dumps(pecas, ensure_ascii=False)).replace('{{V}}', '5')
(S / 'index.html').write_text(h, encoding='utf8')
print('index.html', round(len(h) / 1024), 'KB')
