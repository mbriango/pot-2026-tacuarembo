#!/usr/bin/env python3
"""Build a navigable HTML site from Obsidian POT markdown files."""

import os, re, glob, shutil, html as html_mod
from pathlib import Path
from markdown_it import MarkdownIt

MD = MarkdownIt('default', {'linkify': False})

BASE = Path(__file__).parent
OUT = BASE / "_site"
NOTES_DIR = BASE
ZE_DIR = BASE / "Zonas-Especiales"
ZR_DIR = BASE / "Zonas-Reglamentadas"

# ── collect all notes ──────────────────────────────────────────────
notes = {}  # slug -> {title, path, content_md}

def add_note(filepath):
    rel = filepath.relative_to(BASE)
    slug = rel.stem
    title = slug.replace("-", " ").replace("_", " ").title()
    content = filepath.read_text(encoding="utf-8")
    notes[slug] = {"title": title, "path": rel, "content": content, "filepath": filepath}

for f in sorted(BASE.glob("*.md")):
    if f.name == "build_site.py": continue
    add_note(f)
for f in sorted(ZE_DIR.glob("*.md")):
    add_note(f)
for f in sorted(ZR_DIR.glob("*.md")):
    add_note(f)

# ── resolve wikilinks ──────────────────────────────────────────────
def resolve_wikilink(text):
    def repl(m):
        target = m.group(1).strip()
        # split on | for display text
        if "|" in target:
            link, label = target.split("|", 1)
        else:
            link = target
            label = target.replace("-", " ").replace("_", " ").title()
        slug = link.strip().replace(" ", "-").lower()
        # try to find note
        for s in notes:
            if s.lower() == slug or s.lower().replace("_", "-") == slug:
                href = f"{s}.html"
                return f'[{html_mod.escape(label.strip())}]({href})'
        # try fuzzy
        for s in notes:
            if slug in s.lower() or s.lower() in slug:
                href = f"{s}.html"
                return f'[{html_mod.escape(label.strip())}]({href})'
        return f'~~{html_mod.escape(label.strip())}~~ (enlace roto)'
    return re.sub(r'(?<!!)\[\[(.+?)\]\]', repl, text)

# ── convert markdown to html ───────────────────────────────────────
def md_to_html(md_text):
    # pre-process wikilinks
    md_text = resolve_wikilink(md_text)
    # fix relative image paths
    # If image already has a path prefix (e.g., fichas/), use as-is
    # Otherwise, default to laminas/
    def fix_img_path(m):
        img = m.group(1)
        if '/' in img:
            return f'![{img}]({img})'
        return f'![{img}](laminas/{img})'
    md_text = re.sub(r'!\[\[([^\]]+)\]\]', fix_img_path, md_text)
    html = MD.render(md_text)
    return html

# ── template ───────────────────────────────────────────────────────
NAV_HTML = """
<div class="nav-header">
  <h2><a href="index.html">🗺️ POT Tacuarembó</a></h2>
  <p>Revisión 2025</p>
</div>
<hr>
<div class="nav-section">
  <h3><a href="POT-Tacuarembo-MOC.html">📋 Mapa de Contenido</a></h3>
</div>
<div class="nav-section">
  <h3>⭐ Zonas Especiales</h3>
  <ul class="nav-list">
""" + "\n".join(f'    <li><a href="{s}.html">{notes[s]["title"]}</a></li>'
    for s in sorted(n for n in notes if n.startswith("ZE"))) + """
  </ul>
</div>
<div class="nav-section">
  <h3>📋 Zonas Reglamentadas</h3>
  <ul class="nav-list">
""" + "\n".join(f'    <li><a href="{s}.html">{notes[s]["title"]}</a></li>'
    for s in sorted(n for n in notes if n.startswith("ZR"))) + """
  </ul>
</div>
<hr>
<div class="nav-section">
  <ul class="nav-list">
    <li><a href="Laminas-MOC.html">🗺️ Láminas</a></li>
    <li><a href="Enclaves-Suburbanos.html">🏭 Enclaves</a></li>
    <li><a href="Riesgo-Inundacion.html">🌊 Riesgo</a></li>
    <li><a href="Proyectos-Estrategicos.html">📋 Proyectos</a></li>
    <li><a href="Sistema-Vial.html">🛣️ Vialidad</a></li>
    <li><a href="Espacios-Publicos.html">🌳 Esp. Públicos</a></li>
    <li><a href="Categorizacion-Suelo.html">🏷️ Categorías</a></li>
    <li><a href="Estructura-Modelo-Territorial.html">🏗️ Modelo</a></li>
    <li><a href="Analisis-Critico.html">⚠️ Análisis Crítico</a></li>
  </ul>
</div>
<hr>
<div class="nav-section">
  <ul class="nav-list">
    <li><a href="Articulado-Completo.html">📜 Articulado Completo</a></li>
  </ul>
</div>
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — POT Tacuarembó</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f5f5f0; color: #222; }}
  
  /* ── hamburger button (mobile only) ── */
  #menu-toggle {{
    display: none;
    position: fixed; top: 0.7rem; left: 0.7rem; z-index: 1001;
    background: #1a1a2e; color: #fff; border: none;
    width: 40px; height: 40px; border-radius: 8px;
    font-size: 1.4rem; cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  }}
  #menu-overlay {{
    display: none;
    position: fixed; inset: 0; z-index: 998;
    background: rgba(0,0,0,0.4);
  }}
  #menu-overlay.show {{ display: block; }}

  #layout {{ display: flex; min-height: 100vh; }}
  #sidebar {{
    width: 280px; background: #1a1a2e; color: #eee; padding: 1.2rem;
    position: sticky; top: 0; height: 100vh; overflow-y: auto;
    flex-shrink: 0;
  }}
  #sidebar a {{ color: #a8d8ea; text-decoration: none; }}
  #sidebar a:hover {{ color: #fff; text-decoration: underline; }}
  #sidebar h2 {{ font-size: 1.1rem; margin-bottom: 0.3rem; }}
  #sidebar h2 a {{ color: #fff; }}
  #sidebar h3 {{ font-size: 0.85rem; margin: 0.8rem 0 0.3rem; color: #888; text-transform: uppercase; letter-spacing: 0.05em; }}
  #sidebar p {{ font-size: 0.75rem; color: #888; }}
  .nav-list {{ list-style: none; padding-left: 0.5rem; font-size: 0.8rem; }}
  .nav-list li {{ margin: 0.15rem 0; }}
  .nav-list a {{ color: #c0d8e8; }}
  .nav-section {{ margin-bottom: 0.5rem; }}
  hr {{ border: none; border-top: 1px solid #333; margin: 0.6rem 0; }}
  #content {{
    flex: 1; padding: 2rem 3rem; max-width: 900px;
    background: #fff; margin: 1rem 2rem 1rem 1rem;
    border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    line-height: 1.6;
  }}
  #content h1 {{ font-size: 1.8rem; margin-bottom: 1rem; color: #1a1a2e; border-bottom: 2px solid #e0e0e0; padding-bottom: 0.5rem; }}
  #content h2 {{ font-size: 1.3rem; margin: 1.5rem 0 0.5rem; color: #2d4059; }}
  #content h3 {{ font-size: 1.1rem; margin: 1rem 0 0.3rem; color: #444; }}
  #content p {{ margin: 0.5rem 0; }}
  #content table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.9rem; }}
  #content th, #content td {{ border: 1px solid #ddd; padding: 0.4rem 0.6rem; text-align: left; }}
  #content th {{ background: #f0f0e8; font-weight: 600; }}
  #content tr:nth-child(even) {{ background: #fafaf5; }}
  #content code {{ background: #f0f0e8; padding: 0.15rem 0.3rem; border-radius: 3px; font-size: 0.85rem; }}
  #content pre {{ background: #f5f5f0; padding: 0.8rem; border-radius: 4px; overflow-x: auto; font-size: 0.85rem; }}
  #content a {{ color: #1a5276; }}
  #content a:hover {{ color: #2980b9; }}
  #content blockquote {{ border-left: 3px solid #2d4059; padding-left: 1rem; margin: 1rem 0; color: #555; font-style: italic; }}
  #content ul, #content ol {{ margin: 0.5rem 0; padding-left: 1.5rem; }}
  #content li {{ margin: 0.2rem 0; }}
  
  /* responsive tables */
  .table-wrap {{ overflow-x: auto; margin: 1rem 0; }}
  #content table {{ min-width: 500px; }}

  .broken-link {{ color: #c0392b; font-weight: bold; text-decoration: line-through; }}
  .fuzzy {{ color: #d4a017; font-style: italic; }}
  .lamina-link {{ display: inline-block; background: #1a5276; color: #fff !important; padding: 0.3rem 0.8rem; border-radius: 4px; text-decoration: none; font-size: 0.9rem; }}
  .lamina-link:hover {{ background: #2980b9; }}
  #back-to-top {{
    position: fixed; bottom: 1.5rem; right: 1.5rem;
    background: #1a1a2e; color: #fff; border: none;
    width: 40px; height: 40px; border-radius: 50%;
    cursor: pointer; font-size: 1.2rem; display: none;
  }}
  #back-to-top:hover {{ background: #2d4059; }}

  /* ── mobile: hamburger menu ── */
  @media (max-width: 768px) {{
    #menu-toggle {{ display: block; }}
    #layout {{ flex-direction: column; }}
    #sidebar {{
      position: fixed; top: 0; left: -300px;
      width: 280px; height: 100vh; z-index: 999;
      transition: left 0.25s ease;
      box-shadow: 4px 0 12px rgba(0,0,0,0.2);
    }}
    #sidebar.open {{ left: 0; }}
    #content {{
      margin: 0.5rem; padding: 1rem;
      padding-top: 3.5rem;
    }}
    /* inline images on mobile */
    #content img {{ max-width: 100%; height: auto; }}
  }}
</style>
</head>
<body>
<div id="layout">
<button id="menu-toggle" onclick="toggleMenu()" title="Menú">☰</button>
<div id="menu-overlay" onclick="toggleMenu()"></div>
<div id="sidebar">
  {nav}
</div>
<div id="content">
  {content}

<hr>
<footer style="text-align:center;font-size:0.85rem;padding:1rem 0;color:#666;border-top:1px solid #e0e0e0;margin-top:1.5rem;">
  <p><a href="index.html">← Volver al inicio</a></p>
  <p>Elaborado por <strong>La Nueve</strong></p>
</footer>

</div>
</div>
<button id="back-to-top" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" title="Volver arriba">↑</button>
<script>
  function toggleMenu() {{
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('menu-overlay').classList.toggle('show');
  }}
  window.addEventListener('scroll', function(){{
    const btn = document.getElementById('back-to-top');
    if (btn) btn.style.display = window.scrollY > 300 ? 'block' : 'none';
  }});
</script>
</body>
</html>
"""

# ── build all pages ─────────────────────────────────────────────────
OUT.mkdir(parents=True, exist_ok=True)

for slug, info in notes.items():
    title = info["title"]
    md_content = info["content"]
    html_body = md_to_html(md_content)
    page = HTML_TEMPLATE.format(title=html_mod.escape(title), nav=NAV_HTML, content=html_body)
    outfile = OUT / f"{slug}.html"
    outfile.write_text(page, encoding="utf-8")

# ── also build index ────────────────────────────────────────────────
index_md = BASE / "POT-Tacuarembo-MOC.md"
if index_md.exists():
    title = "POT Tacuarembó — Mapa de Contenido"
    md_content = index_md.read_text(encoding="utf-8")
    html_body = md_to_html(md_content)
    page = HTML_TEMPLATE.format(title=html_mod.escape("POT Tacuarembó — Navegable"), nav=NAV_HTML, content=html_body)
    (OUT / "index.html").write_text(page, encoding="utf-8")

# ── copy assets ──────────────────────────────────────────────────
laminas_src = BASE / "Laminas"
laminas_dst = OUT / "laminas"
if laminas_src.exists():
    laminas_dst.mkdir(parents=True, exist_ok=True)
    for img in laminas_src.iterdir():
        if img.suffix.lower() in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            shutil.copy2(img, laminas_dst / img.name)
    img_count = len(list(laminas_dst.iterdir()))
    print(f"   {img_count} imágenes copiadas a _site/laminas/")

# ── copy fichas (zone data sheets) ────────────────────────────
fichas_src = BASE / "fichas"
fichas_dst = OUT / "fichas"
if fichas_src.exists():
    fichas_dst.mkdir(parents=True, exist_ok=True)
    for img in fichas_src.iterdir():
        if img.suffix.lower() in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            shutil.copy2(img, fichas_dst / img.name)
    ficha_count = len(list(fichas_dst.iterdir()))
    print(f"   {ficha_count} fichas copiadas a _site/fichas/")

count = len(list(OUT.glob("*.html")))
print(f"✅ Sitio generado: {count} páginas HTML en {OUT}")
print(f"   Abrí file://{OUT / 'index.html'} en tu navegador")
