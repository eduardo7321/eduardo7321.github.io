"""Politicas de privacidade dos apps, geradas a partir de _src/politicas/<app>.md.

Cada uma vira <app>-privacidade/index.html na raiz do site. O caminho e o
mesmo que ja esta cadastrado no Play Console (Orbita e Fotons): nao mudar.

O markdown aceito e so o que as politicas usam: # e ##, paragrafos, listas
com "- " (um nivel de recuo de 2 espacos), ---, **negrito**, *italico*,
`codigo` e enderecos https:// soltos no texto.
"""
import html
import pathlib
import re

SRC = pathlib.Path(__file__).parent
RAIZ = SRC.parent

# arquivo em _src/politicas -> (pasta publicada, titulo curto para o rodape)
POLITICAS = {
    "orbita": ("orbita-privacidade", "Órbita"),
    "laboratorio-de-fotons": ("laboratorio-de-fotons-privacidade", "Laboratório de Fótons"),
    "harpa-crista": ("harpa-crista-privacidade", "Harpa Cristã"),
    "laboratorio-periodico": ("laboratorio-periodico-privacidade", "Laboratório Periódico"),
}


def _inline(texto):
    t = html.escape(texto, quote=False)
    codigos = []

    def guarda(m):
        codigos.append(m.group(1))
        return f"\x00{len(codigos) - 1}\x00"

    t = re.sub(r"`([^`]+)`", guarda, t)
    t = re.sub(r"(https://[^\s<]+?)([.,;:)]?)(?=\s|$)", r'<a href="\1">\1</a>\2', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codigos[int(m.group(1))]}</code>", t)


def md_para_html(md):
    saida, para, lista = [], [], []   # lista: [(nivel, texto)]

    def fecha_para():
        if para:
            saida.append(f"<p>{_inline(' '.join(para))}</p>")
            para.clear()

    def fecha_lista():
        if not lista:
            return
        h, aberto = ["<ul>"], 0
        for i, (nivel, txt) in enumerate(lista):
            prox = lista[i + 1][0] if i + 1 < len(lista) else 0
            h.append(f"<li>{_inline(txt)}")
            if prox > nivel:
                h.append("<ul>")
                aberto += 1
            else:
                h.append("</li>")
                if prox < nivel:
                    h.append("</ul></li>")
                    aberto -= 1
        h.append("</ul></li>" * aberto + "</ul>")
        saida.append("".join(h))
        lista.clear()

    for linha in md.splitlines():
        m = re.match(r"^( *)- (.*)$", linha)
        if m:
            fecha_para()
            lista.append((len(m.group(1)) // 2, m.group(2)))
            continue
        fecha_lista()
        if not linha.strip():
            fecha_para()
        elif linha.strip() == "---":
            fecha_para()
            saida.append("<hr>")
        elif linha.startswith("## "):
            fecha_para()
            saida.append(f"<h2>{_inline(linha[3:])}</h2>")
        elif linha.startswith("# "):
            fecha_para()
            saida.append(f"<h1>{_inline(linha[2:])}</h1>")
        else:
            para.append(linha.strip())
    fecha_lista()
    fecha_para()
    return "\n".join(saida)


PAGINA = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="robots" content="index, follow">
<link rel="icon" href="../favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&display=swap" rel="stylesheet">
<style>
  :root {{ --paper: #f6f8fc; --ink: #14213d; --ink-soft: #4a5875; --line: #d9e0ec; --gold: #ffcf5a; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--paper); color: var(--ink);
         font: 1.05rem/1.65 "Atkinson Hyperlegible", system-ui, sans-serif; }}
  header {{ border-bottom: 1px solid var(--line); background: #fff; }}
  header a {{ display: inline-block; padding: 16px; color: var(--ink); font-weight: 700; text-decoration: none; }}
  main {{ max-width: 760px; margin: 0 auto; padding: 32px 16px 80px; }}
  h1, h2 {{ font-family: "Bricolage Grotesque", system-ui, sans-serif; line-height: 1.2; }}
  h1 {{ font-size: clamp(1.8rem, 5vw, 2.4rem); font-weight: 800; margin: 24px 0 8px; }}
  h2 {{ font-size: 1.3rem; font-weight: 600; margin: 36px 0 8px; }}
  p, li {{ color: var(--ink-soft); }}
  strong {{ color: var(--ink); }}
  code {{ font-size: 0.9em; background: #fff; border: 1px solid var(--line); border-radius: 6px; padding: 1px 5px; word-break: break-word; }}
  a {{ color: var(--ink); overflow-wrap: anywhere; }}
  hr {{ border: 0; border-top: 1px solid var(--line); margin: 56px 0 24px; }}
</style>
</head>
<body>
<header><a href="../">← Iluminar Apps</a></header>
<main>
{corpo}
</main>
</body>
</html>
"""


def gerar():
    for nome, (pasta, _) in POLITICAS.items():
        md = (SRC / "politicas" / f"{nome}.md").read_text(encoding="utf-8")
        corpo = md_para_html(md)
        titulo = re.search(r"<h1>(.*?)</h1>", corpo).group(1)
        destino = RAIZ / pasta / "index.html"
        destino.parent.mkdir(exist_ok=True)
        destino.write_text(PAGINA.format(titulo=re.sub(r"<[^>]+>", "", titulo), corpo=corpo),
                           encoding="utf-8")


NOMES_EN = {"orbita": "Orbita", "laboratorio-de-fotons": "Photon Lab"}


def rodape(lang, raiz):
    linhas = []
    for nome, (pasta, curto) in POLITICAS.items():
        rotulo = NOMES_EN.get(nome, curto) if lang == "en" else curto
        linhas.append(f'<p><a href="{raiz}{pasta}/">{rotulo}</a></p>')
    return "\n      ".join(linhas)
