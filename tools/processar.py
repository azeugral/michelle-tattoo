# -*- coding: utf-8 -*-
"""Recorta o corpo da foto e assenta no chao do lado (papel ou preto), em 4:5. Saida: assets/img/p/<id>.webp, foto original em assets/img/o/<arq>.webp.
Uso: python tools/processar.py [ids]"""
import sys, cv2, numpy as np
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import importlib, dados; importlib.reload(dados)
SITE = Path(__file__).resolve().parent.parent; REF = SITE.parent / '_ref'
P = SITE / 'assets/img/p'; O = SITE / 'assets/img/o'; M = REF / 'mascaras'
for d in (P, O, M): d.mkdir(parents=True, exist_ok=True)

PAPEL = np.array([224, 234, 240], np.float32); PRETO = np.array([11, 10, 11], np.float32)
W, H = 960, 1200

POLI = {
 '05_0': [(.50,0),(1,0),(1,.1),(.82,.25),(.73,.45),(.68,.6),(.66,.8),(.60,1),(.27,1),(.33,.75),(.29,.55),(.31,.40),(.42,.16)],
 '03_0': [(.0,.22),(.12,.10),(.30,.03),(.35,0),(.62,0),(.72,.06),(.85,.12),(.97,.22),(.93,.45),(.90,.68),(.90,.85),(.92,1),(.10,1),(.13,.85),(.10,.72),(.03,.52)],
 '22_0': [(.32,0),(.74,0),(.66,.3),(.68,.5),(.72,.7),(.76,1),(.14,1),(.15,.7),(.20,.5),(.27,.3)],
 '08_0': [(.24,0),(.80,0),(.80,.25),(.76,.5),(.70,.75),(.65,1),(.30,1),(.27,.75),(.29,.5),(.25,.25)],
 '17_0': [(.18,0),(.85,0),(.82,.25),(.80,.5),(.76,.75),(.72,1),(.26,1),(.22,.75),(.20,.5),(.19,.25)],
 '13_0': [(.20,0),(.78,0),(.75,.25),(.73,.5),(.62,.75),(.60,1),(.32,1),(.29,.75),(.28,.5),(.24,.25)],
 '21_0': [(.20,0),(.77,0),(.76,.2),(.70,.5),(.65,.75),(.62,1),(.36,1),(.34,.8),(.29,.5),(.23,.2)],
 '04_0': [(.09,0),(.69,0),(1,.14),(1,1),(.09,1)],
}
INTEIRA = {'11_0','18_0','19_0','20_0'}

def por_contorno(nome, bgr):
    h, w = bgr.shape[:2]
    e = 720 / max(h, w)
    p = cv2.resize(bgr, None, fx=e, fy=e, interpolation=cv2.INTER_AREA)
    hh, ww = p.shape[:2]
    base = np.zeros((hh, ww), np.uint8)
    cv2.fillPoly(base, [np.int32([(x * ww, y * hh) for x, y in POLI[nome]])], 1)
    k = int(.06 * ww) | 1
    cert = cv2.erode(cv2.copyMakeBorder(base, 40, 40, 40, 40, cv2.BORDER_REPLICATE), np.ones((k, k), np.uint8))[40:-40, 40:-40]
    prov = cv2.dilate(base, np.ones((k, k), np.uint8))
    gc = np.full(base.shape, cv2.GC_BGD, np.uint8)
    gc[prov > 0] = cv2.GC_PR_BGD; gc[base > 0] = cv2.GC_PR_FGD; gc[cert > 0] = cv2.GC_FGD
    cv2.grabCut(p, gc, None, np.zeros((1, 65)), np.zeros((1, 65)), 5, cv2.GC_INIT_WITH_MASK)
    m = ((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD)).astype(np.uint8)
    m = cv2.morphologyEx(cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8)), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, l, s, _ = cv2.connectedComponentsWithStats(m)
    m = (l == 1 + np.argmax(s[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    m = cv2.resize(m.astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    return (cv2.GaussianBlur(m, (0, 0), 3.2) * 255).clip(0, 255).astype(np.uint8)

def mascara(nome, bgr):
    """Pele pela cor (croma), tinta incluida por fechamento e buracos, borda refinada com GrabCut."""
    f = M / f'{nome}.png'
    if f.exists(): return cv2.imread(str(f), 0)
    if nome in INTEIRA:
        m = np.full(bgr.shape[:2], 255, np.uint8); cv2.imwrite(str(f), m); return m
    if nome in POLI:
        m = por_contorno(nome, bgr); cv2.imwrite(str(f), m); return m
    h, w = bgr.shape[:2]
    e = 720 / max(h, w)
    p = cv2.resize(bgr, None, fx=e, fy=e, interpolation=cv2.INTER_AREA)
    pp = cv2.bilateralFilter(p, 9, 40, 9)
    lab = cv2.cvtColor(pp, cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, B = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128
    hsv = cv2.cvtColor(pp, cv2.COLOR_BGR2HSV)
    pele = ((A > 5) & (B > 4) & (L > 45) & (B < 46) & (A > B * .28)).astype(np.uint8)
    pele = cv2.morphologyEx(pele, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, l, s, _ = cv2.connectedComponentsWithStats(pele)
    base = np.zeros_like(pele)
    if n > 1:
        grande = s[1:, cv2.CC_STAT_AREA].max()
        for i in range(1, n):
            if s[i, cv2.CC_STAT_AREA] > grande * .12: base[l == i] = 1
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (45, 45))
    fech = cv2.morphologyEx(base, cv2.MORPH_CLOSE, k)
    # preenche buracos (tinta preta grande) sem vazar pela borda da foto
    pad = cv2.copyMakeBorder(fech, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    ff = pad.copy(); cv2.floodFill(ff, None, (0, 0), 2)
    fech = np.where(ff[1:-1, 1:-1] == 2, 0, 1).astype(np.uint8)
    cert = cv2.erode(fech, np.ones((15, 15), np.uint8))
    prov = cv2.dilate(fech, np.ones((25, 25), np.uint8))
    gc = np.full(fech.shape, cv2.GC_BGD, np.uint8)
    gc[prov > 0] = cv2.GC_PR_BGD; gc[fech > 0] = cv2.GC_PR_FGD; gc[cert > 0] = cv2.GC_FGD
    if (gc == cv2.GC_PR_BGD).sum() > 50 and (fech == 0).mean() > .02:
        cv2.grabCut(p, gc, None, np.zeros((1, 65)), np.zeros((1, 65)), 4, cv2.GC_INIT_WITH_MASK)
    m = ((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD)).astype(np.uint8)
    n, l, s, _ = cv2.connectedComponentsWithStats(m)
    if n > 1:
        grande = s[1:, cv2.CC_STAT_AREA].max()
        m = np.isin(l, [i for i in range(1, n) if s[i, cv2.CC_STAT_AREA] > grande * .1]).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    m = cv2.resize(m.astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    m = (cv2.GaussianBlur(m, (0, 0), 3) * 255).clip(0, 255).astype(np.uint8)
    cv2.imwrite(str(f), m); return m

def peca(p, lado):
    bgr = cv2.imread(str(REF / 'ig' / f"{p['arq']}.jpg"))
    h, w = bgr.shape[:2]
    m = mascara(p['arq'], bgr).astype(np.float32) / 255
    # contorno liso: borra forte e corta de novo, some o serrilhado do GrabCut
    m = cv2.GaussianBlur(m, (0, 0), 16)
    m = np.clip((m - .50) / .03, 0, 1)
    m = cv2.GaussianBlur(m, (0, 0), 1.6)
    # tom: pele neutra e fria o bastante para os dois lados conversarem
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[..., 1] = 128 + (lab[..., 1] - 128) * .42
    lab[..., 2] = 128 + (lab[..., 2] - 128) * .42
    L = lab[..., 0] / 255
    alvoL = .72 if lado == 'd' else .80
    med = np.percentile(L[m > .6], 88) if (m > .6).any() else .7
    L = np.clip(L * min(alvoL / med, 1.35), 0, 1)
    L = L ** (1.12)           # preto mais denso
    lab[..., 0] = L * 255
    tom = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
    ch = PRETO if lado == 'd' else PAPEL
    A = m[..., None]
    sai = tom * A + ch * (1 - A)
    # moldura 4:5
    cw = min(w, h * .8) / p.get('zoom', 1); chh = cw / .8
    x0 = int(np.clip(p['foco'][0] * w - cw / 2, 0, w - cw)); y0 = int(np.clip(p['foco'][1] * h - chh / 2, 0, h - chh))
    c = sai[y0:int(y0 + chh), x0:int(x0 + cw)]
    c = cv2.resize(c, (W, H), interpolation=cv2.INTER_LANCZOS4 if cw < W else cv2.INTER_AREA)
    Image.fromarray(cv2.cvtColor(np.clip(c, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)).save(P / f"{p['id']}.webp", quality=88, method=6)
    for a in [p['arq']] + p.get('extra', []):
        Image.open(REF / 'ig' / f'{a}.jpg').convert('RGB').save(O / f'{a}.webp', quality=86, method=6)

alvo = sys.argv[1:]
for lado, g in (('e', dados.DELICADO), ('d', dados.DARK)):
    for p in g:
        if not alvo or p['id'] in alvo: peca(p, lado); print(p['id'], flush=True)
# folha
T = 240
linhas = []
for g in (dados.DELICADO, dados.DARK):
    fs = [Image.open(P / f"{p['id']}.webp").resize((T, int(T * 1.25))) for p in g]
    s = Image.new('RGB', (T * 5, int(T * 1.25) * 2))
    for i, f in enumerate(fs): s.paste(f, ((i % 5) * T, (i // 5) * int(T * 1.25)))
    linhas.append(s)
f = Image.new('RGB', (T * 10, linhas[0].height)); f.paste(linhas[0], (0, 0)); f.paste(linhas[1], (T * 5, 0)); f.save(REF / 'folha-pecas.jpg', quality=86)
