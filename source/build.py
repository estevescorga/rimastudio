#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re, os, shutil, html

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
IMG_SRC = os.path.join(ROOT, "web")
SITE_URL = "https://rimastudio.pt"

with open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8") as f:
    SITE = json.load(f)
with open(os.path.join(ROOT, "data", "layouts.json"), encoding="utf-8") as f:
    LAYOUTS = json.load(f)
with open(os.path.join(ROOT, "data", "projects.json"), encoding="utf-8") as f:
    PROJECTS = json.load(f)

# Grid-cover images, verified directly against the original Wix portfolio
# grid (these are dedicated "cover" assets Wix shows in the grid — distinct
# from each project's own gallery images, which project_thumb() used to
# fall back to, causing mismatched covers). Not every project's cover was
# identifiable from the original grid (a handful of aria-labels resolved to
# a generic filename instead of a title); those fall back to images[0] as
# before rather than risk assigning the wrong cover.
PROJECT_COVERS = {
    "casa-del-yoga": "e46b83_c4b327d36daf43c28df78df939c7d722~mv2.jpg",
    "tailor-made-events": "e46b83_40d16cd77b3b4c10a7119cae445dce7c~mv2.jpg",
    "olqnsoqqs": "e46b83_30144659456e4619bac8ad62ed123b3e~mv2.png",
    "noveme": "e46b83_c9a37c77c82f41c2945698a8e622855a~mv2.jpg",
    "kc-the-brand": "e46b83_8f4ee2b58a154d30a42cf09a6e6c21cf~mv2.jpg",
    "vicente": "e46b83_cfb5d8448a474535b994fc26b0d7f40b~mv2.jpg",
    "armar-o-baile": "e46b83_a1e776c3cfde4bfab850e3c29284a0dd~mv2.jpg",
    "talismas": "e46b83_7dd5050fb3014385bb97746b8b42f2c8~mv2.png",
    "de-la-espada-lookbook": "e46b83_27529189680446629d90e9cf22817098~mv2.jpg",
    "quinta-foz-do-sabor": "e46b83_f37bdc8a7cb04ac889ae03b5ead39463~mv2.jpg",
    "andanças-22": "e46b83_87c6e59e7a904caf88e6441f3746ce3d~mv2.jpg",
    "videoclip-linho": "e46b83_8d069f206f8845d89d97cc0bd9b62be3~mv2.jpg",
    "ctt-retrospectiva-2022": "e46b83_dc0bd52946df4815b284f167a4f7d20f~mv2.jpg",
    "o-protesto-do-lobo-mau": "e46b83_c134117eef5c4c5093995219dc7c1592~mv2.jpg",
    "dahu-shoes-off": "e46b83_8f3cfc3436114b359293f4913fcc6605~mv2.jpg",
    "padrao-byou": "e46b83_09961fc6f03e4ae09cd558fd2022562a~mv2.jpg",
    "omami": "e46b83_717ac4218a7f419d8569c7549bec7e0a~mv2.png",
    "jfdo": "e46b83_b42f5b3325474cd48b001b49b703aec9~mv2.jpg",
    "mil-jewellery": "e46b83_2762a212ca4d45338eaec60485545332~mv2.jpg",
    "troglodicas": "e46b83_67db48c2f53b481792271e3059c21143~mv2.jpg",
    "eclipse": "e46b83_f999c48213f84b7bbbbb1dc4625a1255~mv2.png",
    "the-bear-collection": "e46b83_627fd07c940b4bd4b0e36c2b437d5042~mv2.png",
    "o-pequeno-ego": "e46b83_82d79fb18de9415ea1582896ae679c57~mv2.png",
}

# Order of the tiles on the original portfolio grid (verified against the Wix site).
PORTFOLIO_ORDER = ["casa-del-yoga", "tailor-made-events", "olqnsoqqs", "noveme", "jfdo",
    "kc-the-brand", "vicente", "armar-o-baile", "talismas", "de-la-espada-lookbook",
    "quinta-foz-do-sabor", "mil-jewellery", "andanças-22", "troglodicas", "videoclip-linho",
    "ctt-retrospectiva-2022", "o-protesto-do-lobo-mau", "dahu-shoes-off", "padrao-byou",
    "eclipse", "omami", "o-pequeno-ego", "the-bear-collection"]

MISSION_LINES_PT = ["A TECNOLOGIA TRANSFORMA A FORMA", "COMO CRIAMOS. O OLHAR HUMANO", "CONTINUA A FAZER A DIFERENÇA."]
MISSION_LINES_EN = ["TECHNOLOGY IS CHANGING THE WAY", "WE CREATE. THE HUMAN PERSPECTIVE", "STILL MAKES THE DIFFERENCE."]

# Current build pass language ('pt' or 'en'). main() builds the whole site
# once per language. PT pages are written at the site root; EN pages under
# /en/ — real, separate, crawlable URLs (not a client-side toggle), so each
# language can be indexed and linked independently (hreflang ties them
# together below).
LANG = "pt"

STATIC_FILENAMES = ["index.html", "portfolio.html", "oestudio.html",
                     "design.html", "animacao.html", "ilustracao.html"]
PROJECT_FILENAMES = [f"{p['slug']}.html" for p in PROJECTS]
DRAFT_FILENAMES = ["the-people-series.html"]  # built, in menu, but noindex and not in sitemap
ALL_FILENAMES = STATIC_FILENAMES + PROJECT_FILENAMES

def webp_name(id_):
    # strip any existing extension (.png/.jpg/.jpeg) before adding .webp
    for ext in (".png", ".jpg", ".jpeg", ".PNG", ".JPG"):
        if id_.endswith(ext):
            return id_[: -len(ext)] + ".webp"
    return id_ + ".webp"

def img(id_, cls="", alt="", eager=False):
    loading = "eager" if eager else "lazy"
    return f'<img src="/images/{webp_name(id_)}" alt="{html.escape(alt)}" loading="{loading}" class="{cls}">'

def e(s):
    return html.escape(s, quote=False) if s else ""

def url_for(filename, lang=None):
    """Absolute-from-root path for a logical page filename in a given language.
    The home page resolves to the bare directory root ("/" or "/en/") rather
    than "/index.html", so there's one canonical URL per page, not two."""
    lang = lang or LANG
    prefix = "/" if lang == "pt" else "/en/"
    if filename == "index.html":
        return prefix
    return prefix + filename

def L(pt, en):
    """Pick the text for the language currently being built."""
    return pt if LANG == "pt" else en

def bi(pt, en, tag="span", cls=""):
    """Render the current-language text in a styled tag (no JS toggle — each
    language is a separate static page now)."""
    return f'<{tag} class="{cls}">{e(L(pt, en))}</{tag}>'

BRAND_NAMES = ("RIMA studio", "RIMA lab")

def bi_brand(pt, en, tag="span", cls=""):
    """Like bi(), but bolds mentions of the studio/lab name, matching the
    original site's inline emphasis on first mention of the brand."""
    txt = e(L(pt, en))
    for b in BRAND_NAMES:
        txt = txt.replace(b, f"<strong>{b}</strong>")
    return f'<{tag} class="{cls}">{txt}</{tag}>'

def hover_tags(tags_pt, tags_en):
    """Grid-thumbnail hover caption tags: lowercase, ' . '-separated, matching
    the original site's hover treatment (project pages keep the uppercase
    ' | ' tags as-is — this is only for the grid caption)."""
    raw = L(tags_pt or "", tags_en or "")
    parts = [t.strip() for t in raw.split("|") if t.strip()]
    return " . ".join(p.lower() for p in parts)

def grid_markup(items, extra_cls=""):
    """Shared alternating narrow/wide project grid, used on the home page's
    featured projects and on the portfolio/filter pages, with a consistent
    hover caption: bold uppercase title + lowercase tags, centered at the
    bottom of the thumbnail (matching the original site). Items are grouped
    in rows of two (1/3 + 2/3, flipping sides each row, like the original);
    a lone last item gets half the row width."""
    def tile(p, size_cls):
        tags = hover_tags(p.get("tags_pt"), p.get("tags_en"))
        return f'''    <a class="grid-item {size_cls}" href="{url_for(p['slug'] + ".html")}">
      {img(project_thumb(p), alt=p['title'], eager=True)}
      <span class="grid-caption">
        <span class="grid-caption-title">{e(L(p.get('title', p['slug']), p.get('title_en', p.get('title', p['slug']))))}</span>
        <span class="grid-caption-tags">{e(tags)}</span>
      </span>
    </a>
'''
    out = f'<div class="grid {extra_cls}">\n'
    for r in range(0, len(items), 2):
        pair = items[r:r + 2]
        row_a = ((r // 2) % 2 == 0)
        if len(pair) == 1:
            out += '  <div class="grid-row row-half">\n' + tile(pair[0], 'half') + '  </div>\n'
            continue
        sizes = ('narrow', 'wide') if row_a else ('wide', 'narrow')
        out += f'  <div class="grid-row {"row-a" if row_a else "row-b"}">\n'
        out += tile(pair[0], sizes[0]) + tile(pair[1], sizes[1])
        out += '  </div>\n'
    out += '</div>'
    return out

def clients_section(eyebrow_html, title_or_text_html):
    """Continuously auto-scrolling strip of client logos (the logo list is
    rendered twice back-to-back so the CSS animation loops seamlessly)."""
    logos = SITE['oestudio']['client_logos']
    track = "".join(f'      {img(logo, alt="cliente")}\n' for logo in logos * 2)
    return f'''    <div class="clients-strip">
      <div class="clients-track">
{track}      </div>
    </div>
'''

NAV_ITEMS = [
    ("index.html", "HOME", "HOME"),
    ("portfolio.html", "PORTFOLIO", "WORK"),
    ("oestudio.html", "O ESTÚDIO", "THE STUDIO"),
]

def base_head(filename, title, desc=""):
    pt_url = SITE_URL + url_for(filename, "pt")
    en_url = SITE_URL + url_for(filename, "en")
    canonical = SITE_URL + url_for(filename, LANG)
    locale = "pt_PT" if LANG == "pt" else "en_US"
    noindex = '<meta name="robots" content="noindex, nofollow">\n' if filename in DRAFT_FILENAMES else ""
    return f'''<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{noindex}<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="pt" href="{pt_url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="x-default" href="{pt_url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="{locale}">
<link rel="icon" href="/images/{webp_name(SITE['meta']['favicon'])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Karla:ital,wght@0,400;0,700;1,400&family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/style.css">
'''

def header(filename="index.html"):
    home_url = url_for("index.html")
    portfolio_url = url_for("portfolio.html")
    oestudio_url = url_for("oestudio.html")
    design_url = url_for("design.html")
    animacao_url = url_for("animacao.html")
    ilustracao_url = url_for("ilustracao.html")
    pt_url = url_for(filename, "pt")
    en_url = url_for(filename, "en")

    return f'''<header class="site-header" id="siteHeader">
  <div class="site-header-inner">
    <button class="menu-btn" id="menuBtn" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
    <a href="{home_url}" class="logo">{img(SITE['meta']['logo'], 'logo-img', eager=True)}</a>
    <nav class="lang-switch">
      <a href="{pt_url}" class="lang-btn {'active' if LANG=='pt' else ''}" hreflang="pt">PT</a>
      <a href="{en_url}" class="lang-btn {'active' if LANG=='en' else ''}" hreflang="en">EN</a>
    </nav>
  </div>
</header>
<nav class="offcanvas" id="offcanvas">
  <button class="offcanvas-close" id="offcanvasClose" aria-label="Fechar">&times;</button>
  <ul class="offcanvas-nav">
    <li><a href="{home_url}">{e(L('HOME','HOME'))}</a></li>
    <li><a href="{portfolio_url}">{e(L('PORTFOLIO','WORK'))}</a>
      <ul class="offcanvas-sub">
        <li><a href="{design_url}">{e(L('#design','#design'))}</a></li>
        <li><a href="{animacao_url}">{e(L('#animação','#animation'))}</a></li>
        <li><a href="{ilustracao_url}">{e(L('#ilustração','#illustration'))}</a></li>
      </ul>
    </li>
    <li><a href="{oestudio_url}">{e(L('O ESTÚDIO','THE STUDIO'))}</a></li>
    <li><a href="{url_for('the-people-series.html')}">THE PEOPLE SERIES</a></li>
    <li><a href="{oestudio_url}#contacto">{e(L('CONTACTO','CONTACT'))}</a></li>
    <li><a href="{SITE['meta']['external']['rimalab']}" target="_blank" rel="noopener">RIMA lab</a></li>
    <li><a href="{SITE['meta']['external']['estevescorga']}" target="_blank" rel="noopener">ESTEVES CORGA</a>
      <ul class="offcanvas-sub">
        <li><a href="{SITE['meta']['external']['estevescorga']}" target="_blank" rel="noopener">{e(L('Portfolio de Autor','Author Portfolio'))}</a></li>
      </ul>
    </li>
  </ul>
  <div class="offcanvas-social">
    <a href="{SITE['meta']['social']['facebook']}" target="_blank" rel="noopener" aria-label="Facebook">{SOCIAL_SVG["facebook"]}</a>
    <a href="{SITE['meta']['social']['instagram']}" target="_blank" rel="noopener" aria-label="Instagram">{SOCIAL_SVG["instagram"]}</a>
    <a href="{SITE['meta']['social']['linkedin']}" target="_blank" rel="noopener" aria-label="LinkedIn">{SOCIAL_SVG["linkedin"]}</a>
  </div>
</nav>
<div class="offcanvas-overlay" id="offcanvasOverlay"></div>
'''

SOCIAL_SVG = {
    "facebook": '''<svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M22 12.06C22 6.5 17.52 2 12 2S2 6.5 2 12.06c0 5 3.66 9.15 8.44 9.94v-7.03H7.9v-2.91h2.54V9.84c0-2.5 1.49-3.89 3.77-3.89 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56v1.87h2.78l-.45 2.91h-2.33V22c4.78-.79 8.44-4.94 8.44-9.94z"/></svg>''',
    "instagram": '''<svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M12 2c2.72 0 3.06.01 4.12.06 1.06.05 1.78.22 2.41.46.65.25 1.2.59 1.75 1.14.5.5.9 1.1 1.14 1.75.24.63.41 1.35.46 2.41.05 1.06.06 1.4.06 4.12s-.01 3.06-.06 4.12c-.05 1.06-.22 1.78-.46 2.41a4.9 4.9 0 01-1.14 1.75 4.9 4.9 0 01-1.75 1.14c-.63.24-1.35.41-2.41.46-1.06.05-1.4.06-4.12.06s-3.06-.01-4.12-.06c-1.06-.05-1.78-.22-2.41-.46a4.9 4.9 0 01-1.75-1.14 4.9 4.9 0 01-1.14-1.75c-.24-.63-.41-1.35-.46-2.41C2.01 15.06 2 14.72 2 12s.01-3.06.06-4.12c.05-1.06.22-1.78.46-2.41.25-.65.59-1.2 1.14-1.75a4.9 4.9 0 011.75-1.14c.63-.24 1.35-.41 2.41-.46C8.94 2.01 9.28 2 12 2zm0 1.8c-2.67 0-2.99.01-4.04.06-.97.04-1.5.2-1.85.34-.46.18-.8.4-1.15.75s-.57.69-.75 1.15c-.14.35-.3.88-.34 1.85-.05 1.05-.06 1.37-.06 4.04s.01 2.99.06 4.04c.04.97.2 1.5.34 1.85.18.46.4.8.75 1.15s.69.57 1.15.75c.35.14.88.3 1.85.34 1.05.05 1.37.06 4.04.06s2.99-.01 4.04-.06c.97-.04 1.5-.2 1.85-.34.46-.18.8-.4 1.15-.75s.57-.69.75-1.15c.14-.35.3-.88.34-1.85.05-1.05.06-1.37.06-4.04s-.01-2.99-.06-4.04c-.04-.97-.2-1.5-.34-1.85a3.1 3.1 0 00-.75-1.15 3.1 3.1 0 00-1.15-.75c-.35-.14-.88-.3-1.85-.34-1.05-.05-1.37-.06-4.04-.06zm0 3.06a5.14 5.14 0 110 10.28 5.14 5.14 0 010-10.28zm0 1.8a3.34 3.34 0 100 6.68 3.34 3.34 0 000-6.68zm5.34-1.99a1.2 1.2 0 11-2.4 0 1.2 1.2 0 012.4 0z"/></svg>''',
    "linkedin": '''<svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.03-1.85-3.03-1.85 0-2.14 1.45-2.14 2.94v5.66H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29zM5.34 7.43a2.07 2.07 0 110-4.13 2.07 2.07 0 010 4.13zM7.12 20.45H3.56V9h3.56v11.45z"/></svg>''',
}

def footer():
    return f'''<footer class="site-footer">
  <div class="site-footer-inner">
    <p class="copyright">&copy; RIMA studio 2026 | Lisboa | all rights reserved</p>
    <div class="footer-social">
      <a href="{SITE['meta']['social']['facebook']}" target="_blank" rel="noopener" aria-label="Facebook">
        <svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M22 12.06C22 6.5 17.52 2 12 2S2 6.5 2 12.06c0 5 3.66 9.15 8.44 9.94v-7.03H7.9v-2.91h2.54V9.84c0-2.5 1.49-3.89 3.77-3.89 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56v1.87h2.78l-.45 2.91h-2.33V22c4.78-.79 8.44-4.94 8.44-9.94z"/></svg>
      </a>
      <a href="{SITE['meta']['social']['instagram']}" target="_blank" rel="noopener" aria-label="Instagram">
        <svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M12 2c2.72 0 3.06.01 4.12.06 1.06.05 1.78.22 2.41.46.65.25 1.2.59 1.75 1.14.5.5.9 1.1 1.14 1.75.24.63.41 1.35.46 2.41.05 1.06.06 1.4.06 4.12s-.01 3.06-.06 4.12c-.05 1.06-.22 1.78-.46 2.41a4.9 4.9 0 01-1.14 1.75 4.9 4.9 0 01-1.75 1.14c-.63.24-1.35.41-2.41.46-1.06.05-1.4.06-4.12.06s-3.06-.01-4.12-.06c-1.06-.05-1.78-.22-2.41-.46a4.9 4.9 0 01-1.75-1.14 4.9 4.9 0 01-1.14-1.75c-.24-.63-.41-1.35-.46-2.41C2.01 15.06 2 14.72 2 12s.01-3.06.06-4.12c.05-1.06.22-1.78.46-2.41.25-.65.59-1.2 1.14-1.75a4.9 4.9 0 011.75-1.14c.63-.24 1.35-.41 2.41-.46C8.94 2.01 9.28 2 12 2zm0 1.8c-2.67 0-2.99.01-4.04.06-.97.04-1.5.2-1.85.34-.46.18-.8.4-1.15.75s-.57.69-.75 1.15c-.14.35-.3.88-.34 1.85-.05 1.05-.06 1.37-.06 4.04s.01 2.99.06 4.04c.04.97.2 1.5.34 1.85.18.46.4.8.75 1.15s.69.57 1.15.75c.35.14.88.3 1.85.34 1.05.05 1.37.06 4.04.06s2.99-.01 4.04-.06c.97-.04 1.5-.2 1.85-.34.46-.18.8-.4 1.15-.75s.57-.69.75-1.15c.14-.35.3-.88.34-1.85.05-1.05.06-1.37.06-4.04s-.01-2.99-.06-4.04c-.04-.97-.2-1.5-.34-1.85a3.1 3.1 0 00-.75-1.15 3.1 3.1 0 00-1.15-.75c-.35-.14-.88-.3-1.85-.34-1.05-.05-1.37-.06-4.04-.06zm0 3.06a5.14 5.14 0 110 10.28 5.14 5.14 0 010-10.28zm0 1.8a3.34 3.34 0 100 6.68 3.34 3.34 0 000-6.68zm5.34-1.99a1.2 1.2 0 11-2.4 0 1.2 1.2 0 012.4 0z"/></svg>
      </a>
      <a href="{SITE['meta']['social']['linkedin']}" target="_blank" rel="noopener" aria-label="LinkedIn">
        <svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.03-1.85-3.03-1.85 0-2.14 1.45-2.14 2.94v5.66H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29zM5.34 7.43a2.07 2.07 0 110-4.13 2.07 2.07 0 010 4.13zM7.12 20.45H3.56V9h3.56v11.45z"/></svg>
      </a>
    </div>
  </div>
</footer>
<script src="/js/main.js"></script>
'''

PAGE_TMPL = '''<!DOCTYPE html>
<html lang="{lang}">
<head>
{head}
</head>
<body class="{body_cls}">
{header}
<main>
{content}
</main>
{footer}
</body>
</html>'''

def write_page(filename, title, content, desc=""):
    body_cls = "page-home" if filename == "index.html" else ""
    html_out = PAGE_TMPL.format(lang=LANG, head=base_head(filename, title, desc),
                                 body_cls=body_cls,
                                 header=header(filename=filename), content=content, footer=footer())
    out_dir = DIST if LANG == "pt" else os.path.join(DIST, "en")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, filename), "w", encoding="utf-8") as f:
        f.write(html_out)

def project_by_slug(slug):
    for p in PROJECTS:
        if p["slug"] == slug:
            return p
    return None

def project_thumb(p):
    cover = PROJECT_COVERS.get(p.get("slug"))
    if cover:
        return cover
    return p["images"][0] if p.get("images") else SITE['meta']['logo']

# ---------------- HOME ----------------
def build_home():
    h = SITE["home"]
    hero_bg = "e46b83_948ff9bdf490423eaf5301ead1312725~mv2.jpg"
    mission_bg = "e46b83_55e65d7ca94949a09af46888f42438d1~mv2.jpg"
    studio_photo = "e46b83_90dafd6a050f45f6adb7fb31cfdd2ec1~mv2.jpg"
    # Featured projects on the home page: the same 4 the original site shows
    # (noveme, o livro que não sabia o que queria ser, os infanticidas, onde
    # mora a minha irmã?), not an arbitrary pick.
    featured = [project_by_slug(s) for s in ("noveme", "olqnsoqqs", "o-pequeno-ego", "omami")]
    content = f'''
<section class="hero" style="background-image:url('/images/{webp_name(hero_bg)}')">
  <div class="hero-inner">
    {bi(h['pt']['hero_title'], h['en']['hero_title'], 'h1')}
    {bi(h['pt']['hero_sub'], h['en']['hero_sub'], 'p')}
  </div>
</section>

<section>
  <div class="container">
    {bi(h['pt']['projects_eyebrow'], h['en']['projects_eyebrow'], 'p', 'eyebrow')}
    {bi(h['pt']['projects_title'], h['en']['projects_title'], 'h2', 'section-title section-title--projects')}
    {bi(h['pt']['projects_sub'], h['en']['projects_sub'], 'p', 'section-sub')}
    <div class="divider"></div>
    {grid_markup(featured, 'grid--home')}
    <div class="center">
      <a class="cta-link" href="{url_for('portfolio.html')}">{bi(h['pt']['projects_cta'], h['en']['projects_cta'])}</a>
    </div>
  </div>
</section>

<section>
  <div class="container">
    {bi(h['pt']['what_eyebrow'], h['en']['what_eyebrow'], 'p', 'eyebrow')}
    {bi(h['pt']['what_title'], h['en']['what_title'], 'h2', 'section-title')}
    {bi(h['pt']['what_sub'], h['en']['what_sub'], 'p', 'section-sub')}
    <div class="divider"></div>
    <div class="services">
'''
    for i, s in enumerate(h['pt']['services']):
        s_en = h['en']['services'][i]
        content += f'''      <div class="service">
        <h3>{bi(s['name'], s_en['name'])}</h3>
        <p>{bi(s['text'], s_en['text'])}</p>
        <p class="tags">{bi(s['tags'], s_en['tags'])}</p>
      </div>
'''
    content += f'''    </div>
  </div>
</section>

<section class="mission" style="background-image:url('/images/{webp_name(mission_bg)}')">
  <div class="mission-inner">
    <p>{'<br>'.join(e(x) for x in L(MISSION_LINES_PT, MISSION_LINES_EN))}</p>
  </div>
</section>

<section>
  <div class="container split">
    <div>
      {img(studio_photo, alt='RIMA studio — Ricardo Esteves Corga e Marta Oliveira', eager=True)}
    </div>
    <div class="split-text">
      {bi(h['pt']['studio_eyebrow'], h['en']['studio_eyebrow'], 'p', 'eyebrow')}
      {bi_brand(h['pt']['studio_text'], h['en']['studio_text'], 'p')}
      <a class="cta-link" href="{url_for('oestudio.html')}">{bi(h['pt']['studio_cta'], h['en']['studio_cta'])}</a>
    </div>
  </div>
</section>

<section class="band-dark">
  <div class="container center">
    {bi(h['pt']['lab_eyebrow'], h['en']['lab_eyebrow'], 'p', 'eyebrow')}
    {bi(h['pt']['lab_title'], h['en']['lab_title'], 'h2', 'section-title')}
    <p style="max-width:620px;margin:0 auto;">{bi_brand(h['pt']['lab_text'], h['en']['lab_text'])}</p>
    <a class="cta-link" href="{SITE['meta']['external']['rimalab']}" target="_blank" rel="noopener">{bi(h['pt']['lab_cta'], h['en']['lab_cta'])}</a>
  </div>
</section>

<section class="band-taupe section-tight home-clients">
  <div class="container center">
    {bi(SITE['oestudio']['pt']['clients_eyebrow'], SITE['oestudio']['en']['clients_eyebrow'], 'p', 'eyebrow')}
{clients_section("", "")}  </div>
</section>
'''
    title = L("RIMA studio | Design, Ilustração e Animação | Cascais",
              "RIMA studio | Design, Illustration and Animation Studio | Cascais")
    desc = L("Design, ilustração e animação para empresas e projetos que valorizam ideias, autoria e uma abordagem próxima.",
             "Design, illustration and animation for companies and projects that value ideas, authorship and a personal approach.")
    write_page("index.html", title, content, desc=desc)

# ---------------- O ESTUDIO ----------------
STUDIO_BOLD = {
    "pt": ("design gráfico, ilustração e animação 2D", "Ricardo Esteves Corga", "Marta Oliveira"),
    "en": ("graphic design, illustration and 2D animation", "Ricardo Esteves Corga", "Marta Oliveira"),
}

def studio_para(i):
    """One paragraph of the studio text, with the same inline bold as the original."""
    o = SITE["oestudio"]
    txt = e(L(o["pt"]["paragraphs"][i], o["en"]["paragraphs"][i]))
    for b in BRAND_NAMES + STUDIO_BOLD[LANG]:
        txt = txt.replace(b, f"<strong>{b}</strong>")
    return txt

def studio_intro_paras():
    """Paragraph 0 is split in two (first sentence, then the rest), as in the original."""
    full = studio_para(0)
    cut = full.index(". ") + 1
    return full[:cut], full[cut:].strip()

def contact_form_html():
    key = SITE["meta"].get("web3forms_key", "")
    lab = {
        "name": L("Nome", "Name"), "surname": L("Apelido", "Last name"),
        "email": "Email", "subject": L("Assunto", "Subject"),
        "message": L("Mensagem", "Message"), "send": L("ENVIAR", "SEND"),
        "ok": L("Mensagem enviada. Obrigado, respondemos em breve.", "Message sent. Thank you, we will reply shortly."),
        "err": L("Não foi possível enviar. Escreva-nos para", "Could not send. Please write to us at"),
    }
    return f'''<form class="contact-form" id="contactForm" action="https://api.web3forms.com/submit" method="POST"
        data-key="{key}" data-ok="{e(lab["ok"])}" data-err="{e(lab["err"])}" data-email="{SITE["meta"]["email"]}">
    <input type="hidden" name="access_key" value="{key}">
    <input type="hidden" name="from_name" value="RIMA studio (rimastudio.pt)">
    <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">
    <div class="cf-left">
      <label>{lab["name"]} *<input type="text" name="name" required></label>
      <label>{lab["surname"]} *<input type="text" name="surname" required></label>
      <label>{lab["email"]} *<input type="email" name="email" required></label>
      <label>{lab["subject"]} *<input type="text" name="subject" required></label>
    </div>
    <label class="cf-right">{lab["message"]}<textarea name="message"></textarea></label>
    <button type="submit" class="cf-send">{lab["send"]}</button>
    <p class="cf-status" role="status" aria-live="polite"></p>
  </form>'''

def contact_modal_html():
    return f'''<div class="modal" id="contactModal" role="dialog" aria-modal="true" aria-label="{e(L('Contacto','Contact'))}" hidden>
  <div class="modal-box">
    <button class="modal-close" type="button" data-close-contact aria-label="{e(L('Fechar','Close'))}">&times;</button>
    <p class="studio-contact-lead"><strong>{e(L('Vamos criar algo para as suas pessoas?','Shall we create something for your people?'))}</strong><br>
    {e(L('Preencha o formulário ou escreva-nos para','Fill in the form or write to us at'))} <strong>{SITE["meta"]["email"]}</strong></p>
    {contact_form_html()}
  </div>
</div>'''

def build_oestudio():
    o = SITE["oestudio"]
    key = SITE["meta"].get("web3forms_key", "")
    first, rest = studio_intro_paras()
    hero_img = o["team_images"][0]
    portraits = [o["team_images"][1], o["studio_image"]]
    lab = {
        "name": L("Nome", "Name"), "surname": L("Apelido", "Last name"),
        "email": "Email", "subject": L("Assunto", "Subject"),
        "message": L("Mensagem", "Message"), "send": L("ENVIAR", "SEND"),
        "ok": L("Mensagem enviada. Obrigado, respondemos em breve.", "Message sent. Thank you, we will reply shortly."),
        "err": L("Não foi possível enviar. Escreva-nos para", "Could not send. Please write to us at"),
    }
    content = f'''
<div class="studio-hero" role="img" aria-label="RIMA studio" style="background-image:url('/images/{webp_name(hero_img)}')"></div>

<section class="studio-text">
  <p>{first}</p>
  <p>{rest}</p>
  <p>{studio_para(1)}</p>
</section>

<section class="studio-portraits">
  <div>{img(portraits[0], alt="Ricardo Esteves Corga", cls="pos-ricardo")}</div>
  <div>{img(portraits[1], alt="Marta Oliveira", cls="pos-marta")}</div>
</section>

<section class="studio-text">
  <p>{studio_para(2)}</p>
  <p>{studio_para(3)}</p>
  <p>{studio_para(4)}</p>
</section>

<section class="studio-contact" id="contacto">
  <h2 class="studio-title">{e(L(o["pt"]["contact_eyebrow"], o["en"]["contact_eyebrow"]))}</h2>
  <div class="divider divider--dark"></div>
  <p class="studio-contact-lead"><strong>{e(L(o["pt"]["contact_title"], o["en"]["contact_title"]))}</strong><br>
  {e(L("Preencha o formulário abaixo ou escreva-nos diretamente para", "Fill in the form below or write to us directly at"))} <strong>{SITE["meta"]["email"]}</strong></p>
  {contact_form_html()}
</section>

<section class="map-band">
  <div class="map-duotone">
    <iframe src="https://www.google.com/maps?q=RIMA+studio,R.+Moinho+Vermelho+638,2645-449+Alcabideche&output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="{e(L('Localização RIMA studio','RIMA studio location'))}"></iframe>
  </div>
</section>

<section class="band-taupe">
  <h2 class="studio-title studio-title--light">{e(L(o["pt"]["clients_eyebrow"], o["en"]["clients_eyebrow"]))}</h2>
  <div class="divider divider--light"></div>
  <p class="studio-clients-text">{bi_brand(o["pt"]["clients_text"], o["en"]["clients_text"])}</p>
{clients_section("", "")}
</section>
'''
    title = L("O Estúdio | RIMA studio, Cascais", "The Studio | RIMA studio, Cascais")
    desc = L("O RIMA studio é um estúdio criativo dedicado à comunicação visual para marcas e instituições.",
             "RIMA studio is a creative studio dedicated to visual communication for brands and institutions.")
    write_page("oestudio.html", title, content, desc=desc)

# ---------------- PORTFOLIO + FILTERS ----------------
FILTER_TITLES = {
    None:       ("PORTFÓLIO", "WORK | Graphic Design, Illustration and Animation Projects"),
    "design":   ("Design", "Design"),
    "animacao": ("Animação", "Animation"),
    "ilustracao": ("Ilustração", "Illustration"),
}

def build_portfolio(category=None, filename="portfolio.html"):
    h = SITE["home"]
    ordered = sorted(PROJECTS, key=lambda p: PORTFOLIO_ORDER.index(p["slug"]) if p["slug"] in PORTFOLIO_ORDER else 999)
    items = ordered if category is None else [p for p in ordered if category in p["categories"]]
    content = f'''
<section class="section-tight">
  <div class="container">
    {bi(h['pt']['projects_eyebrow'], h['en']['projects_eyebrow'], 'p', 'eyebrow')}
    {bi(h['pt']['projects_title'], h['en']['projects_title'], 'h2', 'section-title')}
    <div class="filter-tabs">
      <a href="{url_for('portfolio.html')}" class="{'active' if category is None else ''}">{e(L('TODOS','ALL'))}</a>
      <a href="{url_for('design.html')}" class="{'active' if category=='design' else ''}">{e(L('#design','#design'))}</a>
      <a href="{url_for('animacao.html')}" class="{'active' if category=='animacao' else ''}">{e(L('#animação','#animation'))}</a>
      <a href="{url_for('ilustracao.html')}" class="{'active' if category=='ilustracao' else ''}">{e(L('#ilustração','#illustration'))}</a>
    </div>
    <div class="divider"></div>
    {grid_markup(items)}
  </div>
</section>
'''
    title_pt, title_en = FILTER_TITLES[category]
    title = f"{L(title_pt, title_en)} | RIMA studio"
    write_page(filename, title, content)

# ---------------- PROJECT PAGES ----------------
# Per-project "+ INFO" lines (label PT, label EN, href or None) and inline links,
# copied from the original Wix project pages.
INFO_LINES = {
    "casa-del-yoga": [("www.casadelyoga.com", None, "http://www.casadelyoga.com"), ("@casadelyoga", None, "http://www.instagram.com/casadelyoga")],
    "noveme": [("www.noveme.co.uk", None, "http://www.noveme.co.uk")],
    "the-bear-collection": [("Post Instagram Parfois - The Bear Collection", None, "https://www.instagram.com/p/DSR29grjFwA/?img_index=1")],
    "dahu-shoes-off": [("www.dahu.pt", None, "http://www.dahu.pt"), ("@dahu.som", None, "http://www.instagram.com/dahu.som")],
    "kc-the-brand": [("www.kcthebrand.com", None, "http://www.kcthebrand.com")],
    "troglodicas": [("www.mocedumcabreste.pt", None, "http://www.mocedumcabreste.pt"), ("@mocedumcabreste", None, "http://www.instagram.com/mocedumcabreste")],
    "o-protesto-do-lobo-mau": [("www.pingodoce.pt/premio-literatura-infantil/", None, "http://www.pingodoce.pt/premio-literatura-infantil")],
    "talismas": [("edição limitada esgotada", "limited edition - sold out", None)],
    "omami": [("livro disponível para compra em eraumaines.pt", "book available for purchase at eraumaines.pt", "https://eraumaines.pt/")],
    "videoclip-linho": [("www.katerinaldokova.com", None, "https://katerinaldokova.com/")],
    "mil-jewellery": [("www.miljewellery.com", None, "http://www.miljewellery.com"), ("@miljewellery", None, "http://www.instagram.com/miljewellery")],
    "padrao-byou": [("Arua | tiger dress", None, "https://byoubb.com/collections/africa-ss20/products/9776"), ("Gaya | tiger set", None, "https://byoubb.com/collections/africa-ss20/products/9767-tiger-ensemble")],
    "de-la-espada-lookbook": [("DLE Lookbook IV", None, "https://delaespada.com/pages/look-book-volume-4")],
    "o-pequeno-ego": [("IMDB \"Os Infanticidas\"", None, "https://www.imdb.com/pt/title/tt35636226/")],
}
# Words inside a paragraph that are links on the original page: (paragraph index, word, href)
TEXT_LINKS = {"padrao-byou": [(0, "BYOU", "https://byoubb.com/")]}

# Hosted videos (Wix video CDN ids). poster = same-order images of the project.
VIDEOS = {
    "the-bear-collection": dict(q="720p", ids=[
        "e46b83_c0827596dff64df6b2a2bf29d78f4347", "e46b83_68b2014ca37945b4a469048977707af9",
        "e46b83_2edfc12a58ac4d8aba1c084cab6889b6", "e46b83_fa35e3bf7efd485ba83d10d26f56df1d",
        "e46b83_cc364211fa874099a573f8c0ea3c50cf"],
        names=["SKI", "NERD", "NATALICIO", "INFLUENCER", "DORMINHOCO"],
        files=["ski", "nerd", "natalicio", "influencer", "dorminhoco"]),
    "talismas": dict(q="480p", ids=[
        "e46b83_ecd5ac0185b5478ab0757ccd9313268e", "e46b83_bd1963559c29445c97aeba6612b14326"],
        names=["Talismãs 1", "Talismãs 2"], files=["talismas-1", "talismas-2"]),
}

def _video_tag(slug, n, poster, ratio_cls=""):
    v = VIDEOS[slug]
    local = v["files"][n]
    if os.path.exists(os.path.join(ROOT, "videos", local + ".mp4")):
        src = f"/videos/{local}.mp4"  # self-hosted copy
    else:
        src = f"https://video.wixstatic.com/video/{v['ids'][n]}/{v['q']}/mp4/file.mp4"  # fallback until the file is added
    label = L("Reproduzir vídeo", "Play video")
    return (f'<div class="pj-video {ratio_cls}"><video preload="none" playsinline controlslist="nodownload" '
            f'poster="/images/{webp_name(poster)}" src="{src}" title="{html.escape(v["names"][n])}"></video>'
            f'<button type="button" class="pj-play" aria-label="{label}"></button></div>')

def _info_html(slug):
    lines = INFO_LINES.get(slug)
    if not lines:
        return ""
    rows = ""
    for pt, en, href in lines:
        txt = e(L(pt, en or pt))
        if href:
            txt = f'<a href="{href}" target="_blank" rel="noopener">{txt}</a>'
        rows += f'<p class="pj-info-line">{txt}</p>'
    return f'<div class="pj-info"><p class="pj-info-label">+ INFO</p>{rows}</div>'

def _gallery_html(p, blocks):
    slug = p["slug"]
    title = L(p.get("title", slug), p.get("title_en", p.get("title", slug)))
    out = ""
    def im(f, cls=""):
        return img(f, cls=cls, alt=title) if f else ""
    for b in blocks[1:]:
        t = b["t"]
        g = 68 if b.get("gap", 15) > 30 else 15  # uniform section spacing
        out += f'<div class="pj-gap" style="height:{g - 30}px"></div>' if g > 30 else ""
        if t == "strip":
            out += f'<div class="pj-row pj-strip">{im(b["img"])}</div>'
        elif t == "img":
            if not b["img"]:
                continue  # image not available locally (see report)
            w, h = b["ratio"]
            cls = "pj-img pj-img--b" if h in (732, 733) else "pj-img"
            out += f'<div class="{cls}" style="--ar:{w}/{h}">{im(b["img"])}</div>'
        elif t == "mosaic":
            big = f'<div class="pj-sq">{im(b["big"])}</div>'
            col = "".join(f'<div class="pj-sq">{im(b[k])}</div>' for k in ("s1", "s2") if b.get(k))
            col = f'<div class="pj-col">{col}</div>' if col else ""
            cls = "pj-mosaic" + (" pj-mosaic--rev" if b.get("rev") else "") + ("" if col else " pj-mosaic--solo")
            out += f'<div class="{cls}">{col + big if b.get("rev") else big + col}</div>'
        elif t == "small":
            out += f'<div class="pj-mosaic pj-mosaic--solo pj-mosaic--small"><div class="pj-sq">{im(b["img"])}</div></div>'
        elif t == "yt":
            vid = p.get("youtube_id")
            if vid:
                w, h = b["ratio"]
                out += (f'<div class="pj-yt" style="--ar:{w}/{h}"><iframe src="https://www.youtube-nocookie.com/embed/{vid}" '
                        f'title="{html.escape(title)}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
                        f'allowfullscreen loading="lazy"></iframe></div>')
        elif t == "carousel":
            v = VIDEOS[slug]
            tags = "".join(_video_tag(slug, n, "bear-" + f) for n, f in enumerate(v["files"]))
            out += f'<div class="pj-videos pj-videos--5">{tags}</div>'
        elif t == "videos":
            posters = [f for f in p["images"] if f not in {x.get("img") for x in blocks if x.get("img")}]
            out += '<div class="pj-videos">' + "".join(_video_tag(slug, n, f) for n, f in enumerate(posters[:2])) + '</div>'
    return out

def _curly(t):
    """Typographic double quotes, as on the original Wix pages."""
    t = re.sub(r'(^|[\s(\[])"', lambda m: m.group(1) + "\u201c", t)
    return t.replace('"', "\u201d")

def build_project(p, idx):
    slug = p["slug"]
    tags_pt = p.get("tags_pt", "")
    tags_en = p.get("tags_en", "")
    title = p.get("title", slug)
    title_en = p.get("title_en", title)
    blocks = LAYOUTS[slug]
    cover = blocks[0]

    paras = ""
    links = TEXT_LINKS.get(slug, [])
    for i, t in enumerate(p.get("text_pt", [])):
        en_t = p.get("text_en", [""] * len(p["text_pt"]))[i] if i < len(p.get("text_en", [])) else ""
        txt = e(_curly(L(t, en_t)))
        for (pi, word, href) in links:
            if pi == i:
                txt = txt.replace(word, f'<a href="{href}" target="_blank" rel="noopener">{word}</a>', 1)
        paras += f"<p>{txt}</p>\n"
    if p.get("credit"):
        paras += f'<p>{e(p["credit"])}</p>\n'

    prev_p = PROJECTS[idx-1] if idx > 0 else PROJECTS[-1]
    next_p = PROJECTS[idx+1] if idx < len(PROJECTS)-1 else PROJECTS[0]
    ar_w, ar_h = cover["ratio"]
    content = f'''
<section class="pj-cover" style="--ar:{ar_w}/{ar_h}">{img(cover["img"], alt=L(title, title_en), eager=True)}</section>
<section class="pj-head">
  <h1 class="pj-title">{e(L(title, title_en))}</h1>
  <p class="pj-tags">{e(L(tags_pt, tags_en))}</p>
  <span class="pj-line" aria-hidden="true"></span>
</section>
<section class="pj-text">
{paras}{_info_html(slug)}</section>
<section class="pj-gallery">{_gallery_html(p, blocks)}</section>
<nav class="pj-nav-links" aria-label="{L("Outros projetos", "Other projects")}">
  <a href="{url_for(prev_p['slug'] + '.html')}">&larr; {e(L(prev_p['title'], prev_p.get('title_en', prev_p['title'])))}</a>
  <a href="{url_for(next_p['slug'] + '.html')}">{e(L(next_p['title'], next_p.get('title_en', next_p['title'])))} &rarr;</a>
</nav>
'''
    page_title = f"{L(title, title_en)} | RIMA studio"
    desc_pt = (p.get("text_pt") or [""])[0][:160]
    desc_en = (p.get("text_en") or [desc_pt])[0][:160]
    write_page(f"{p['slug']}.html", page_title, content, desc=L(desc_pt, desc_en))


# ---------------- THE PEOPLE SERIES (draft page) ----------------
def ph(label_pt, label_en, ratio="4/3", cls=""):
    """Visible placeholder for a photo still to be produced (draft only)."""
    return f'<div class="ph {cls}" style="aspect-ratio:{ratio}"><span>{e(L(label_pt, label_en))}</span></div>'

def ul(items_pt, items_en):
    return "<ul class=\"tps-list\">" + "".join(f"<li>{e(x)}</li>" for x in L(items_pt, items_en)) + "</ul>"

TL_SVG = {
    "preview": '<svg viewBox="0 0 100 125" fill="none" stroke="#1a1a1a" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="15" y="30" width="70" height="48" rx="2"/><path d="M50 78v14M36 92h28"/><circle cx="50" cy="47" r="7"/><path d="M36 74q14-20 28 0"/></svg>',
    "print": '<svg viewBox="0 0 100 125" fill="none" stroke="#1a1a1a" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="28" y="25" width="44" height="62"/><circle cx="50" cy="47" r="6"/><path d="M38 76q12-18 24 0"/><path d="M20 20h6M20 20v6M80 20h-6M80 20v6M20 92h6M20 92v-6M80 92h-6M80 92v-6"/></svg>',
    "frame": '<svg viewBox="0 0 100 125" fill="none" stroke="#1a1a1a" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="22" y="22" width="56" height="76"/><rect x="30" y="30" width="40" height="60"/><circle cx="50" cy="52" r="6"/><path d="M40 82q10-18 20 0"/><path d="M32 98l-6 8h48l-6-8"/></svg>',
    "box": '<svg viewBox="0 0 100 125" fill="none" stroke="#1a1a1a" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="22" y="50" width="56" height="42"/><rect x="18" y="38" width="64" height="12"/><path d="M50 38v54"/><rect x="58" y="66" width="14" height="10"/></svg>',
}

def timeline_html():
    steps = [
        ("img", "tps-ref-mulher", L("Referência", "Reference")),
        ("img", "tps-traco-mulher", L("Desenho", "Drawing")),
        ("img", "tps-tl-preview", "Preview"),
        ("img", "tps-tl-impressao", L("Impressão", "Print")),
        ("img", "tps-tl-moldura", L("Moldura", "Frame")),
        ("img", "tps-tl-caixa", L("Caixa", "Box")),
    ]
    items = ""
    for i, (kind, ref, label) in enumerate(steps, 1):
        vis = img(ref, alt="", cls="tps-tl-img") if kind == "img" else TL_SVG[ref]
        items += f'<li><div class="tps-tl-visual tps-tl-{kind}">{vis}</div><span class="tps-tl-label"><b>{i:02d}</b> {e(label)}</span></li>'
    return f'<ol class="tps-timeline">{items}</ol>'

def build_people_series():
    mail = "hello@rimastudio.pt"
    contact = url_for("oestudio.html") + "#contacto"
    steps = L([
        ("Briefing", "Percebemos o contexto da iniciativa, número de colaboradores, ocasião, timing e nível de personalização pretendido."),
        ("Referências", "A empresa fornece, idealmente, pelo menos duas referências atuais de cada pessoa."),
        ("Direção visual", "A RIMA studio propõe a abordagem de ilustração que considera mais adequada ao projeto. O cliente pode optar entre Traço, Forma ou Textura, sem alteração de valor."),
        ("Ilustração", "Cada retrato é desenvolvido individualmente pela equipa RIMA."),
        ("Preview", "Antes da produção física, enviamos sempre um preview digital para aprovação. Está incluída uma ronda de pequenos ajustes."),
        ("Produção", "Depois da aprovação, cada retrato é preparado, impresso e finalizado."),
        ("Entrega", "As peças podem ser entregues apenas impressas ou já emolduradas e prontas a oferecer. O ficheiro digital em .jpg é sempre incluído."),
    ], [
        ("Brief", "We understand the context of the initiative, number of employees, occasion, timing and level of customisation required."),
        ("References", "The company provides, ideally, at least two recent references of each person."),
        ("Visual direction", "RIMA studio proposes the illustration approach we believe best fits the project. The client may choose between Line, Form or Texture, with no price difference between styles."),
        ("Illustration", "Each portrait is developed individually by the RIMA team."),
        ("Preview", "Before physical production, we always send a digital preview for approval. One round of minor adjustments is included."),
        ("Production", "After approval, each portrait is prepared, printed and finished."),
        ("Delivery", "The pieces can be delivered as prints only or framed and ready to give. A high-resolution .jpg file is always included."),
    ])
    steps_html = "".join(
        f'<li><span class="tps-num">{i+1:02d}</span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>'
        for i, (t, d) in enumerate(steps))

    styles = L([
        ("Traço", "A abordagem mais simples e essencial.",
         "O retrato é construído sobretudo através da linha, com uma utilização muito contida da cor. A imagem é reduzida aos elementos necessários para preservar a expressão, a postura e os traços mais reconhecíveis de cada pessoa.",
         "O resultado é leve, limpo e intemporal, mantendo uma forte ligação à fotografia de referência sem perder o carácter ilustrado."),
        ("Forma", "Uma abordagem mais construída, em que ao traço se juntam manchas de cor, sombras suaves e elementos de fundo.",
         "Estas camadas acrescentam maior definição e presença ao retrato, criando uma imagem visualmente mais preenchida sem perder a simplicidade e a clareza do desenho.",
         "O resultado mantém-se contemporâneo e equilibrado, com uma leitura mais gráfica e uma maior sensação de profundidade."),
        ("Textura", "A abordagem mais expressiva e rica visualmente.",
         "Ao traço juntam-se diferentes camadas de cor, hachuras, manchas, sobreposições e texturas, criando uma imagem com maior densidade gráfica e um carácter mais editorial.",
         "O retrato mantém a identidade e os traços essenciais da pessoa, mas permite uma interpretação visual mais livre, dinâmica e autoral."),
    ], [
        ("Line", "The simplest and most essential approach.",
         "The portrait is built mainly through line, with a very restrained use of colour. The image is reduced to the elements needed to preserve the expression, posture and most recognisable features of each person.",
         "The result is light, clean and timeless, maintaining a strong connection to the reference while still feeling clearly illustrated."),
        ("Form", "A more constructed approach, where line is complemented by areas of colour, soft shadows and background elements.",
         "These layers add definition and presence to the portrait, creating a fuller image while preserving the simplicity and clarity of the drawing.",
         "The result remains contemporary and balanced, with a more graphic reading and a stronger sense of depth."),
        ("Texture", "The most expressive and visually rich approach.",
         "Line is layered with colour, hatching, marks, overlays and textures, creating a portrait with greater graphic density and a more editorial character.",
         "The portrait still preserves the identity and essential features of the person, while allowing for a freer, more dynamic and author-led interpretation."),
    ])
    styles_html = ""
    for t, lead, p1, p2 in styles:
        slug = {"Traço": "traco", "Line": "traco", "Forma": "forma", "Form": "forma", "Textura": "textura", "Texture": "textura"}[t]
        alts = {"homem": L("retrato de homem", "portrait of a man"), "mulher": L("retrato de mulher", "portrait of a woman"), "grupo": L("retrato de grupo", "group portrait")}
        shots = "".join(img(f"tps-{slug}-{w}", cls=f"tps-{w}", alt=f"The People Series — {t}: {alts[w]}") for w in ("homem", "mulher", "grupo"))
        styles_html += f'''
<section class="tps-style">
  <div class="container">
    <div class="tps-style-text">
      <h3>{e(t)}</h3>
      <p class="tps-lead">{e(lead)}</p>
      <p>{e(p1)}</p>
      <p>{e(p2)}</p>
    </div>
    <div class="tps-trio">{shots}</div>
  </div>
</section>'''

    faq = L([
        ("Quantas fotografias são necessárias?", "Idealmente, pelo menos duas referências atuais de cada pessoa."),
        ("As fotografias têm de ser profissionais?", "Não. Fotografias informais podem funcionar perfeitamente, desde que permitam ver bem a pessoa."),
        ("Podem trabalhar a partir de vídeo?", "Sim. Frames de vídeo podem ser utilizados como referência quando mostram bem a pessoa."),
        ("O cliente escolhe o estilo?", "A RIMA studio propõe a abordagem que considera mais adequada ao projeto, mas o cliente pode optar entre Traço, Forma ou Textura. O estilo não altera o valor."),
        ("Existe aprovação antes da impressão?", "Sim. Enviamos sempre um preview digital antes da produção física."),
        ("Estão incluídas alterações?", "Está incluída uma ronda de pequenos ajustes. Alterações estruturais, mudança de referência, pose ou abordagem depois de iniciado o desenho podem implicar orçamento adicional."),
        ("Qual é o formato?", "O formato standard é A5. Formatos superiores estão disponíveis mediante pedido."),
        ("A moldura está incluída?", "Existem duas opções: ilustração impressa ou ilustração emoldurada."),
        ("O ficheiro digital está incluído?", "Sim. É sempre entregue um ficheiro .jpg de alta resolução."),
        ("Podem personalizar a embalagem?", "Sim. A versão standard utiliza a identidade The People Series / RIMA studio, mas podemos adaptar elementos à identidade da empresa."),
        ("Existe quantidade mínima?", "Não existe quantidade mínima pública. O serviço pode ser desenvolvido para uma única pessoa ou para séries maiores."),
        ("Podem criar programas anuais?", "Sim. O serviço adapta-se particularmente bem a programas recorrentes de reconhecimento, como 5, 10, 15 ou mais anos de casa."),
        ("Trabalham fora de Lisboa?", "Sim. Projetos fora da região de Lisboa/Cascais e envios nacionais ou internacionais são avaliados caso a caso."),
    ], [
        ("How many photographs are needed?", "Ideally, at least two recent references of each person."),
        ("Do the photographs need to be professional?", "No. Informal photographs can work perfectly well, as long as the person can be seen clearly."),
        ("Can you work from video?", "Yes. Video frames can be used as references when they show the person clearly."),
        ("Does the client choose the style?", "RIMA studio proposes the approach we believe best fits the project, but the client can choose between Line, Form or Texture. The style does not affect the price."),
        ("Is there an approval stage before printing?", "Yes. We always send a digital preview before physical production."),
        ("Are revisions included?", "One round of minor adjustments is included. Structural changes, a new reference, pose or illustration approach after work has started may require an additional quote."),
        ("What is the standard format?", "The standard format is A5. Larger formats are available upon request."),
        ("Is the frame included?", "There are two options: printed illustration or framed illustration."),
        ("Is the digital file included?", "Yes. A high-resolution .jpg file is always included."),
        ("Can the packaging be customised?", "Yes. The standard version uses The People Series / RIMA studio identity, but selected elements can be adapted to the company's identity."),
        ("Is there a minimum quantity?", "There is no public minimum quantity. The service can be developed for one person or for larger series."),
        ("Can this be an annual programme?", "Yes. The service is particularly suited to recurring recognition programmes such as 5, 10, 15 or more years of service."),
        ("Do you work outside Lisbon?", "Yes. Projects outside Lisbon/Cascais and national or international shipping are evaluated case by case."),
    ])
    faq_html = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faq)

    GRUNENTHAL_APPROVED = False  # set True only after Grünenthal's written validation (hides the draft banner)
    gr_blocks = L([
        ("Seis anos a celebrar pessoas através da ilustração", [
            "Durante seis anos consecutivos, o RIMA studio colaborou com a Grünenthal num projeto de reconhecimento de colaboradores integrado nas celebrações do aniversário da empresa.",
            "Todos os anos, a empresa distinguia colaboradores que atingiam marcos importantes de antiguidade, como 5, 10, 15 ou mais anos de casa, através de uma oferta personalizada entregue durante o evento anual.",
            "Ao longo destes seis anos, desenvolvemos aproximadamente 50 retratos ilustrados, criados individualmente para cada pessoa homenageada."]),
        ("Um presente pensado para cada pessoa", [
            "O departamento de Recursos Humanos selecionava os colaboradores a reconhecer e partilhava connosco as respetivas referências.",
            "A partir dessas imagens, cada retrato era desenvolvido individualmente pela equipa RIMA, procurando preservar os traços, a expressão e a identidade de cada pessoa.",
            "Depois de aprovado, o retrato era impresso, emoldurado e preparado numa caixa identificada, acompanhado por uma mensagem da própria empresa dirigida ao colaborador."]),
        ("Uma iniciativa que se tornou recorrente", [
            "O que começou como uma encomenda pontual tornou-se um projeto renovado ao longo de seis anos consecutivos.",
            "Essa continuidade permitiu acompanhar diferentes grupos de colaboradores ao longo do tempo e mostrou-nos o valor que uma peça verdadeiramente pessoal pode ter dentro de uma iniciativa de reconhecimento.",
            "Foi também esta experiência que ajudou a consolidar aquilo que hoje apresentamos como The People Series."]),
    ], [
        ("Six years celebrating people through illustration", [
            "For six consecutive years, RIMA studio collaborated with Grünenthal on an employee recognition project integrated into the company's anniversary celebrations.",
            "Each year, the company recognised employees reaching important service milestones, such as 5, 10, 15 or more years with the company, through a personalised gift presented during the annual event.",
            "Across these six years, we created approximately 50 illustrated portraits, individually developed for each person being recognised."]),
        ("A gift made for each person", [
            "The Human Resources department selected the employees to be recognised and shared the relevant references with us.",
            "Using those images, each portrait was developed individually by the RIMA team, with particular attention to the person's features, expression and identity.",
            "After approval, the portrait was printed, framed and prepared in an identified box, together with a message from the company addressed to the employee."]),
        ("A project that became recurring", [
            "What started as an individual commission became a project renewed over six consecutive years.",
            "That continuity allowed us to follow different groups of employees over time and showed us the value that a truly personal piece can bring to an employee recognition initiative.",
            "It was also this experience that helped consolidate what we now present as The People Series."]),
    ])
    gr_stats = L([("6 anos", "de colaboração continuada"), ("≈ 50 retratos", "criados individualmente"), ("5, 10, 15+ anos", "de percurso reconhecido")],
                 [("6 years", "of continued collaboration"), ("≈ 50 portraits", "individually created"), ("5, 10, 15+ years", "of service recognised")])
    gr_title = L("Seis anos a celebrar pessoas através da ilustração", "Six years celebrating people through illustration")
    gr_text = "".join(f'<div class="tps-gr-block"><h3>{e(h)}</h3>' + "".join(f"<p>{e(x)}</p>" for x in ps) + "</div>" for (h, ps) in gr_blocks[1:])
    gr_first = "".join(f"<p>{e(x)}</p>" for x in gr_blocks[0][1])
    gr_stats_html = "".join(f'<div><strong>{e(a)}</strong><span>{e(b)}</span></div>' for a, b in gr_stats)
    gr_banner = "" if GRUNENTHAL_APPROVED else f'''<p class="tps-draft">{e(L("[Rascunho para validação da Grünenthal. Esta é a extensão total da referência à Grünenthal que pretendemos publicar no site do RIMA studio. Não está prevista publicidade paga nem conteúdo promocional isolado com o nome da Grünenthal ou dos seus colaboradores. O material visual será escolhido para mostrar o projeto como um todo e não colaboradores individuais. O logótipo só se mantém se for autorizado.]", "[Draft for Grünenthal validation. This is the full extent of the Grünenthal reference we intend to publish on the RIMA studio website. No paid advertising or standalone promotional content featuring the Grünenthal name or employees is planned. Any visual material used will be selected to show the project as a whole rather than individual employees. The logo stays only if authorised.]"))}</p>'''
    case_html = f'''
<section class="tps-section tps-case" id="case-study">
  <div class="container">
    {gr_banner}
    <p class="eyebrow tps-h-center">Case study</p>
    <div class="tps-gr-head">{img("tps-grunenthal-logo", cls="tps-gr-logo", alt="Grünenthal")}</div>
    <h2 class="tps-h-center tps-gr-title">{e(gr_title)}</h2>
    <div class="tps-narrow tps-gr-first">{gr_first}</div>
    <div class="tps-gr-stats">{gr_stats_html}</div>
    <div class="tps-gr-cols">{gr_text}</div>
  </div>
</section>
'''

    content = f'''
<section class="tps-hero">
  <div class="container">
    <p class="eyebrow">THE PEOPLE SERIES</p>
    <h1>Recognition, made personal.</h1>
    <p class="tps-sub">{e(L("Ilustrações de autor criadas para celebrar as pessoas por detrás de uma empresa.", "Author illustrations created to celebrate the people behind a company."))}</p>
    <div class="tps-ctas">
      <button type="button" class="cta-link" data-open-contact>{e(L("Falar connosco", "Get in touch"))}</button>
      <a class="cta-link cta-link--outline" href="#como-funciona">{e(L("Ver como funciona", "See how it works"))}</a>
    </div>
    {ph("Hero: retrato A5 emoldurado + caixa aberta (ou vídeo em loop 15–25 s)", "Hero: framed A5 portrait + open box (or 15–25 s loop video)", "16/9", "ph--wide")}
  </div>
</section>

<section class="tps-section">
  <div class="container tps-narrow">
    <h2>{e(L("Uma forma mais pessoal de reconhecer", "A more personal form of recognition"))}</h2>
    <p>{e(L("Uma empresa é feita de muitas coisas, mas sobretudo das pessoas que a constroem todos os dias.", "A company is made of many things, but above all, of the people who build it every day."))}</p>
    <p>{e(L("The People Series nasce como uma forma mais pessoal e artística de reconhecer essas pessoas. Um serviço de retratos ilustrados de autor pensado para empresas que valorizam os seus colaboradores e procuram assinalar momentos importantes de uma forma menos convencional e mais significativa.", "The People Series was created as a more personal and artistic way to recognise those people. An author illustration service for companies that value their employees and want to mark meaningful moments in a less conventional, more thoughtful way."))}</p>
    <p>{e(L("Mais do que reproduzir uma fotografia, procuramos transformar cada pessoa numa peça única, pensada para ser oferecida, guardada e associada a um momento de reconhecimento.", "Rather than simply reproducing a photograph, we turn each person into a unique piece designed to be given, kept and associated with a moment of recognition."))}</p>
  </div>
  <div class="container">{img("tps-intro", cls="tps-intro", alt=L("Retratos ilustrados emoldurados, lado a lado numa mesa", "Framed illustrated portraits side by side on a table"))}</div>
</section>

<section class="tps-section tps-tint">
  <div class="container tps-narrow">
    <h2>{e(L("Pensado para momentos com significado", "Made for meaningful moments"))}</h2>
    <p>{e(L("The People Series pode ser integrado em diferentes momentos de reconhecimento dentro de uma empresa:", "The People Series can be part of different moments of recognition within a company:"))}</p>
    {ul(["Anos de casa / work anniversaries", "5, 10, 15, 20 ou mais anos na empresa", "Reforma", "Saída de um colaborador", "Reconhecimento de uma contribuição ou conquista", "Prémios internos", "Aniversários da empresa", "Celebrações de equipa", "Programas anuais de employee recognition"],
        ["Work anniversaries", "5, 10, 15, 20 or more years with the company", "Retirement", "Employee departures", "Recognition of a contribution or achievement", "Internal awards", "Company anniversaries", "Team celebrations", "Annual employee recognition programmes"])}
    <p>{e(L("Pode funcionar como uma iniciativa pontual ou como um programa recorrente ao longo dos anos.", "It can work as a one-off initiative or as an ongoing recognition programme over the years."))}</p>
  </div>
</section>

<section class="tps-section">
  <div class="container tps-split">
    <div>{img("tps-equipa", cls="tps-team", alt=L("Marta e Ricardo no RIMA studio, a rever ilustrações impressas", "Marta and Ricardo at RIMA studio, reviewing printed illustrations"))}</div>
    <div class="tps-narrow">
      <h2>{e(L("Criado pela equipa RIMA studio", "Created by RIMA studio"))}</h2>
      <p>{e(L("Cada retrato é desenvolvido pela equipa do RIMA studio, Marta e Ricardo, a partir de fotografias e outras referências da pessoa retratada.", "Each portrait is developed by the RIMA studio team, Marta and Ricardo, using photographs and other visual references of the person being portrayed."))}</p>
      <p>{e(L("O trabalho parte sempre de uma linguagem de ilustração autoral, contemporânea e humana, mas é pensado especificamente para cada projeto.", "The work always starts from an author-led, contemporary and human illustration language, while being adapted to the specific context of each project."))}</p>
      <p>{e(L("Mais do que reproduzir uma imagem, cruzamos referências para perceber melhor a expressão, os traços e a presença de cada pessoa.", "Rather than simply reproducing one image, we cross-reference different materials to better understand each person's expression, features and presence."))}</p>
    </div>
  </div>
</section>

<section class="tps-section tps-center">
  <div class="container tps-narrow">
    <h2>{e(L("Um conceito, diferentes abordagens", "One concept, different approaches"))}</h2>
    <p>{e(L("Cada projeto pode assumir uma linguagem visual diferente, mantendo sempre a identidade do The People Series e o carácter autoral da ilustração.", "Each project can take on a different visual language while keeping the identity of The People Series and the author-led nature of the illustration."))}</p>
    <p>{e(L("As três abordagens distinguem-se sobretudo pela forma como trabalham o traço, a cor, a sombra e a textura, permitindo adaptar o resultado ao contexto, à dimensão do projeto e à identidade de cada empresa.", "The three approaches differ mainly in the way they use line, colour, shadow and texture, allowing the result to adapt to the context, scale and identity of each company."))}</p>
    <p>{e(L("Nenhuma é apresentada como superior às restantes. São diferentes formas de interpretar o mesmo princípio: criar retratos reconhecíveis, pessoais e com valor para quem os recebe.", "None is presented as superior to the others. They are simply different ways of interpreting the same principle: creating recognisable, personal portraits with meaning for the person receiving them."))}</p>
  </div>
</section>
{styles_html}

<section class="tps-cta-mid">
  <div class="container">
    <p>{e(L("Quer ver como ficaria na sua empresa?", "Want to see how it would work for your company?"))}</p>
    <button type="button" class="cta-link" data-open-contact>{e(L("Falar connosco", "Talk to us"))}</button>
  </div>
</section>


<section class="tps-section tps-tint">
  <div class="container tps-narrow">
    <h2>{e(L("Trabalhamos a partir de referências", "We work from references"))}</h2>
    <p>{e(L("Idealmente, pedimos pelo menos duas referências atuais de cada pessoa.", "Ideally, we ask for at least two recent references of each person."))}</p>
    <p>{e(L("Podem ser fotografias profissionais ou informais. Não precisam de ter sido produzidas especificamente para o projeto. Também podemos trabalhar a partir de vídeo, desde que permita ver bem a pessoa.", "They can be professional or informal photographs and do not need to have been produced specifically for the project. We can also work from video, as long as the person can be seen clearly."))}</p>
    <p>{e(L("A equipa RIMA cruza as diferentes referências para perceber melhor os traços, a expressão e a presença de cada colaborador, sem ficar dependente de uma única fotografia.", "The RIMA team cross-references the available material to better understand each employee's features, expression and presence, rather than relying on a single photograph."))}</p>
  </div>
  <div class="container tps-refs">
    <div class="tps-refs-photos">
      {"".join(f'<figure>{img(f"tps-ref-{w}", alt=L("Fotografia de referência", "Reference photograph") + " — " + lbl)}<figcaption>{e(L("Referência", "Reference"))} · {e(lbl)}</figcaption></figure>' for w, lbl in (("homem", L("Homem", "Man")), ("mulher", L("Mulher", "Woman")), ("grupo", L("Grupo", "Group"))))}
    </div>
    <p class="tps-note tps-refs-note">{e(L("Fotografias de referência meramente ilustrativas, geradas por IA. Não correspondem a pessoas reais. Todos os retratos The People Series são desenhados pela equipa RIMA studio.", "Reference photographs shown are illustrative only and were generated with AI. They do not depict real people. All The People Series portraits are drawn by the RIMA studio team."))}</p>
  </div>
</section>

<section class="tps-section" id="como-funciona">
  <div class="container">
    <h2 class="tps-h-center">{e(L("Como funciona", "How it works"))}</h2>
    <ol class="tps-steps">{steps_html}</ol>
    {timeline_html()}
  </div>
</section>

<section class="tps-section tps-tint">
  <div class="container tps-split">
    <div class="tps-narrow">
      <h2>{e(L("Da ilustração a uma peça para guardar", "From illustration to a piece worth keeping"))}</h2>
      <p>{e(L("Cada retrato é pensado para existir para além do momento em que é oferecido.", "Each portrait is designed to live beyond the moment in which it is given."))}</p>
      <p>{e(L("O formato standard é A5, suficientemente presente para ter destaque numa secretária, estante ou prateleira, sem se tornar demasiado grande para um espaço pessoal. Formatos superiores podem ser desenvolvidos mediante pedido.", "The standard format is A5 — large enough to have presence on a desk, shelf or bookcase, while remaining suitable for a personal space. Larger formats are available upon request."))}</p>
      <h3>Illustration</h3>
      {ul(["Retrato ilustrado", "Impressão A5", "Ficheiro digital .jpg"], ["Illustrated portrait", "A5 print", "Digital .jpg file"])}
      <h3>Framed Illustration</h3>
      {ul(["Retrato ilustrado", "Impressão A5", "Moldura", "Ficheiro digital .jpg", "Embalagem preparada para oferta"], ["Illustrated portrait", "A5 print", "Frame", "Digital .jpg file", "Packaging prepared for gifting"])}
      <p class="tps-note">{e(L("A disponibilidade de molduras está sempre sujeita ao stock do fornecedor.", "Frame availability is always subject to supplier stock."))}</p>
    </div>
    <div class="tps-duo">
      {img("tps-tl-envelope", alt=L("Retrato ilustrado em envelope, versão sem moldura", "Illustrated portrait in an envelope, unframed version"))}
      {img("tps-tl-moldura", alt=L("Retrato ilustrado emoldurado", "Framed illustrated portrait"))}
    </div>
  </div>
</section>

<section class="tps-section">
  <div class="container tps-narrow">
    <div class="tps-narrow">
      <h2>{e(L("Adaptado a cada empresa", "Adapted to each company"))}</h2>
      <p>{e(L("A identidade standard do The People Series é assinada pela RIMA studio. Quando faz sentido, podemos adaptar alguns elementos à identidade da empresa:", "The standard The People Series identity is signed by RIMA studio. When relevant, selected elements can be adapted to the company's identity:"))}</p>
      {ul(["Logótipo", "Cor", "Nome do colaborador", "Anos de casa", "Data", "Mensagem", "Cartão", "Packaging"], ["Logo", "Colour", "Employee name", "Years with the company", "Date", "Message", "Card", "Packaging"])}
      <p>{e(L("Personalizações mais extensas ou produção de packaging específico são avaliadas caso a caso. A ilustração mantém sempre o carácter autoral do projeto, evitando transformar o retrato numa peça excessivamente corporate.", "More extensive customisation or bespoke packaging production is evaluated on a project-by-project basis. The illustration always retains the author-led character of the project, avoiding an overly corporate result."))}</p>
    </div>
  </div>
</section>

{case_html}

<section class="tps-cta-mid">
  <div class="container">
    <p>{e(L("Quer ver como ficaria na sua empresa?", "Want to see how it would work for your company?"))}</p>
    <button type="button" class="cta-link" data-open-contact>{e(L("Falar connosco", "Talk to us"))}</button>
  </div>
</section>

<section class="tps-section tps-tint">
  <div class="container tps-narrow">
    <h2>{e(L("Um serviço testado em contexto real", "A service tested in real corporate contexts"))}</h2>
    <p>{e(L("The People Series nasce de experiência real em projetos de reconhecimento corporate. Não é um template, um filtro ou um processo automático. Cada retrato é desenvolvido individualmente pela equipa RIMA studio.", "The People Series is built on real experience in corporate recognition projects. It is not a template, a filter or an automated process. Each portrait is developed individually by the RIMA studio team."))}</p>
    <p>{e(L("A experiência acumulada permite-nos trabalhar tanto com projetos pontuais como com programas recorrentes ao longo dos anos.", "Our experience allows us to work both on one-off projects and on recurring recognition programmes over the years."))}</p>
  </div>
</section>

<section class="tps-section">
  <div class="container tps-narrow">
    <h2>{e(L("Ilustração de autor, não um presente corporate genérico", "Author illustration, not a generic corporate gift"))}</h2>
    <p>{e(L("The People Series não é:", "The People Series is not:"))}</p>
    {ul(["Caricatura", "Retrato fotorealista", "Produção automática", "IA generativa", "Aplicação de um template", "Merchandising", "Um brinde corporate genérico"], ["Caricature", "Photorealistic portraiture", "Automated production", "Generative AI", "A template applied to photographs", "Merchandise", "A generic corporate giveaway"])}
    <p>{e(L("É uma forma de aplicar ilustração de autor ao reconhecimento das pessoas dentro de uma empresa.", "It is a way of bringing author illustration into employee recognition."))}</p>
  </div>
</section>

<section class="tps-section tps-tint">
  <div class="container tps-narrow">
    <h2>{e(L("Também em formato digital", "Digital file included"))}</h2>
    <p>{e(L("O ficheiro digital em alta resolução é sempre incluído. Pode ser utilizado pela empresa em contextos relacionados com a iniciativa de reconhecimento, como:", "A high-resolution digital file is always included. It can be used by the company in contexts related to the recognition initiative, such as:"))}</p>
    {ul(["Intranet", "Newsletters internas", "Apresentações", "Comunicação do evento", "Publicações de reconhecimento nas redes sociais"], ["Intranet", "Internal newsletters", "Presentations", "Event communication", "Employee recognition posts on social media"])}
    <p>{e(L("Utilizações comerciais, publicidade paga, merchandising, revenda ou alterações à ilustração devem ser avaliadas separadamente.", "Commercial campaigns, paid advertising, merchandising, resale or alterations to the artwork should be discussed separately."))}</p>
  </div>
</section>

<section class="tps-section">
  <div class="container tps-faq">
    <h2 class="tps-h-center">FAQ</h2>
    {faq_html}
  </div>
</section>

<section class="tps-cta">
  <div class="container">
    <h2>{e(L("Há pessoas que merecem mais do que um presente genérico.", "Some people deserve more than a generic corporate gift."))}</h2>
    <p>{e(L("Se a sua empresa procura uma forma mais pessoal de reconhecer quem faz parte da sua história, gostávamos de conhecer o projeto.", "If your company is looking for a more personal way to recognise the people behind its story, we would love to hear about the project."))}</p>
    <button type="button" class="cta-link" data-open-contact>{e(L("Falar connosco", "Get in touch"))}</button>
    <p class="tps-mail"><a href="mailto:{mail}">{mail}</a></p>
    <p class="tps-credit">{L("<strong>The People Series</strong> é um projeto do <strong>RIMA studio</strong>, desenvolvido por Marta + Ricardo.", "<strong>The People Series</strong> is a project by <strong>RIMA studio</strong>, developed by Marta + Ricardo.")}</p>
  </div>
</section>
'''
    title = L("The People Series | Retratos ilustrados para empresas — RIMA studio",
              "The People Series | Author Portraits for Employee Recognition — RIMA studio")
    desc = L("Retratos ilustrados de autor para employee recognition, anos de casa, milestones e momentos especiais dentro de uma empresa. Um projeto do RIMA studio.",
             "Author illustrations created for employee recognition, work anniversaries, milestones and meaningful moments inside a company. A project by RIMA studio.")
    content += contact_modal_html()
    write_page("the-people-series.html", title, content, desc=desc)

# ---------------- SITEMAP / ROBOTS ----------------
def build_sitemap():
    urls = []
    for fn in ALL_FILENAMES:
        pt_url = SITE_URL + url_for(fn, "pt")
        en_url = SITE_URL + url_for(fn, "en")
        for loc, alt1, alt2 in ((pt_url, "pt", "en"), (en_url, "en", "pt")):
            urls.append(f'''  <url>
    <loc>{loc}</loc>
    <xhtml:link rel="alternate" hreflang="pt" href="{pt_url}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{en_url}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{pt_url}"/>
  </url>''')
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
{chr(10).join(urls)}
</urlset>
'''
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)

    robots = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    with open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    with open(os.path.join(DIST, "CNAME"), "w", encoding="utf-8") as f:
        f.write("rimastudio.pt\n")

# ---------------- MAIN ----------------
def build_all_pages():
    build_home()
    build_oestudio()
    build_people_series()
    build_portfolio()
    build_portfolio("design", "design.html")
    build_portfolio("animacao", "animacao.html")
    build_portfolio("ilustracao", "ilustracao.html")
    for idx, p in enumerate(PROJECTS):
        build_project(p, idx)

def main():
    global LANG
    if os.path.exists(DIST):
        for fn in os.listdir(DIST):
            full = os.path.join(DIST, fn)
            if fn.endswith(".html") or fn in ("sitemap.xml", "robots.txt", "CNAME"):
                os.remove(full)
        en_dir = os.path.join(DIST, "en")
        if os.path.exists(en_dir):
            for fn in os.listdir(en_dir):
                if fn.endswith(".html"):
                    os.remove(os.path.join(en_dir, fn))
    os.makedirs(DIST, exist_ok=True)
    os.makedirs(os.path.join(DIST, "en"), exist_ok=True)
    img_dist = os.path.join(DIST, "images")
    os.makedirs(img_dist, exist_ok=True)
    for fn in os.listdir(IMG_SRC):
        shutil.copyfile(os.path.join(IMG_SRC, fn), os.path.join(img_dist, fn))
    vid_src = os.path.join(ROOT, "videos")
    if os.path.isdir(vid_src):
        vid_dist = os.path.join(DIST, "videos")
        os.makedirs(vid_dist, exist_ok=True)
        for fn in os.listdir(vid_src):
            shutil.copyfile(os.path.join(vid_src, fn), os.path.join(vid_dist, fn))

    for LANG in ("pt", "en"):
        build_all_pages()

    build_sitemap()

    total_html = len(PROJECTS) * 2 + len(STATIC_FILENAMES) * 2
    print(f"Built {total_html} HTML pages ({len(PROJECTS)} projects x 2 langs + {len(STATIC_FILENAMES)} static x 2 langs).")
    print("Images copied:", len(os.listdir(img_dist)))
    print("sitemap.xml + robots.txt + CNAME written.")

if __name__ == "__main__":
    main()
