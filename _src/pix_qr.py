"""Gera img/pix-qr.svg a partir do PIX do gerar.py.   <python com segno> _src/pix_qr.py"""
import pathlib
import sys

import segno

SRC = pathlib.Path(__file__).parent
sys.path.insert(0, str(SRC))
from gerar import PIX  # noqa: E402

ARQ = SRC.parent / "img/pix-qr.svg"
segno.make(PIX, error="m").save(str(ARQ), scale=4, border=2, dark="#14213d", light="#ffffff",
                                 xmldecl=False, svgns=True)
# Com viewBox o SVG escala no tamanho que o CSS pedir (sem ele, o navegador corta).
svg = ARQ.read_text()
lado = svg.split('width="')[1].split('"')[0]
ARQ.write_text(svg.replace("<svg ", f'<svg viewBox="0 0 {lado} {lado}" ', 1))
