# Michelle Tattoo

Prévia do site da Michelle (@michelle.tattoostudio), tatuadora em Nova Resende, MG.
Publicado em https://azeugral.github.io/michelle-tattoo/ com `noindex`.

## Conceito

Dois lados. As hashtags dela são `#tatuagemdark` e `#tatuagemdelicadas`, e a máscara partida por uma katana (post de 12/10) é a mesma ideia tatuada. O eixo da lâmina atravessa o site: papel à esquerda (delicado), preto à direita (dark).

- Nome inteiro em Manufacturing Consent (a gótica dos nomes dela), trocando de cor no eixo. `Delicado` em Mrs Saint Delafield (as frases finas dela). Corpo em Rethink Sans.
- Todo título da página atravessa o eixo: Delicado | Dark, Antes | Depois, Veja | de perto.
- Hero: tinta real da foto, positivo sobre papel e negativo sobre preto. Abre espelhada do centro (2,8 s) e segue em laço de 14 s. WebGL no computador, MP4 no celular em pé, shader de reserva no Modo de Pouca Energia, pôster se não houver WebGL.
- Portfólio: 10 peças de cada lado, foto real sem recorte em 3:4, só com o tom igualado. Abre com 6 + 6 no computador e 3 + 3 no celular; o resto fica em "Ver todos". A legenda aparece ao abrir a peça.
- Michelle: cartão pequeno no eixo, logo depois do portfólio, com a história de um lado e o orçamento do outro. O antes e depois usa o mesmo formato.
- Sem logo: o nome em gótica faz esse papel até ela ter uma.

## Editar

| O quê | Onde | Depois rodar |
| --- | --- | --- |
| Textos e seções | `tools/modelo.html` | `python tools/montar.py` |
| Peças, legendas e enquadramento | `tools/dados.py` | `python tools/processar.py <id>` e `montar.py` |
| Arte do hero | `tools/tinta_hero.py`, `tools/textura.py` | `python tools/gerar_video.py` |
| Posição da arte | `moldura()` em `assets/js/tinta.js` | `python tools/gerar_video.py` (o MP4 usa a mesma função) |
| Capa de link e favicon | `tools/marca.py` | `python tools/marca.py` |

Conferência: `python tools/auditar.py <url>` (13 tamanhos + 18 testes de uso), `python tools/fotos.py <url>`.

## CONFIRMAR com a cliente

1. **Endereço do estúdio**: não está em lugar nenhum; o site diz que é passado ao marcar o horário.
2. **Nome de contato**: o WhatsApp (35) 99716-2092 veio da bio. Confirmar se é o número de orçamento.
3. **Depoimentos**: os 4 são comentários reais dos posts, com o @. Pedir autorização, principalmente o da anestesia, que sugere uso de anestésico.
4. **Autorização das fotos**: o site mostra fotos de clientes e legendas sem nomes, mas os nomes tatuados aparecem nas imagens (Kelly, Luis, Daniel, Lucas, Diogo, João Miguel, Cecília e outros).
5. **Estilos**: "semi realismo" vem da legenda dela; "fine line" e "blackwork" foram deduzidos das fotos.
6. **Texto da reforma**: descreve a foto de antes e depois; conferir se o tribal foi mantido de propósito.
7. **Cidades vizinhas** citadas em Onde (Muzambinho, Monte Belo, Juruaia, Guaxupé): confirmar se atende esse público.
8. **Sinal, formas de pagamento, idade mínima e cuidados**: não foram publicados por falta de fonte.
9. **Peça de fora**: o post da marca no rosto ficou fora da grade; o anjo com rachaduras também (pele ainda vermelha, sem foto cicatrizada).

Site por L R G Z.
