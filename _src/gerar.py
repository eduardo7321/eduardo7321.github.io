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
VIDEO_LABEL = {"pt": "Vídeo do Órbita, 54 segundos", "en": "Orbita video, 52 seconds"}


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
        href = (raiz + pasta) or "./"
        botoes.append(f'<a href="{href}" hreflang="{cod}" lang="{cod}"{atual} '
                      f'onclick="guardarIdioma(\'{cod}\')">{rotulo}</a>')
    troca = ('<div class="lang" role="group" aria-label="Idioma / Language">'
             + "".join(botoes) + "</div>")
    video = (f'<video class="feature" controls preload="none" playsinline width="1920" height="1080" '
             f'poster="{raiz}video/poster-{lang}-16x9.jpg" aria-label="{VIDEO_LABEL[lang]}">'
             f'<source src="{raiz}video/orbita-{lang}-16x9.mp4" type="video/mp4"></video>')
    return {"cabeca_idioma": cabeca, "troca_idioma": troca, "orbita_video": video}


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
