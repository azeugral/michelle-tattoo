# -*- coding: utf-8 -*-
"""Tira a mascara partida (post 06_0) da pele: endireita a lamina e separa tom de tinta e vermelho em camadas.
Saida em _ref/estudo: tom.png (0 = pele, 255 = preto), verm.png (0..255), e prova.jpg."""
import cv2, numpy as np
from pathlib import Path
R = Path(__file__).resolve().parents[2] / '_ref'
im = cv2.imread(str(R / 'ig/06_0.jpg'))
h, w = im.shape[:2]
ANG = -5.0   # graus: deixa a lamina em pe
M = cv2.getRotationMatrix2D((w / 2, h / 2), ANG, 1)
im = cv2.warpAffine(im, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
L, A, B = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128
L0 = cv2.bilateralFilter(L, 5, 9, 3)
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (71, 71))
fundo = cv2.GaussianBlur(cv2.morphologyEx(L0, cv2.MORPH_CLOSE, k), (0, 0), 36)
r = L0 / np.maximum(fundo, 1)
tom = np.clip((.885 - r) / .66, 0, 1)
# vermelho: saturado para o vermelho e claro o bastante
v = np.clip((A - 16) / 16, 0, 1) * np.clip((B - 2) / 12, 0, 1) * np.clip((L0 - 48) / 24, 0, 1)
v = cv2.GaussianBlur(v, (0, 0), 1.0)
v = np.clip((v - .25) / .4, 0, 1)
# regiao da peca: maior componente do traco forte, engordado
forte = ((tom > .42) | (v > .5)).astype(np.uint8)
forte = cv2.morphologyEx(forte, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
n, l, s, _ = cv2.connectedComponentsWithStats(forte, connectivity=8)
ordem = np.argsort(-s[1:, cv2.CC_STAT_AREA])[:6] + 1
print([(i, s[i, :5].tolist()) for i in ordem])
reg = np.zeros_like(forte)
for i in ordem:
    x, y, ww, hh, a = s[i]
    cx = x + ww / 2
    if a > 1500 and 300 < cx < 1250 and x > 240 and (x + ww) < 1260: reg[l == i] = 1
reg = cv2.dilate(reg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (45, 45)))
reg = cv2.GaussianBlur(reg.astype(np.float32), (0, 0), 6)
reg[1380:, :470] = 0
tom *= reg; v *= reg
# tira poros: pontos fracos soltos
tom = np.where(tom < .10, 0, (tom - .10) / .90)
pontos = (tom > .04).astype(np.uint8)
n, l, s, _ = cv2.connectedComponentsWithStats(pontos, connectivity=8)
ok = np.zeros(n, bool); ok[1:] = s[1:, cv2.CC_STAT_AREA] > 240
tom *= cv2.GaussianBlur(ok[l].astype(np.float32), (0, 0), .8)
tom = tom ** .86
tom = tom * (1 - v * .95)
cv2.imwrite(str(R / 'estudo/tom.png'), (tom * 255).astype(np.uint8))
cv2.imwrite(str(R / 'estudo/verm.png'), (v * 255).astype(np.uint8))
# prova: contracambio no eixo
ys, xs = np.where(tom > .3); print('caixa', xs.min(), xs.max(), ys.min(), ys.max())
papel = np.array([224, 234, 240], np.float32); preto = np.array([10, 9, 11], np.float32); rub = np.array([38, 44, 214], np.float32)
eixo = int(np.median(xs))
sai = np.zeros((h, w, 3), np.float32)
T = tom[..., None]; V = v[..., None]
esq = papel * (1 - T) + preto * T; dir_ = preto * (1 - T) + papel * T
sai[:, :eixo] = esq[:, :eixo]; sai[:, eixo:] = dir_[:, eixo:]
sai = sai * (1 - V) + rub * V
cv2.imwrite(str(R / 'estudo/prova.jpg'), sai.astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 90]); print(eixo)
