# -*- coding: utf-8 -*-
"""Grava o hero do celular: abertura (2,8 s) + laco (14 s fechado) em 1080x1920 a 60 fps, e os posteres. Uso: python tools/gerar_video.py [abertura laco poster]"""
import base64, subprocess, shutil, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import io
S = Path(__file__).resolve().parent.parent
ff = shutil.which('ffmpeg'); FPS = 60
Q = sys.argv[1:] or ['poster', 'abertura', 'laco']
b64 = lambda f: 'data:image/webp;base64,' + base64.b64encode((S / f).read_bytes()).decode()

with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    g = b.new_page(viewport={'width': 400, 'height': 400})
    g.set_content('<body style="margin:0"><canvas id=c></canvas></body>')
    g.add_script_tag(content=(S / 'assets/js/tinta.js').read_text(encoding='utf8'))
    g.evaluate("""async(a)=>{window.T=tintaHero(document.getElementById('c'),{guardar:true});
      for(const i of [0,1]){const m=new Image();m.src=a[i];await m.decode();T.textura(i,m)}}""", [b64('assets/img/hero/tom.webp'), b64('assets/img/hero/verm.webp')])
    def foto(t, f, W, H, q=.97):
        d = g.evaluate(f"(T.desenha({t},{f},{W},{H},1),document.getElementById('c').toDataURL('image/jpeg',{q}))")
        return base64.b64decode(d.split(',', 1)[1])
    if 'poster' in Q:
        for n, W, H in (('pe', 1080, 1920), ('deitado', 1920, 1080)):
            Image.open(io.BytesIO(foto(4, 1, W, H))).save(S / f'assets/img/hero-{n}.webp', quality=86, method=6)
            print('poster', n, flush=True)
    def grava(nome, n, fn):
        mp4 = S / f'assets/video/hero-{nome}.mp4'
        enc = subprocess.Popen([ff, '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                                '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-color_range', 'tv', '-r', str(FPS), '-movflags', '+faststart', '-an', str(mp4)], stdin=subprocess.PIPE)
        for i in range(n):
            t, f = fn(i)
            enc.stdin.write(foto(t, f, 1080, 1920))
            if i % 120 == 0: print(nome, i, n, flush=True)
        enc.stdin.close(); enc.wait()
        print(mp4.name, round(mp4.stat().st_size / 1e6, 2), 'MB', flush=True)
    def abre(s): return min(1, 1 - (1 - min(s / 2.8, 1)) ** 2.6)
    if 'abertura' in Q: grava('abertura', int(2.8 * FPS), lambda i: (0, abre(i / FPS)))
    if 'laco' in Q: grava('laco', 14 * FPS, lambda i: (i / FPS, 1))
    b.close()
