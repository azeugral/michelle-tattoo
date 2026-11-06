# -*- coding: utf-8 -*-
"""Favicon e capa de link."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import base64
S = Path(__file__).resolve().parent.parent
b64 = lambda f: base64.b64encode((S / f).read_bytes()).decode()
FONT = f"""@font-face{{font-family:S;src:url(data:font/woff2;base64,{b64('assets/fonts/script.woff2')})}}
@font-face{{font-family:G;src:url(data:font/woff2;base64,{b64('assets/fonts/gotica.woff2')})}}
@font-face{{font-family:C;src:url(data:font/woff2;base64,{b64('assets/fonts/corpo.woff2')})}}
*{{margin:0;box-sizing:border-box}}"""
FAV = f"""<style>{FONT}body{{width:256px;height:256px;background:linear-gradient(90deg,#f0eae0 50%,#0b0a0b 50%);display:grid;place-items:center;overflow:hidden}}
b{{font:400 214px/1 G;background:linear-gradient(90deg,#0b0a0b 50%,#f0eae0 50%);-webkit-background-clip:text;background-clip:text;color:transparent;padding:0 20px}}</style><b>M</b>"""
OG = f"""<style>{FONT}body{{width:1200px;height:630px;position:relative;overflow:hidden;background:#000}}img{{position:absolute;inset:0;width:1200px;height:630px;object-fit:cover}}
.n{{position:absolute;inset:6px 0 auto 0;text-align:center}}.n b{{display:inline-block;font:400 112px/1.1 G;padding:0 .14em;background:linear-gradient(90deg,#0b0a0b 50%,#f0eae0 50%);-webkit-background-clip:text;background-clip:text;color:transparent}}
.x{{position:absolute;bottom:34px;font:500 24px C}}.x1{{color:#0b0a0b;right:calc(50% + 150px)}}.x2{{color:#f0eae0;left:calc(50% + 150px)}}</style>
<img src="data:image/webp;base64,{b64('assets/img/hero-og.webp')}"><div class=n><b>Michelle</b></div><p class="x x1">Tatuadora</p><p class="x x2">Nova Resende, MG</p>"""
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge')
    g = b.new_page(viewport={'width': 256, 'height': 256}); g.set_content(FAV); g.wait_for_timeout(500); g.screenshot(path=str(S / 'assets/img/favicon.png'))
    g = b.new_page(viewport={'width': 1200, 'height': 630}); g.set_content(OG); g.wait_for_timeout(500); g.screenshot(path=str(S / 'assets/img/og.jpg'), type='jpeg', quality=88)
