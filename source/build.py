#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, shutil, html

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
IMG_SRC = os.path.join(ROOT, "web")
SITE_URL = "https://rimastudio.pt"

with open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8") as f:
    SITE = json.load(f)
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
    return f'''<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
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
    <li><a href="{oestudio_url}#contacto">{e(L('CONTACTO','CONTACT'))}</a></li>
    <li><a href="{SITE['meta']['external']['rimalab']}" target="_blank" rel="noopener">RIMA lab</a></li>
    <li><a href="{SITE['meta']['external']['estevescorga']}" target="_blank" rel="noopener">ESTEVES CORGA</a>
      <ul class="offcanvas-sub">
        <li><a href="{SITE['meta']['external']['estevescorga']}" target="_blank" rel="noopener">{e(L('Portfolio de Ilustração','Illustration Portfolio'))}</a></li>
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
  <form class="contact-form" id="contactForm" action="https://api.web3forms.com/submit" method="POST"
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
  </form>
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
def build_project(p, idx):
    tags_pt = p.get("tags_pt", "")
    tags_en = p.get("tags_en", "")
    title = p.get("title", p["slug"])
    title_en = p.get("title_en", title)
    paras = ""
    for i, t in enumerate(p.get("text_pt", [])):
        en_t = p.get("text_en", [""]*len(p["text_pt"]))[i] if i < len(p.get("text_en", [])) else ""
        paras += f'      <p>{bi(t, en_t)}</p>\n'

    credit = f'<p class="project-credit">{e(p["credit"])}</p>' if p.get("credit") else ""

    info_block = ""
    if p.get("info") or p.get("info_en"):
        info_block = f'<p class="project-info">{bi(p.get("info",""), p.get("info_en", p.get("info","")))}</p>'
    if p.get("external_link"):
        info_block += f'<div class="center"><a class="external-link" href="{p["external_link"]}" target="_blank" rel="noopener">{e(p.get("external_label",""))}</a></div>'

    # Video embed: only rendered once a real YouTube id is set on the project
    # via "youtube_id" in projects.json (these are the original, already-public
    # client/film videos — not re-uploads). No placeholder text otherwise — we
    # don't invent copy that wasn't on the original site.
    video_note = ""
    if p.get("youtube_id"):
        video_note = f'''<div class="project-video">
      <div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/{p['youtube_id']}" title="{e(p['title'])}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe></div>
    </div>'''

    gallery_imgs = p.get("images", [])
    cols_class = "cols-2" if len(gallery_imgs) > 1 else ""
    gallery = f'<div class="project-gallery {cols_class}">\n'
    for im in gallery_imgs:
        gallery += f'      {img(im, alt=title)}\n'
    gallery += '    </div>'

    prev_p = PROJECTS[idx-1] if idx > 0 else PROJECTS[-1]
    next_p = PROJECTS[idx+1] if idx < len(PROJECTS)-1 else PROJECTS[0]

    note_html = f'<!-- NOTA interna: {e(p["note"])} -->' if p.get("note") else ""

    content = f'''
{note_html}
<section class="project-head">
  <div class="container">
    {bi(title, title_en, 'h1', 'project-title')}
    {bi(tags_pt, tags_en, 'p', 'project-tags')}
  </div>
</section>
<section class="section-tight" style="padding-top:0;">
  <div class="container">
    <div class="project-text">
{paras}    </div>
    {credit}
    <div class="center">{info_block}</div>
    {video_note}
    {gallery}
  </div>
</section>
<div class="project-nav">
  <a href="{url_for(prev_p['slug'] + '.html')}">&larr; {e(prev_p['title'])}</a>
  <a href="{url_for(next_p['slug'] + '.html')}">{e(next_p['title'])} &rarr;</a>
</div>
'''
    page_title = f"{L(title, title_en)} | RIMA studio"
    desc_pt = (p.get("text_pt") or [""])[0][:160]
    desc_en = (p.get("text_en") or [desc_pt])[0][:160]
    write_page(f"{p['slug']}.html", page_title, content, desc=L(desc_pt, desc_en))

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

    for LANG in ("pt", "en"):
        build_all_pages()

    build_sitemap()

    total_html = len(PROJECTS) * 2 + len(STATIC_FILENAMES) * 2
    print(f"Built {total_html} HTML pages ({len(PROJECTS)} projects x 2 langs + {len(STATIC_FILENAMES)} static x 2 langs).")
    print("Images copied:", len(os.listdir(img_dist)))
    print("sitemap.xml + robots.txt + CNAME written.")

if __name__ == "__main__":
    main()
