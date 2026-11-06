# -*- coding: utf-8 -*-
"""Foto real em 3:4, sem recorte do corpo, com o mesmo tom em todas. Saida: assets/img/p/<id>.webp, foto original em assets/img/o/<arq>.webp.
Uso: python tools/processar.py [ids]"""
import sys, cv2, numpy as np
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
import dados
SITE = Path(__file__).resolve().parent.parent; REF = SITE.parent / '_ref'
P = SITE / 'assets/img/p'; O = SITE / 'assets/img/o'
P.mkdir(parents=True, exist_ok=True); O.mkdir(parents=True, exist_ok=True)
W, H = 720, 960

def tom(bgr, lado):
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[..., 1] = 128 + (lab[..., 1] - 128) * .42
    lab[..., 2] = 128 + (lab[..., 2] - 128) * .42
    L = lab[..., 0] / 255
    alvo = .74 if lado == 'd' else .82
    ref = np.percentile(L, 88)
    L = np.clip(L * min(alvo / ref, 1.3), 0, 1) ** 1.1
    lab[..., 0] = L * 255
    return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)

def enquadra(bgr, p):
    h, w = bgr.shape[:2]
    if p.get('cheia') and w / h > .75:
        # foto larga: inteira no meio, a pele continua espelhada e desfocada em cima e embaixo
        alt = int(round(w / .75)); pad = (alt - h) // 2
        ref = cv2.copyMakeBorder(bgr, pad, alt - h - pad, 0, 0, cv2.BORDER_REFLECT_101)
        bor = cv2.GaussianBlur(ref, (0, 0), 34)
        mk = np.zeros((alt, w), np.float32); mk[pad:pad + h] = 1
        mk = cv2.GaussianBlur(mk, (0, 0), 46)[..., None]
        return (ref * mk + bor * (1 - mk)).astype(np.uint8)
    cw = min(w, h * .75) / p.get('zoom', 1); ch = cw / .75
    x0 = int(np.clip(p['foco'][0] * w - cw / 2, 0, w - cw)); y0 = int(np.clip(p['foco'][1] * h - ch / 2, 0, h - ch))
    return bgr[y0:int(y0 + ch), x0:int(x0 + cw)]

def peca(p, lado):
    bgr = cv2.imread(str(REF / 'ig' / f"{p['arq']}.jpg"))
    c = enquadra(tom(bgr, lado), p)
    c = cv2.resize(c, (W, H), interpolation=cv2.INTER_AREA)
    Image.fromarray(cv2.cvtColor(c, cv2.COLOR_BGR2RGB)).save(P / f"{p['id']}.webp", quality=86, method=6)
    for a in [p['arq']] + p.get('extra', []):
        if not (O / f'{a}.webp').exists():
            Image.open(REF / 'ig' / f'{a}.jpg').convert('RGB').save(O / f'{a}.webp', quality=86, method=6)

alvo = sys.argv[1:]
for lado, g in (('e', dados.DELICADO), ('d', dados.DARK)):
    for p in g:
        if not alvo or p['id'] in alvo: peca(p, lado); print(p['id'], flush=True)
T = 200; lin = []
s = Image.new('RGB', (T * 10, int(T / .75) * 2))
for k, g in enumerate((dados.DELICADO, dados.DARK)):
    for i, p in enumerate(g):
        s.paste(Image.open(P / f"{p['id']}.webp").resize((T, int(T / .75))), ((i % 5 + k * 5) * T, (i // 5) * int(T / .75)))
s.save(REF / 'folha-pecas.jpg', quality=86)
