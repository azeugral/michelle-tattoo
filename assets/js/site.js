(function () {
  'use strict';
  var d = document, raiz = d.documentElement;
  raiz.classList.add('js');
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };
  var ZAP = '5535997162092';
  var calmo = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var toque = matchMedia('(hover: none) and (pointer: coarse)').matches;

  /* tudo pronto de cara: nada de carregar imagem so ao rolar */
  addEventListener('load', function () { $$('img[loading=lazy]').forEach(function (i) { i.loading = 'eager'; }); });

  /* ---------- hero ---------- */
  var fundo = $('#heroFundo'), hero = $('.hero');
  var motor = null, canvas = null, video = null, rodando = false, t0 = 0, usandoVideo = false;
  var VW = 1080, VH = 1920;      // formato do MP4 em pe

  function montarVert() {
    var vert = hero.clientWidth / hero.clientHeight < .82;
    raiz.classList.toggle('vert', vert);
    /* em pe, o titulo fica num bloco proprio acima da mascara */
    $$('.hero-lado').forEach(function (l) {
      var cab = $('.hero-cab', l);
      if (!cab) {
        cab = d.createElement('div'); cab.className = 'hero-cab';
        cab.appendChild($('.chapeu', l)); cab.appendChild($('.nome', l));
        l.insertBefore(cab, l.firstChild);
      }
    });
    var W = hero.clientWidth, H = hero.clientHeight, m;
    if (usandoVideo) {
      var e = Math.max(W / VW, H / VH), ref = tintaMoldura(VW, VH);
      m = { top: (H - VH * e) / 2 + ref.top * e, h: ref.h * e, w: ref.w * e };
    } else m = tintaMoldura(W, H);
    hero.style.setProperty('--art-topo', Math.round(m.top) + 'px');
    hero.style.setProperty('--art-h', Math.round(m.h) + 'px');
    hero.style.setProperty('--art-w', Math.round(m.w) + 'px');
  }

  function dpr() { return Math.min(devicePixelRatio || 1, toque ? 1.5 : 2); }

  function quadro(ag) {
    if (!rodando) return;
    var s = (ag - t0) / 1000;
    motor.desenha(s < 2.8 ? 0 : (s - 2.8) % 14, tintaAbre(s), hero.clientWidth, hero.clientHeight, dpr());
    requestAnimationFrame(quadro);
  }
  function ligar() {
    if (rodando || !motor || d.hidden) return;
    rodando = true;
    if (!t0) t0 = performance.now();
    requestAnimationFrame(quadro);
  }
  function carregar(src) {
    return new Promise(function (ok, nao) { var i = new Image(); i.onload = function () { (i.decode ? i.decode() : Promise.resolve()).then(function () { ok(i); }, function () { ok(i); }); }; i.onerror = nao; i.src = src; });
  }
  function poster() {
    var p = $('#heroPoster'), vert = hero.clientWidth / hero.clientHeight < .82;
    p.src = 'assets/img/hero-' + (vert ? 'pe' : 'deitado') + '.webp'; p.hidden = false;
  }
  function comShader(depois) {
    canvas = d.createElement('canvas');
    fundo.insertBefore(canvas, fundo.firstChild);
    try { motor = tintaHero(canvas); } catch (e) { motor = null; }
    if (!motor) { canvas.remove(); poster(); return; }
    Promise.all([carregar('assets/img/hero/tom.webp'), carregar('assets/img/hero/verm.webp')]).then(function (t) {
      motor.textura(0, t[0]); motor.textura(1, t[1]);
      if (depois) depois();
      else if (calmo) motor.desenha(4, 1, hero.clientWidth, hero.clientHeight, dpr());
      else ligar();
    }, poster);
  }
  function comVideo() {
    usandoVideo = true; montarVert();
    var abre = d.createElement('video'), laco = d.createElement('video');
    [abre, laco].forEach(function (v) {
      v.muted = true; v.defaultMuted = true; v.playsInline = true; v.setAttribute('playsinline', ''); v.setAttribute('muted', ''); v.preload = 'auto'; v.setAttribute('aria-hidden', 'true'); v.disablePictureInPicture = true;
    });
    abre.src = 'assets/video/hero-abertura.mp4'; laco.src = 'assets/video/hero-laco.mp4'; laco.loop = true; laco.style.visibility = 'hidden';
    fundo.insertBefore(laco, fundo.firstChild); fundo.insertBefore(abre, fundo.firstChild);
    video = laco;
    laco.load();
    abre.addEventListener('ended', function () {
      laco.style.visibility = 'visible';
      var r = laco.play(); if (r && r.catch) r.catch(function () {});
      abre.remove();
    });
    var caiu = false;
    function plano() {
      /* Modo de Pouca Energia ou arquivo que nao abriu: roda o mesmo hero no shader */
      if (caiu) return; caiu = true;
      abre.remove(); laco.remove(); usandoVideo = false; montarVert(); comShader();
    }
    abre.addEventListener('error', plano);
    var r = abre.play();
    if (r && r.catch) r.catch(plano);
  }
  montarVert();
  var eVert = hero.clientWidth / hero.clientHeight < .82;
  if (calmo) { if (toque) poster(); else comShader(); }
  else if (toque && hero.clientWidth / hero.clientHeight < .64) comVideo();
  else comShader();

  var rz; addEventListener('resize', function () { clearTimeout(rz); rz = setTimeout(montarVert, 120); });
  d.addEventListener('visibilitychange', function () { if (d.hidden) rodando = false; else if (!calmo) ligar(); });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (e) {
      if (!motor || calmo) return;
      if (e[0].isIntersecting) ligar(); else rodando = false;
    }).observe(hero);
  }

  /* ---------- menu ---------- */
  var menu = $('#menu'), btMenu = $('#btMenu');
  function abreMenu(s) {
    menu.hidden = !s; btMenu.setAttribute('aria-expanded', String(s)); btMenu.textContent = s ? 'Fechar' : 'Menu';
    d.body.style.overflow = s ? 'hidden' : '';
  }
  btMenu.addEventListener('click', function () { abreMenu(menu.hidden); });
  $$('a', menu).forEach(function (a) { a.addEventListener('click', function () { abreMenu(false); }); });
  $('.topo .bt-orc').addEventListener('click', function () { abreMenu(false); });

  /* ---------- revelar do eixo para fora ---------- */
  var alvos = $$('.peca-q, .reel video, .sobre-foto img');
  alvos.forEach(function (a) { a.parentNode.classList.add('revela-p'); });
  if (!calmo && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.remove('fora'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -6% 0px' });
    $$('.peca, .reel').forEach(function (p) { p.classList.add('revela', 'fora'); });
    /* observa o pai para o recorte nao esconder o alvo do observador */
    $$('.peca, .reel').forEach(function (p) {
      var sent = d.createElement('i'); sent.style.cssText = 'display:block;height:1px;margin-bottom:-1px';
      p.parentNode.insertBefore(sent, p);
      var o = new IntersectionObserver(function (es) {
        if (es[0].isIntersecting) { p.classList.remove('fora'); o.disconnect(); sent.remove(); }
      }, { rootMargin: '0px 0px -4% 0px' });
      o.observe(sent);
    });
    setTimeout(function () { $$('.revela.fora').forEach(function (p) { if (p.getBoundingClientRect().top < innerHeight) p.classList.remove('fora'); }); }, 900);
  }

  /* ---------- ver mais no celular ---------- */
  var LIM = 4;
  var verMais = $('#verMais'), abertos = false;
  function limita() {
    var cel = matchMedia('(max-width:640px)').matches;
    $$('.col').forEach(function (c) {
      if (!c.closest('#grade')) return;
      $$('.peca', c).forEach(function (p, i) { p.hidden = cel && !abertos && i >= LIM; });
    });
    /* o sentinela do revelar pode ter sido criado antes: nada fica escondido por ele */
    if (abertos) $$('#grade .revela.fora').forEach(function (p) { p.classList.remove('fora'); });
  }
  limita();
  addEventListener('resize', limita);
  verMais.addEventListener('click', function () {
    abertos = !abertos; verMais.textContent = abertos ? 'Ver menos' : 'Ver todos os trabalhos'; limita();
    if (!abertos) $('#grade').scrollIntoView({ block: 'start' });
  });

  /* ---------- galeria ---------- */
  var lb = $('#lb'), palco = $('#lbPalco'), leg = $('#lbLeg'), vistas = $('#lbVistas'), atual = 0, vista = 0, voltar = null;
  var P = window.PECAS || [];
  function mostra() {
    var p = P[atual], itens = p.fotos.slice();
    if (p.video) itens.push({ video: p.video });
    vista = Math.min(vista, itens.length - 1);
    palco.textContent = '';
    var it = itens[vista];
    if (it.video) {
      var v = d.createElement('video'); v.src = it.video; v.muted = true; v.loop = true; v.autoplay = true; v.playsInline = true; v.setAttribute('playsinline', ''); v.controls = false; palco.appendChild(v);
      var r = v.play(); if (r && r.catch) r.catch(function () {});
    } else {
      var i = d.createElement('img'); i.src = it; i.alt = p.leg; i.draggable = false; palco.appendChild(i);
    }
    leg.textContent = p.leg;
    vistas.textContent = '';
    if (itens.length > 1) itens.forEach(function (x, n) {
      var b = d.createElement('button'); b.type = 'button'; b.textContent = n + 1; b.setAttribute('aria-pressed', String(n === vista)); b.setAttribute('aria-label', 'Vista ' + (n + 1));
      b.addEventListener('click', function () { vista = n; mostra(); });
      vistas.appendChild(b);
    });
  }
  function abre(id, el) {
    atual = Math.max(0, P.findIndex(function (p) { return p.id === id; })); vista = 0; voltar = el;
    lb.hidden = false; d.body.style.overflow = 'hidden'; mostra(); $('#lbX').focus();
  }
  function fecha() {
    lb.hidden = true; palco.textContent = ''; d.body.style.overflow = '';
    if (voltar) voltar.focus({ preventScroll: true });
  }
  function passa(n) { atual = (atual + n + P.length) % P.length; vista = 0; mostra(); }
  $$('.peca').forEach(function (b) { b.addEventListener('click', function () { abre(b.dataset.id, b); }); });
  $('#lbX').addEventListener('click', fecha);
  $('#lbAnt').addEventListener('click', function () { passa(-1); });
  $('#lbProx').addEventListener('click', function () { passa(1); });
  d.addEventListener('keydown', function (e) {
    if (lb.hidden) { if (e.key === 'Escape' && !menu.hidden) abreMenu(false); return; }
    if (e.key === 'Escape') fecha();
    if (e.key === 'ArrowRight') passa(1);
    if (e.key === 'ArrowLeft') passa(-1);
  });
  var x0 = null;
  palco.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  palco.addEventListener('touchend', function (e) {
    if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 48) passa(dx < 0 ? 1 : -1);
  });
  $('#lbQuero').addEventListener('click', function () {
    var p = P[atual];
    marcaLado(p.lado === 'e' ? 'Delicado' : 'Dark');
    $('#fIdeia').value = 'Quero uma parecida com "' + p.leg + '".';
    fecha();
    $('#orcamento').scrollIntoView({ block: 'start', behavior: calmo ? 'auto' : 'smooth' });
  });

  /* ---------- antes e depois ---------- */
  var comp = $('#comp'), compR = $('#compR');
  compR.addEventListener('input', function () { comp.style.setProperty('--p', compR.value + '%'); });

  /* ---------- videos so tocam na tela ---------- */
  var vids = $$('.reel video');
  if ('IntersectionObserver' in window) {
    var ov = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) {
          if (!v.src) { v.src = v.dataset.src; }
          if (!calmo) { var r = v.play(); if (r && r.catch) r.catch(function () {}); }
        } else v.pause();
      });
    }, { threshold: .25 });
    vids.forEach(function (v) { ov.observe(v); });
  }

  /* ---------- orcamento ---------- */
  var ladoSel = '', botoes = $$('#fLado button');
  function marcaLado(n) {
    ladoSel = n;
    botoes.forEach(function (b) { b.setAttribute('aria-pressed', String(b.textContent === n)); });
  }
  botoes.forEach(function (b) { b.addEventListener('click', function () { marcaLado(b.textContent === ladoSel ? '' : b.textContent); }); });
  $$('a[data-lado]').forEach(function (a) { a.addEventListener('click', function () { marcaLado(a.dataset.lado); }); });
  var campoNome = $('#fNome'), erro = $('#fErro');
  campoNome.addEventListener('input', function () { erro.hidden = true; });
  $('#form').addEventListener('submit', function (e) {
    e.preventDefault();
    var nome = campoNome.value.trim();
    if (!nome) { erro.hidden = false; campoNome.focus(); return; }
    var L = ['Oi, Michelle! Vim pelo seu site e quero um orçamento.', '', 'Nome: ' + nome];
    if (ladoSel) L.push('Estilo: ' + ladoSel);
    var i = $('#fIdeia').value.trim(), l = $('#fLugar').value.trim(), t = $('#fTam').value.trim();
    if (i) L.push('Ideia: ' + i);
    if (l) L.push('Lugar do corpo: ' + l);
    if (t) L.push('Tamanho: ' + t);
    window.open('https://wa.me/' + ZAP + '?text=' + encodeURIComponent(L.join('\n')), '_blank', 'noopener');
  });
})();
