"""Gera index.html (pt) e en/index.html a partir de _src/molde.html e
_src/textos/<lang>.json.   python3 _src/gerar.py

Para um idioma novo: criar textos/<lang>.json com as mesmas chaves e
acrescentar o idioma em IDIOMAS (e em idioma.js).
"""
import json
import pathlib
import re

SRC = pathlib.Path(__file__).parent
RAIZ = SRC.parent
URL = "https://eduardo7321.github.io/"
# codigo: (pasta de saida, rotulo do botao)
IDIOMAS = {"pt": ("", "PT"), "en": ("en/", "EN")}
VIDEO_LABEL = {"pt": "Vídeo do Órbita, 1 minuto e 18 segundos", "en": "Orbita video, 52 seconds"}
FOTONS_LABEL = {"pt": "Vídeo do Laboratório de Fótons, 1 minuto e 32 segundos",
                "en": "Photon Lab video, 1 minute and 30 seconds"}
HARPA_LABEL = {"pt": "Vídeo da Harpa Cristã, 1 minuto e 25 segundos",
               "en": "Harpa Cristã video, 1 minute and 29 seconds"}

# Pix copia e cola para doacoes (chave aleatoria, sem valor fixo), gerado no app do banco.
# O QR Code em img/pix-qr.svg sai dele:  <python com segno> _src/pix_qr.py
PIX = ("00020126580014BR.GOV.BCB.PIX0136950848b4-74f0-4576-874c-00e5540de66c5204000053039865802BR"
       "5918Eduardo Jose Silva6009SAO PAULO62140510HFjoMgWAHW630484E2")


def crc_pix(dados):
    """CRC16-CCITT (0xFFFF) do padrao EMV do Pix: os 4 ultimos digitos do codigo."""
    c = 0xFFFF
    for b in dados.encode():
        c ^= b << 8
        for _ in range(8):
            c = ((c << 1) ^ 0x1021) & 0xFFFF if c & 0x8000 else (c << 1) & 0xFFFF
    return "%04X" % c


def _apoio(lang, raiz):
    """Secao de doacao. So em portugues por enquanto (Pix); o ingles ganha Ko-fi depois."""
    if lang != "pt":
        return ""
    return f"""<section class="wrap apoio" id="apoie" aria-labelledby="t-apoio">
    <div class="apoio-box">
      <div>
        <h2 id="t-apoio">Apoie o Iluminar Apps</h2>
        <p>Os apps são gratuitos e vão continuar assim. Se eles ajudam você, seus alunos ou sua igreja, um Pix de qualquer valor ajuda a fazer os próximos.</p>
        <p class="apoio-nota">Aponte a câmera do app do banco para o QR Code ou copie o código e use o Pix copia e cola. O Pix vai para Eduardo Jose Silva, o desenvolvedor.</p>
      </div>
      <div class="pix">
        <img src="{raiz}img/pix-qr.svg" alt="QR Code do Pix para apoiar o Iluminar Apps" width="200" height="200">
        <label for="pix-codigo">Pix copia e cola</label>
        <input id="pix-codigo" type="text" readonly value="{PIX}">
        <button type="button" class="btn btn-gold" id="pix-copiar">Copiar código Pix</button>
        <p class="pix-ok" id="pix-ok" role="status" aria-live="polite"></p>
      </div>
    </div>
  </section>
  <script>
  document.getElementById('pix-copiar').addEventListener('click', function () {{
    var campo = document.getElementById('pix-codigo');
    var ok = document.getElementById('pix-ok');
    function feito() {{ ok.textContent = 'Código copiado. Agora é só colar no app do banco.'; }}
    if (navigator.clipboard && window.isSecureContext) {{
      navigator.clipboard.writeText(campo.value).then(feito, function () {{ campo.select(); document.execCommand('copy'); feito(); }});
    }} else {{ campo.select(); document.execCommand('copy'); feito(); }}
  }});
  </script>"""


def _video(raiz, poster, mp4, rotulo):
    return (f'<video class="feature" controls preload="none" playsinline width="1920" height="1080" '
            f'poster="{raiz}video/{poster}" aria-label="{rotulo}">'
            f'<source src="{raiz}video/{mp4}" type="video/mp4"></video>')


def _extras(lang, raiz):
    js = (SRC / "idioma.js").read_text(encoding="utf-8")
    cabeca = "\n".join([
        f'<link rel="alternate" hreflang="pt-BR" href="{URL}">',
        f'<link rel="alternate" hreflang="en" href="{URL}en/">',
        f'<link rel="alternate" hreflang="x-default" href="{URL}en/">',
        f"<script>\n{js}</script>",
    ])
    botoes = []
    for cod, (pasta, rotulo) in IDIOMAS.items():
        atual = ' aria-current="true"' if cod == lang else ""
        href = ((raiz + pasta) or "./") + f"?lang={cod}"
        botoes.append(f'<a href="{href}" hreflang="{cod}" lang="{cod}"{atual} '
                      f'onclick="guardarIdioma(\'{cod}\')">{rotulo}</a>')
    troca = ('<div class="lang" role="group" aria-label="Idioma / Language">'
             + "".join(botoes) + "</div>")
    video = _video(raiz, f"poster-{lang}-16x9.jpg", f"orbita-{lang}-16x9.mp4", VIDEO_LABEL[lang])
    fotons = _video(raiz, f"poster-fotons-{lang}-16x9.jpg", f"laboratorio-de-fotons-{lang}-16x9.mp4",
                    FOTONS_LABEL[lang])
    harpa = _video(raiz, f"poster-harpa-{lang}-16x9.jpg", f"harpa-crista-{lang}-16x9.mp4", HARPA_LABEL[lang])
    return {"cabeca_idioma": cabeca, "troca_idioma": troca, "orbita_video": video, "fotons_video": fotons,
            "harpa_video": harpa, "apoio": _apoio(lang, raiz)}


def main():
    molde = (SRC / "molde.html").read_text(encoding="utf-8")
    for lang, (pasta, _) in IDIOMAS.items():
        textos = json.loads((SRC / "textos" / f"{lang}.json").read_text(encoding="utf-8"))
        textos.update(_extras(lang, textos["raiz"]))
        html = re.sub(r"\{\{(\w+)\}\}", lambda m: textos[m.group(1)], molde)
        if "{{" in html:
            raise SystemExit(f"{lang}: chave sem texto")
        destino = RAIZ / pasta / "index.html"
        destino.parent.mkdir(exist_ok=True)
        destino.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
