# -*- coding: utf-8 -*-
"""Separa o antes e depois da foto da reforma e alinha as duas metades pelos tracos antigos."""
import cv2, numpy as np
from pathlib import Path
S = Path(__file__).resolve().parent.parent; R = S.parent / '_ref/ig'
i = cv2.imread(str(R / '16_0.jpg'))
A = i[:, :716]; D = i[:, 724:]
# pontos em comum (x,y) em px da metade: olho, nariz, boca, pontas do tribal
pa = np.float32([(320,824),(470,1010),(410,1136),(150,1670),(430,1720)])
pd = np.float32([(276,886),(420,1062),(390,1200),(226,1700),(516,1700)])
M, _ = cv2.estimateAffinePartial2D(pa, pd, method=cv2.LMEDS)
print(M)
Aw = cv2.warpAffine(A, M, (D.shape[1], D.shape[0]), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(11, 10, 11))
y = 470; alt = 1160; lar = 696; x = (D.shape[1] - lar) // 2
for nome, im in (('antes', Aw), ('depois', D)):
    c = im[y:y + alt, x:x + lar]
    lab = cv2.cvtColor(c, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[..., 1] = 128 + (lab[..., 1] - 128) * .42; lab[..., 2] = 128 + (lab[..., 2] - 128) * .42
    c = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
    c = cv2.resize(c, (900, 1500), interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(str(S / f'assets/img/{nome}.webp'), c, [cv2.IMWRITE_WEBP_QUALITY, 86])
print(lar, alt)
