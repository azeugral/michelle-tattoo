# -*- coding: utf-8 -*-
"""Auditoria: estouro, corte de texto e de fonte, simetria no eixo, grades e erros, em 13 tamanhos, + teste funcional.
Uso: python tools/auditar.py [url]"""
import sys
from pathlib import Path
from urllib.parse import unquote
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf8')
URL = next((a for a in sys.argv[1:] if a.startswith('http')), 'http://localhost:8899/')
VPS = [(320, 568, 1), (360, 640, 1), (360, 740, 1), (390, 844, 1), (430, 932, 1), (600, 900, 1), (768, 1024, 1), (844, 390, 1), (1024, 768, 0), (1280, 720, 0), (1440, 900, 0), (1920, 1080, 0), (2560, 1300, 0)]
ARG = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required']
JS = r"""
() => {
  const W = document.documentElement.clientWidth, H = innerHeight, out = [];
  if (document.documentElement.scrollWidth > W) out.push('ESTOURO pagina ' + document.documentElement.scrollWidth + '>' + W);
  document.querySelectorAll('h2,h3,p,a,button,span,small,blockquote,cite,li,label,legend,figcaption').forEach(el => {
    if (el.closest('[hidden],.sr,.saltar,.menu,.lb')) return;
    const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') return;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) return;
    const nome = el.tagName + '.' + el.className + ' "' + (el.textContent || '').trim().slice(0, 26) + '"';
    if (r.right > W + 1 || r.left < -1) out.push('FORA ' + nome + ' ' + Math.round(r.left) + '-' + Math.round(r.right));
    if (el.scrollWidth > el.clientWidth + 1 && cs.display !== 'inline' && el.clientWidth > 0) out.push('CORTE-X ' + nome + ' ' + el.scrollWidth + '>' + el.clientWidth);
  });
  // titulos em dois lados: cada metade nao pode cruzar o eixo
  const eixo = W / 2;
  document.querySelectorAll('.tit .s').forEach(e => { const g = medeTexto(e); if (g.right > eixo + .5) out.push('EIXO esq "' + e.textContent + '" ' + (g.right - eixo).toFixed(1)); if (g.left < 0) out.push('BORDA esq "' + e.textContent + '" ' + g.left.toFixed(1)); });
  document.querySelectorAll('.tit .g').forEach(e => { const g = medeTexto(e); if (g.left < eixo - .5) out.push('EIXO dir "' + e.textContent + '"'); if (g.right > W) out.push('BORDA dir "' + e.textContent + '" ' + (g.right - W).toFixed(1)); });
  function medeTexto(e) { const r = document.createRange(); r.selectNodeContents(e); const b = r.getBoundingClientRect(); return b; }
  // colunas espelhadas
  const ce = [...document.querySelectorAll('#grade .col-e .peca:not([hidden])')], cd = [...document.querySelectorAll('#grade .col-d .peca:not([hidden])')];
  if (ce.length !== cd.length) out.push('PARES ' + ce.length + ' x ' + cd.length);
  ce.forEach((a, i) => { const b = cd[i]; if (!b) return; const ra = a.querySelector('.peca-q').getBoundingClientRect(), rb = b.querySelector('.peca-q').getBoundingClientRect();
    if (Math.abs(ra.width - rb.width) > 1 || Math.abs(ra.height - rb.height) > 1 || Math.abs(ra.top - rb.top) > 1) out.push('SIMETRIA peca ' + i);
    });
  // hero cabe na tela
  const h = document.querySelector('.hero').getBoundingClientRect(), bts = [...document.querySelectorAll('.hero-lado .bt')].map(b => b.getBoundingClientRect());
  bts.forEach(b => { if (b.bottom > h.bottom - 2) out.push('HERO botao cortado'); });
  if (Math.abs(bts[0].top - bts[1].top) > 1 || Math.abs(bts[0].width - bts[1].width) > 1) out.push('HERO botoes desiguais ' + bts.map(b => Math.round(b.top) + '/' + Math.round(b.width)));
  const nm = document.querySelector('.hero-nome').getBoundingClientRect(), sb = document.querySelector('.hero-sub').getBoundingClientRect();
  const barra = document.querySelector('.topo').getBoundingClientRect().bottom;
  if (Math.abs((nm.left + nm.right) / 2 - W / 2) > 1) out.push('HERO nome fora do eixo');
  if (nm.left < 0 || nm.right > W) out.push('HERO nome cortado ' + Math.round(nm.left) + '-' + Math.round(nm.right));
  if (nm.top < barra - 1) out.push('HERO nome sob a barra');
  const ar = parseFloat(getComputedStyle(document.querySelector('.hero')).getPropertyValue('--art-topo'));
  if (sb.bottom > ar + 30) out.push('HERO titulo sobre a arte ' + Math.round(sb.bottom) + ' > ' + ar);
  const tx = [...document.querySelectorAll('.hero-txt')].map(e => e.getBoundingClientRect());
  if (Math.abs(tx[0].top - tx[1].top) > 12) out.push('HERO textos desalinhados');
  const ca = document.querySelector('.carta').getBoundingClientRect();
  if (Math.abs((ca.left + ca.right) / 2 - W / 2) > 1.5) out.push('CARTA fora do eixo');
  return [...new Set(out)];
}
"""
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=ARG)
    tot = 0
    for w, h, tq in VPS:
        c = b.new_context(viewport={'width': w, 'height': h}, has_touch=bool(tq), is_mobile=bool(tq), device_scale_factor=1)
        g = c.new_page(); er = []
        g.on('pageerror', lambda e: er.append('JS ' + str(e)[:200]))
        g.on('console', lambda m: er.append('CON ' + m.text[:160]) if m.type == 'error' else None)
        g.on('response', lambda r: er.append(f'{r.status} ' + r.url[-50:]) if r.status >= 400 else None)
        g.goto(URL, wait_until='load'); g.wait_for_timeout(1400)
        o = g.evaluate(JS) + er
        print(f'{w}x{h}', 'ok' if not o else '')
        for x in o: print('   ', x)
        tot += len(o); c.close()
    print('TOTAL auditoria', tot)
    # funcional
    R = []
    def ok(n, v, x=''):
        R.append(bool(v)); print('OK ' if v else 'FALHOU', n, x)
    c = b.new_context(viewport={'width': 1440, 'height': 900}); g = c.new_page()
    g.goto(URL); g.wait_for_timeout(1500)
    ok('canvas do hero', g.evaluate("!!document.querySelector('#heroFundo canvas')"))
    ok('6 + 6 de cara', g.evaluate("[...document.querySelectorAll('.peca')].filter(p=>!p.hidden).length") == 12)
    g.evaluate("document.querySelector('.peca[data-id=hannya]').scrollIntoView({block:'center',behavior:'instant'})"); g.wait_for_timeout(600)
    g.click('.peca[data-id=hannya]'); g.wait_for_timeout(500)
    ok('lightbox abre', not g.evaluate("document.querySelector('#lb').hidden"))
    ok('lightbox foto', g.evaluate("(()=>{const i=document.querySelector('#lbPalco img');return i&&i.complete&&i.naturalWidth>0})()"))
    ok('vistas', g.evaluate("document.querySelectorAll('#lbVistas button').length") == 3)
    g.click('#lbVistas button:nth-child(3)'); g.wait_for_timeout(500)
    ok('vista em video', g.evaluate("!!document.querySelector('#lbPalco video')"))
    g.keyboard.press('ArrowRight'); g.wait_for_timeout(300)
    ok('seta teclado', g.evaluate("document.querySelector('#lbLeg').textContent") == 'Gueixa e hannya')
    g.click('#lbQuero'); g.wait_for_timeout(1400)
    ok('quero uma assim', 'Gueixa' in g.input_value('#fIdeia') and g.evaluate("document.querySelector('#lb').hidden"))
    ok('lado marcado', g.evaluate("document.querySelector('#fLado [aria-pressed=true]').textContent") == 'Dark')
    g.evaluate("document.querySelector('#form button[type=submit]').scrollIntoView({block:'center',behavior:'instant'})"); g.wait_for_timeout(300)
    g.click('#form button[type=submit]'); g.wait_for_timeout(200)
    ok('erro sem nome', not g.evaluate("document.querySelector('#fErro').hidden"))
    g.fill('#fNome', 'Teste'); g.fill('#fLugar', 'Coxa'); g.fill('#fTam', '20 cm')
    with c.expect_page() as pop: g.click('#form button[type=submit]')
    u = unquote(pop.value.url); pop.value.close()
    ok('whatsapp', '5535997162092' in u and 'Coxa' in u and 'Gueixa' in u, u[:90])
    g.evaluate("document.querySelector('#comp').scrollIntoView({block:'center',behavior:'instant'})"); g.wait_for_timeout(300)
    bx = g.locator('#comp').bounding_box()
    g.mouse.click(bx['x'] + bx['width'] * .8, bx['y'] + 100); g.wait_for_timeout(150)
    ok('comparador', g.evaluate("parseInt(document.querySelector('#comp').style.getPropertyValue('--p'))") > 70)
    g.click('#reforma .bt-sobre'); g.wait_for_timeout(1000)
    ok('reforma marca lado', g.evaluate("document.querySelector('#fLado [aria-pressed=true]').textContent") == 'Reforma')
    g.evaluate("document.querySelector('#perto').scrollIntoView({block:'center',behavior:'instant'})"); g.wait_for_timeout(1500)
    ok('reels tocam', g.evaluate("[...document.querySelectorAll('.reel video')].filter(v=>!v.paused).length") >= 2)
    c.close()
    # celular
    c = b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True); g = c.new_page()
    g.goto(URL); g.wait_for_timeout(2000)
    ok('video no celular', g.evaluate("!!document.querySelector('#heroFundo video')"))
    g.wait_for_timeout(2800)
    ok('laco assume', g.evaluate("(()=>{const v=document.querySelectorAll('#heroFundo video');return v.length==1&&!v[0].paused&&v[0].loop})()"))
    n0 = g.evaluate("[...document.querySelectorAll('.peca')].filter(p=>!p.hidden).length")
    g.evaluate("document.querySelector('#verMais').scrollIntoView({block:'center',behavior:'instant'})"); g.wait_for_timeout(200); g.tap('#verMais'); g.wait_for_timeout(300)
    n1 = g.evaluate("[...document.querySelectorAll('.peca')].filter(p=>!p.hidden).length")
    ok('ver todos', n0 == 6 and n1 == 20, f'{n0}->{n1}')
    g.evaluate("window.scrollTo({top:0,behavior:'instant'})"); g.tap('#btMenu'); g.wait_for_timeout(200)
    ok('menu abre', not g.evaluate("document.querySelector('#menu').hidden"))
    g.tap('.menu-l a[href="#sobre"]'); g.wait_for_timeout(1000)
    ok('menu fecha e rola', g.evaluate("document.querySelector('#menu').hidden && scrollY>500"))
    print('FUNCIONAL', sum(R), '/', len(R))
    b.close()
