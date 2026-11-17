// Escolha de idioma do site. Sem servico externo: usa o idioma pedido no
// link (?lang=, vem do botao PT | EN), a escolha guardada ou, na primeira
// visita, o idioma do aparelho.
function lerSalvo(storage) {
  if (!storage) return null;
  try { var v = storage.getItem("idioma"); return v === "pt" || v === "en" ? v : null; }
  catch (e) { return null; }
}
// Devolve o caminho para onde ir, ou null para ficar.
function escolherIdioma(langs, salvo, caminho, pedido) {
  // O botao leva o idioma no link: quem clicou fica onde clicou, mesmo com
  // o armazenamento bloqueado (sem isto o aparelho em ingles mandaria de volta).
  if (pedido === "pt" || pedido === "en") return null;
  var emEn = /\/en\/(index\.html)?$/.test(caminho);
  if (salvo === "en") return emEn ? null : "/en/";
  if (salvo === "pt") return emEn ? "/" : null;
  // Quem chegou por um link para /en/ fica em ingles.
  if (emEn) return null;
  var primeiro = (langs && langs[0]) ? String(langs[0]).toLowerCase() : "";
  return primeiro.indexOf("pt") === 0 ? null : "/en/";
}
// Ler window.localStorage ja lanca quando o navegador bloqueia dados do site.
function _storage() { try { return window.localStorage; } catch (e) { return null; } }
function guardarIdioma(v) { try { _storage().setItem("idioma", v); } catch (e) {} }
if (typeof window !== "undefined" && location.protocol !== "file:" &&
    !/bot|crawl|spider|slurp/i.test(navigator.userAgent)) {
  var _pedido = (/[?&]lang=(pt|en)\b/.exec(location.search) || [])[1] || null;
  if (_pedido) guardarIdioma(_pedido);
  var _destino = escolherIdioma(navigator.languages || [navigator.language],
    lerSalvo(_storage()), location.pathname, _pedido);
  if (_destino) location.replace(_destino + location.hash);
}
