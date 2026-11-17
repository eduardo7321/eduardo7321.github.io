// Escolha de idioma do site. Sem servico externo: usa a escolha guardada
// (botao PT | EN) ou, na primeira visita, o idioma do aparelho.
function lerSalvo(storage) {
  try { var v = storage.getItem("idioma"); return v === "pt" || v === "en" ? v : null; }
  catch (e) { return null; }
}
// Devolve o caminho para onde ir, ou null para ficar.
function escolherIdioma(langs, salvo, caminho) {
  var emEn = /\/en\/(index\.html)?$/.test(caminho);
  if (salvo === "en") return emEn ? null : "/en/";
  if (salvo === "pt") return emEn ? "/" : null;
  // Quem chegou por um link para /en/ fica em ingles.
  if (emEn) return null;
  var primeiro = (langs && langs[0]) ? String(langs[0]).toLowerCase() : "";
  return primeiro.indexOf("pt") === 0 ? null : "/en/";
}
if (typeof window !== "undefined" && location.protocol !== "file:" &&
    !/bot|crawl|spider|slurp/i.test(navigator.userAgent)) {
  var _destino = escolherIdioma(navigator.languages || [navigator.language], lerSalvo(window.localStorage), location.pathname);
  if (_destino) location.replace(_destino + location.hash);
}
function guardarIdioma(v) { try { localStorage.setItem("idioma", v); } catch (e) {} }
