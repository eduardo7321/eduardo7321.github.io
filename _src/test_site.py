"""Testes do site bilingue.   python3 _src/test_site.py"""
import json
import pathlib
import re
import subprocess
import sys
import unittest

SRC = pathlib.Path(__file__).parent
RAIZ = SRC.parent
sys.path.insert(0, str(SRC))


class Site(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import gerar
        gerar.main()
        cls.pt = (RAIZ / "index.html").read_text(encoding="utf-8")
        cls.en = (RAIZ / "en/index.html").read_text(encoding="utf-8")

    def test_sem_chave_faltando(self):
        pt = json.loads((SRC / "textos/pt.json").read_text(encoding="utf-8"))
        en = json.loads((SRC / "textos/en.json").read_text(encoding="utf-8"))
        self.assertEqual(set(pt), set(en))
        for html in (self.pt, self.en):
            self.assertNotIn("{{", html)

    def test_idioma_da_pagina(self):
        self.assertIn('<html lang="pt-BR">', self.pt)
        self.assertIn('<html lang="en">', self.en)
        self.assertIn("orbita-pt-16x9.mp4", self.pt)
        self.assertIn("orbita-en-16x9.mp4", self.en)
        self.assertNotIn("Jogos que ensinam", self.en)

    def test_hreflang(self):
        for html in (self.pt, self.en):
            self.assertIn('hreflang="pt-BR" href="https://eduardo7321.github.io/"', html)
            self.assertIn('hreflang="en" href="https://eduardo7321.github.io/en/"', html)
            self.assertIn('hreflang="x-default" href="https://eduardo7321.github.io/en/"', html)

    def test_caminhos_relativos_existem(self):
        for nome, html, base in (("pt", self.pt, RAIZ), ("en", self.en, RAIZ / "en")):
            for ref in re.findall(r'(?:src|poster|href)="((?:\.\./)?(?:img|video)/[^"]+)"', html):
                self.assertTrue((base / ref).resolve().exists(), f"{nome}: {ref}")

    def _node(self, codigo):
        js = (SRC / "idioma.js").read_text(encoding="utf-8")
        out = subprocess.run(["node", "-e", js + "\n" + codigo], capture_output=True, text=True, check=True)
        return out.stdout.strip()

    def test_redirect_logic(self):
        casos = [
            (["pt-PT"], None, "/", "null"),
            (["pt"], None, "/", "null"),
            (["pt-AO"], None, "/", "null"),
            (["es"], None, "/", "/en/"),
            (["fr-FR"], None, "/", "/en/"),
            (["pt-BR"], "en", "/", "/en/"),
            (["es"], None, "/en/", "null"),
            (["en"], "pt", "/en/", "/"),
            (["en"], "en", "/en/", "null"),
            (["pt-BR"], "pt", "/", "null"),
            ([], None, "/", "/en/"),
        ]
        for langs, salvo, caminho, esperado in casos:
            r = self._node(f"console.log(String(escolherIdioma({json.dumps(langs)}, {json.dumps(salvo)}, {json.dumps(caminho)})))")
            self.assertEqual(r, esperado, (langs, salvo, caminho))

    def test_storage_bloqueado(self):
        r = self._node('var s={getItem:function(){throw new Error("bloqueado")}};'
                       'console.log(String(lerSalvo(s)))')
        self.assertEqual(r, "null")


if __name__ == "__main__":
    unittest.main()
