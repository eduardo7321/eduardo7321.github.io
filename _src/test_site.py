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

    def test_so_a_harpa_diz_sem_anuncios(self):
        # Fotons, Orbita e Periodico tem (ou vao ter) anuncio; so a Harpa e livre deles.
        for chave, txt in json.loads((SRC / "textos/pt.json").read_text(encoding="utf-8")).items():
            if "sem anúncio" in txt.lower() or "não tem anúncio" in txt.lower():
                self.assertTrue(chave.startswith("harpa"), chave)
        for chave, txt in json.loads((SRC / "textos/en.json").read_text(encoding="utf-8")).items():
            if "no ads" in txt.lower():
                self.assertTrue(chave.startswith("harpa"), chave)

    POLITICAS = {
        "orbita-privacidade": "com.eduardo.orbita",
        "laboratorio-de-fotons-privacidade": "com.eduardo.laboratoriodefotons",
        "harpa-crista-privacidade": "com.eduardo.harpacrista",
        "laboratorio-periodico-privacidade": "com.eduardo.laboratorioperiodico",
    }

    def test_politicas_no_site(self):
        for pasta, pacote in self.POLITICAS.items():
            html = (RAIZ / pasta / "index.html").read_text(encoding="utf-8")
            self.assertIn(pacote, html, pasta)
            self.assertIn("<h1", html)
            self.assertIn('href="../"', html)          # volta para o site
            self.assertNotIn("**", html, pasta)        # markdown convertido
            self.assertNotIn("{{", html)
            for lang_html in (self.pt, self.en):      # rodape liga todas, sem dominio fixo
                self.assertIn(f'href="{"../" if lang_html is self.en else ""}{pasta}/"', lang_html)
        harpa = (RAIZ / "harpa-crista-privacidade/index.html").read_text(encoding="utf-8")
        self.assertIn("Não há anúncios", harpa)
        per = (RAIZ / "laboratorio-periodico-privacidade/index.html").read_text(encoding="utf-8")
        self.assertIn("AdMob", per)
        self.assertIn("13 anos", per)
        self.assertNotIn("eduardo7321.github.io", (SRC / "molde.html").read_text(encoding="utf-8"))

    def test_markdown_da_politica(self):
        import politica
        h = politica.md_para_html("# T\n\nUm **b** e `c` em https://x.org/a\n\n- um\n  - dois\n- tres\n\n---\n\n## S")
        self.assertIn("<h1>T</h1>", h)
        self.assertIn("<strong>b</strong>", h)
        self.assertIn("<code>c</code>", h)
        self.assertIn('<a href="https://x.org/a">https://x.org/a</a>', h)
        self.assertIn("<li>um<ul><li>dois</li></ul></li>", h)
        self.assertIn("<hr>", h)
        self.assertIn("<h2>S</h2>", h)

    def test_idioma_da_pagina(self):
        self.assertIn('<html lang="pt-BR">', self.pt)
        self.assertIn('<html lang="en">', self.en)
        self.assertIn("orbita-pt-16x9.mp4", self.pt)
        self.assertIn("orbita-en-16x9.mp4", self.en)
        self.assertNotIn("Jogos que ensinam", self.en)

    def test_video_fotons(self):
        for lang, html in (("pt", self.pt), ("en", self.en)):
            fotons = html[html.index('class="game fotons"'):]
            fotons = fotons[:fotons.index("</section>")]
            self.assertIn(f"video/laboratorio-de-fotons-{lang}-16x9.mp4", fotons)
            self.assertIn(f"video/poster-fotons-{lang}-16x9.jpg", fotons)
            self.assertLess(fotons.index("<video"), fotons.index('class="shots"'))
        self.assertIn('aria-label="Vídeo do Laboratório de Fótons, 1 minuto e 32 segundos"', self.pt)
        self.assertIn('aria-label="Photon Lab video, 1 minute and 30 seconds"', self.en)

    def test_video_harpa(self):
        for lang, html in (("pt", self.pt), ("en", self.en)):
            harpa = html[html.index('class="harpa"'):]
            harpa = harpa[:harpa.index("</section>")]
            self.assertIn(f"video/harpa-crista-{lang}-16x9.mp4", harpa)
            self.assertIn(f"video/poster-harpa-{lang}-16x9.jpg", harpa)
        self.assertIn('aria-label="Vídeo da Harpa Cristã, 1 minuto e 25 segundos"', self.pt)
        self.assertIn('aria-label="Harpa Cristã video, 1 minute and 29 seconds"', self.en)

    def test_apoio_pix(self):
        import gerar
        pix = gerar.PIX
        self.assertTrue(pix.startswith("000201") and "BR.GOV.BCB.PIX" in pix)
        self.assertEqual(gerar.crc_pix(pix[:-4]), pix[-4:])
        self.assertNotIn("5406", pix.split("5303986")[1][:4])   # sem valor fixo
        apoio = self.pt[self.pt.index('id="apoie"'):]
        apoio = apoio[:apoio.index("</section>")]
        self.assertIn(pix, apoio)
        self.assertIn('src="img/pix-qr.svg"', apoio)
        self.assertIn("Copiar código Pix", apoio)
        self.assertTrue((RAIZ / "img/pix-qr.svg").exists())
        nav = self.pt[self.pt.index("<nav"):self.pt.index("</nav>")]
        self.assertLess(nav.index('href="#fale"'), nav.index('<a href="#apoie">Apoie</a>'))
        self.assertNotIn("BR.GOV.BCB.PIX", self.en)
        self.assertNotIn("ko-fi.com", self.pt)   # no Brasil, so Pix

    def test_apoio_kofi_no_ingles(self):
        apoio = self.en[self.en.index('id="support"'):]
        apoio = apoio[:apoio.index("</section>")]
        self.assertIn('href="https://ko-fi.com/iluminarapps"', apoio)
        self.assertIn("Support on Ko-fi", apoio)
        self.assertIn('rel="noopener"', apoio)
        nav = self.en[self.en.index("<nav"):self.en.index("</nav>")]
        self.assertLess(nav.index('href="#fale"'),
                        nav.index('<a href="#support">Support</a>'))

    def test_video_periodico(self):
        for lang, html in (("pt", self.pt), ("en", self.en)):
            secao = html[html.index('class="game periodico"'):]
            secao = secao[:secao.index("</section>")]
            self.assertIn(f"video/laboratorio-periodico-{lang}-16x9.mp4", secao)
            self.assertIn(f"video/poster-periodico-{lang}-16x9.jpg", secao)
            self.assertLess(secao.index("<video"), secao.index('class="shots"'))
        self.assertIn('aria-label="Vídeo do Laboratório Periódico, 1 minuto e 35 segundos"', self.pt)
        self.assertIn('aria-label="Laboratório Periódico video, 1 minute and 36 seconds"', self.en)

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

    def _pagina(self, idioma, caminho, busca, storage_lanca):
        """Roda o idioma.js como no navegador; devolve para onde redirecionou."""
        js = (SRC / "idioma.js").read_text(encoding="utf-8")
        ambiente = (
            "var destino = null;"
            "var location = {protocol: 'https:', pathname: %s, search: %s, hash: '',"
            " replace: function (u) { destino = u; }};"
            "var navigator = {userAgent: 'Mozilla/5.0', languages: [%s]};"
            "var window = {};"
            "Object.defineProperty(window, 'localStorage', {get: function () {"
            "  if (%s) throw new Error('SecurityError'); return {getItem: function () { return null; }};"
            "}});"
        ) % (json.dumps(caminho), json.dumps(busca), json.dumps(idioma), "true" if storage_lanca else "false")
        # Dentro de uma funcao: o Node tem um `navigator` global que nao aceita troca.
        codigo = "(function () {" + ambiente + js + "\nconsole.log(String(destino)); })()"
        out = subprocess.run(["node", "-e", codigo],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        return out.stdout.strip()

    def test_storage_bloqueado_no_navegador(self):
        # Ler window.localStorage lanca: a pagina nao quebra e segue o aparelho.
        self.assertEqual(self._pagina("en-US", "/", "", True), "/en/")
        self.assertEqual(self._pagina("pt-BR", "/", "", True), "null")

    def test_botao_pt_sem_storage(self):
        # Aparelho em ingles, storage bloqueado, clicou PT: fica no portugues.
        self.assertEqual(self._pagina("en-US", "/", "?lang=pt", True), "null")
        self.assertEqual(self._pagina("pt-BR", "/en/", "?lang=en", True), "null")

    def test_links_carregam_escolha(self):
        self.assertIn('href="./?lang=pt"', self.pt)
        self.assertIn('href="en/?lang=en"', self.pt)
        self.assertIn('href="../?lang=pt"', self.en)

    def test_storage_bloqueado(self):
        r = self._node('var s={getItem:function(){throw new Error("bloqueado")}};'
                       'console.log(String(lerSalvo(s)))')
        self.assertEqual(r, "null")


if __name__ == "__main__":
    unittest.main()
