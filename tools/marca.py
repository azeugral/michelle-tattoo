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
FAV = f"""<style>{FONT}body{{width:256px;height:256px;background:linear-gradient(90deg,#f0eae0 50%,#0b0a0b 50%);position:relative;overflow:hidden}}
b{{position:absolute;font-weight:400;line-height:1;top:50%}}.a{{font:128px/1 S;color:#0b0a0b;right:50%;transform:translate(-2px,-44%)}}.c{{font:136px/1 G;color:#f0eae0;left:50%;transform:translate(16px,-56%)}}</style><b class=a>M</b><b class=c>e</b>"""
OG = f"""<style>{FONT}body{{width:1200px;height:630px;position:relative;overflow:hidden;background:#000}}img{{position:absolute;inset:0;width:1200px;height:630px;object-fit:cover}}
p{{position:absolute;top:50%;line-height:1.1;white-space:nowrap}}.a{{font:104px S;color:#0b0a0b;right:calc(50% + 150px);transform:translateY(-52%)}}.c{{font:92px G;color:#f0eae0;left:calc(50% + 150px);transform:translateY(-52%)}}
.x{{font:500 22px C;top:auto;bottom:34px}}.x1{{color:#0b0a0b;right:calc(50% + 150px)}}.x2{{color:#f0eae0;left:calc(50% + 150px)}}</style>
<img src="data:image/webp;base64,{b64('assets/img/hero-og.webp')}"><p class=a>Mich</p><p class=c>elle</p><p class="x x1">Tatuadora</p><p class="x x2">Nova Resende, MG</p>"""
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge')
    g = b.new_page(viewport={'width': 256, 'height': 256}); g.set_content(FAV); g.wait_for_timeout(500); g.screenshot(path=str(S / 'assets/img/favicon.png'))
    g = b.new_page(viewport={'width': 1200, 'height': 630}); g.set_content(OG); g.wait_for_timeout(500); g.screenshot(path=str(S / 'assets/img/og.jpg'), type='jpeg', quality=88)
