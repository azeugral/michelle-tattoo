# -*- coding: utf-8 -*-
"""Capturas por secao. Uso: python tools/fotos.py [url] [ld|cel|ambos]"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
URL = next((a for a in sys.argv[1:] if a.startswith('http')), 'http://localhost:8899/')
Q = next((a for a in sys.argv[1:] if a in ('ld', 'cel')), 'ambos')
SAI = Path(__file__).resolve().parent.parent.parent / '_ref/capturas'; SAI.mkdir(exist_ok=True)
ARG = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required']
def corre(g, nome, W):
    g.wait_for_timeout(3800)
    alt = g.evaluate('document.documentElement.scrollHeight'); vh = g.evaluate('innerHeight')
    fs = []; y = 0; i = 0
    while y < alt:
        g.evaluate(f'window.scrollTo({{top:{y},behavior:"instant"}})'); g.wait_for_timeout(1300)
        f = SAI / f'{nome}-{i:02d}.jpg'; g.screenshot(path=str(f), type='jpeg', quality=78); fs.append(f); y += vh - (90 if W > 700 else 60); i += 1
    return fs, alt
def folha(fs, nome, col):
    im = [Image.open(f) for f in fs]; w, h = im[0].size
    e = (1800 / col) / w
    w2, h2 = int(w * e), int(h * e)
    lin = (len(im) + col - 1) // col
    s = Image.new('RGB', (w2 * col + 6 * (col - 1), (h2 + 6) * lin), '#f0f')
    for i, x in enumerate(im): s.paste(x.resize((w2, h2)), ((i % col) * (w2 + 6), (i // col) * (h2 + 6)))
    s.save(SAI.parent / f'{nome}.jpg', quality=82); print(nome, s.size, len(im))
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=ARG)
    if Q in ('ld', 'ambos'):
        c = b.new_context(viewport={'width': 1440, 'height': 900}); g = c.new_page(); er = []
        g.on('pageerror', lambda e: er.append(str(e)[:200])); g.on('console', lambda m: er.append(m.text[:200]) if m.type == 'error' else None)
        g.goto(URL); fs, a = corre(g, 'ld', 1440); print('altura', a, er); folha(fs, 'cap-ld', 3); c.close()
    if Q in ('cel', 'ambos'):
        c = b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True, device_scale_factor=2); g = c.new_page(); er = []
        g.on('pageerror', lambda e: er.append(str(e)[:200])); g.on('console', lambda m: er.append(m.text[:200]) if m.type == 'error' else None)
        g.goto(URL); fs, a = corre(g, 'cel', 390); print('altura', a, er); folha(fs, 'cap-cel', 7); c.close()
