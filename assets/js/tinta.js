/* Hero: a mascara partida da Michelle. A tinta abre do centro para os dois lados ao mesmo tempo (borrao espelhado),
   preto sobre papel a esquerda, negativo sobre preto a direita. Ciclo de 14 s fechado, para o MP4 emendar. */
(function (raiz) {
  var VS = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var FS = [
    'precision highp float;',
    'uniform vec2 uR;uniform vec2 uA;uniform float uT,uF;uniform sampler2D uTom,uVer;',
    'const vec3 PAPEL=vec3(.941,.918,.878);const vec3 PRETO=vec3(.043,.039,.043);const vec3 RUB=vec3(.84,.13,.15);',
    'const float PI=3.14159265;',
    'float h(vec2 p){p=fract(p*vec2(123.34,456.21));p+=dot(p,p+45.32);return fract(p.x*p.y);}',
    'float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}',
    'float fbm(vec2 p){float v=0.,a=.5;mat2 m=mat2(.8,.6,-.6,.8);for(int i=0;i<5;i++){v+=a*n(p);p=m*p*2.03+7.1;a*=.5;}return v;}',
    'void main(){',
    ' vec2 px=vec2(gl_FragCoord.x,uR.y-gl_FragCoord.y);',
    ' float ax=uR.x*.5;float dx=px.x-ax;float lado=step(0.,dx);',
    ' float aa=clamp(dx+.5,0.,1.);',
    ' vec2 q=vec2(abs(dx),px.y-(uA.x+uA.y*.44))/uA.y;',
    ' float fase=uT*2.*PI/14.;vec2 gira=vec2(cos(fase),sin(fase))*.34;',
    ' float cr=fbm(q*2.1+gira);float c2=fbm(q*3.6+vec2(cr*1.6,-cr)+gira*.6);',
    ' float dist=length(q*vec2(.95,.72));',
    ' float mancha=smoothstep(.50,.78,c2)*smoothstep(.98,.14,dist);',
    ' float d=length(q);',
    ' float borda=fbm(q*5.)*.20;',
    ' float raio=uF*1.06;',
    ' float rev=1.-smoothstep(raio-.05,raio+.015,d+borda-.05);',
    ' float frente=smoothstep(raio-.09,raio-.01,d+borda-.05)*rev*step(.002,uF)*(1.-smoothstep(.72,1.,uF));',
    ' float largo=uA.y*.37383;',
    ' vec2 uv=vec2((dx+largo*.5)/largo,(px.y-uA.x)/uA.y);',
    ' float tom=0.,ver=0.;',
    ' if(uv.x>0.&&uv.x<1.&&uv.y>0.&&uv.y<1.){tom=texture2D(uTom,uv).r;ver=texture2D(uVer,uv).r;}',
    ' float topo=smoothstep(.0,.085,uv.y+(fbm(vec2(uv.x*6.,3.))-.5)*.06);',
    ' tom*=topo*rev;ver*=topo*rev;',
    ' float ondaLuz=exp(-pow((uv.y-fract(uT/14.)*1.5+.25)/.05,2.));',
    ' float lamina=smoothstep(.10,.03,abs(uv.x-.5))*ondaLuz;',
    ' vec3 fe=mix(PAPEL,PRETO,mancha*.022*uF);',
    ' vec3 fd=mix(PRETO,PAPEL,mancha*.075*uF);',
    ' fe=mix(fe,PRETO,frente*.07);fd=mix(fd,PAPEL,frente*.09);',
    ' vec3 ce=mix(fe,PRETO,tom);vec3 cd=mix(fd,PAPEL,tom*(1.+lamina*.5));',
    ' float pulso=.86+.14*sin(fase*2.);',
    ' vec3 rub=RUB*(1.08*pulso+.08);',
    ' ce=mix(ce,RUB,ver);cd=mix(cd,rub,ver);',
    ' cd+=RUB*ver*.18*pulso;',
    ' vec3 cor=mix(ce,cd,aa);',
    ' gl_FragColor=vec4(cor,1.);',
    '}'].join('\n');

  function moldura(W, H) {
    var A = 800 / 2140;
    var h, t;
    if (W / H < .82) {
      h = H * .655; t = H * .235;
      if (h * A > W * .62) { h = W * .62 / A; t = H * .235 + (H * .655 - h) / 2; }
    } else { h = H * 1.06; t = -H * .06; }
    return { top: t, h: h, w: h * A };
  }

  function tintaHero(cv, op) {
    op = op || {};
    var gl = cv.getContext('webgl', { antialias: false, alpha: false, preserveDrawingBuffer: !!op.guardar, powerPreference: 'high-performance' });
    if (!gl) return null;
    function sh(t, s) {
      var o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o);
      if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o));
      return o;
    }
    var pr = gl.createProgram();
    gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS));
    gl.linkProgram(pr); gl.useProgram(pr);
    var b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    var a = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(a); gl.vertexAttribPointer(a, 2, gl.FLOAT, false, 0, 0);
    var U = {};
    ['uR', 'uA', 'uT', 'uF', 'uTom', 'uVer'].forEach(function (n) { U[n] = gl.getUniformLocation(pr, n); });
    gl.uniform1i(U.uTom, 0); gl.uniform1i(U.uVer, 1);
    function tex(un, im) {
      gl.activeTexture(gl.TEXTURE0 + un);
      var t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.LUMINANCE, gl.LUMINANCE, gl.UNSIGNED_BYTE, im);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    }
    return {
      textura: tex,
      /* t = segundos do ciclo, f = abertura da tinta 0..1; W e H em CSS */
      desenha: function (t, f, W, H, dpr) {
        var w = Math.round(W * dpr), h = Math.round(H * dpr);
        if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; gl.viewport(0, 0, w, h); }
        var m = moldura(W, H);
        gl.uniform2f(U.uR, w, h); gl.uniform2f(U.uA, m.top * dpr, m.h * dpr);
        gl.uniform1f(U.uT, t); gl.uniform1f(U.uF, f);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
      }
    };
  }
  raiz.tintaHero = tintaHero;
  raiz.tintaMoldura = moldura;
  /* abertura: rapida no comeco, assenta no fim */
  raiz.tintaAbre = function (s) { var x = Math.min(s / 2.8, 1); return 1 - Math.pow(1 - x, 2.6); };
})(this);
