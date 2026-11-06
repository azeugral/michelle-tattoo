# -*- coding: utf-8 -*-
"""Recorta a arte no eixo da lamina e completa a ponta. Saida assets/img/hero/{tom,verm}.webp (800x2140)."""
import cv2, numpy as np
from pathlib import Path
from PIL import Image
S = Path(__file__).resolve().parent.parent; E = S.parent / '_ref/estudo'
tom = cv2.imread(str(E / 'tom.png'), 0); ver = cv2.imread(str(E / 'verm.png'), 0)
EIXO = 749; W = 800; X0 = EIXO - W // 2; EXTRA = 220
Y0 = 1668   # abaixo do queixo da mascara: daqui para baixo a propria lamina afina ate virar ponta
def faz(a):
    a = a[:, X0:X0 + W].astype(np.float32)
    H = a.shape[0] + EXTRA
    sai = np.zeros((H, W), np.float32)
    sai[:Y0] = a[:Y0]
    xs0 = np.arange(W) - W / 2
    for y in range(Y0, H):
        t = (y - Y0) / (H - 1 - Y0)
        sy = Y0 + t * (a.shape[0] - 1 - Y0)
        y0 = int(sy); y1 = min(y0 + 1, a.shape[0] - 1); k = sy - y0
        lin = a[y0] * (1 - k) + a[y1] * k
        f = max(1 - t ** 2.2, .003)
        sai[y] = np.interp(xs0 / f + W / 2, np.arange(W), lin, left=0, right=0)
    return sai
t = faz(tom); v = faz(ver)
t = cv2.GaussianBlur(t, (0, 0), .5)
for n, a in (('tom', t), ('verm', v)):
    Image.fromarray(a.clip(0, 255).astype(np.uint8)).save(S / f'assets/img/hero/{n}.webp', quality=90, method=6)
    print(n, a.shape, round((S / f'assets/img/hero/{n}.webp').stat().st_size / 1024), 'KB')
