"""Builds the Busy Beaver Handyman site into dist/.

Shared parts live in src/partials, page content in src/pages and src/content.py.
Run:  python3 build.py
Netlify runs the same command (see netlify.toml) and publishes dist/.
"""
import html
import re
import shutil
from pathlib import Path

import datetime
import math

from src.content import SERVICES, TOWNS
from src.blog import POSTS
from src.reviews import RATING, REVIEWS

ROOT = Path(__file__).parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
DOMAIN = "busybeaverky.com"
PHONE_DISPLAY = "(859) 800-5955"
PHONE_TEL = "+18598005955"
EMAIL = "busybeaverky@gmail.com"

SERVICE_BY_SLUG = {s["slug"]: s for s in SERVICES}
TOWN_BY_SLUG = {t["slug"]: t for t in TOWNS}


def part(name):
    return (SRC / "partials" / name).read_text()


def esc(text):
    return html.escape(text, quote=True)


def icon(sym, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<svg{c} aria-hidden="true"><use href="#{sym}"/></svg>'


# ---------- shared blocks ----------

def footer_services(root):
    items = "\n".join(f'          <li><a href="{root}services/{s["slug"]}.html">{esc(s["name"])}</a></li>' for s in SERVICES)
    return f'<nav class="footer-col" aria-label="Services">\n        <h3>Services</h3>\n        <ul>\n{items}\n        </ul>\n      </nav>'


def footer_areas(root):
    items = "\n".join(f'          <li><a href="{root}service-areas/{t["slug"]}.html">{esc(t["name"])}, KY</a></li>' for t in TOWNS)
    return f'<nav class="footer-col" aria-label="Service areas">\n        <h3>Service Areas</h3>\n        <ul>\n{items}\n        </ul>\n      </nav>'


def service_cards(root, slugs=None):
    items = []
    for s in (SERVICE_BY_SLUG[x] for x in slugs) if slugs else SERVICES:
        has_img = (ROOT / "images" / "services" / f"{s['slug']}.webp").exists()
        photo = (f'<img class="card-photo" src="{root}images/services/{s["slug"]}.webp" width="1536" height="1024" loading="lazy" alt="">' if has_img
                 else f'<span class="card-photo card-photo-empty">{icon(s["icon"])}</span>')
        items.append(
            f'        <li><a class="service-card has-photo" href="{root}services/{s["slug"]}.html">{photo}'
            f'<span class="service-icon">{icon(s["icon"])}</span>'
            f'<h3>{esc(s["name"])}</h3><p>{esc(s["card"])}</p>'
            f'<span class="card-more">Learn more{icon("i-arrow")}</span></a></li>'
        )
    return '      <ul class="services-grid">\n' + "\n".join(items) + "\n      </ul>"


def town_links(root, slugs=None, current=None):
    items = []
    for t in (TOWN_BY_SLUG[x] for x in slugs) if slugs else TOWNS:
        cls = ' class="home"' if t["slug"] == "lexington-ky" and not slugs else ""
        cur = ' aria-current="page"' if t["slug"] == current else ""
        items.append(f'          <li{cls}><a href="{root}service-areas/{t["slug"]}.html"{cur}>{icon("i-pin")}{esc(t["name"])}</a></li>')
    return '        <ul class="town-list">\n' + "\n".join(items) + "\n        </ul>"


def quote_block(root, title="Send us photos, get a quote", page_name="Home", town=None):
    q = part("quote.html")
    q = q.replace("{{quote_title}}", esc(title)).replace("{{page_name}}", esc(page_name))
    if town:
        q = q.replace(f"<option>{town}</option>", f"<option selected>{town}</option>")
    return q


def faq_block(faqs, heading="Questions we hear a lot"):
    items = "\n".join(
        f'        <details>\n          <summary>{esc(q)}{icon("i-plus")}</summary>\n          <p>{esc(a)}</p>\n        </details>'
        for q, a in faqs
    )
    return (
        '  <section class="alt" aria-labelledby="faq-title">\n    <div class="wrap">\n'
        f'      <div class="section-head center"><h2 id="faq-title">{esc(heading)}</h2></div>\n'
        f'      <div class="faq">\n{items}\n      </div>\n    </div>\n  </section>'
    )


def steps_block():
    return """  <section aria-labelledby="how-title">
    <div class="wrap">
      <div class="section-head center"><h2 id="how-title">How it works</h2><p>Three steps from "I should fix that" to done.</p></div>
      <ol class="steps">
        <li><h3>Request an estimate</h3><p>Fill out the form or send photos of the job. A short description is plenty.</p></li>
        <li><h3>Get a clear price</h3><p>We look it over and send you a price before any work starts. No guesswork.</p></li>
        <li><h3>We do the job and clean up</h3><p>We show up, get it done right and leave your place as tidy as we found it.</p></li>
      </ol>
    </div>
  </section>"""


HERO_BG_DEFAULT = "images/blog/fall-home-checklist.webp"


def page_hero(root, crumbs, h1, lede, kicker=None, kicker_icon="i-pin", bg=HERO_BG_DEFAULT):
    trail = [f'<a href="{root}index.html">Home</a>']
    for label, href in crumbs[:-1]:
        trail.append(f'<a href="{href}">{esc(label)}</a>')
    trail.append(f'<span aria-current="page">{esc(crumbs[-1][0])}</span>')
    kick = f'<p class="hero-kicker">{icon(kicker_icon)}{esc(kicker)}</p>' if kicker else ""
    photo = (f'\n    <div class="page-hero-bg" aria-hidden="true"><img src="{root}{bg}" width="1600" height="900" fetchpriority="high" alt=""></div>'
             if bg and (ROOT / bg).exists() else "")
    return f"""  <div class="page-hero on-choc{' has-bg' if photo else ''}">{photo}
    <div class="wrap">
      <nav class="breadcrumb" aria-label="Breadcrumb">{' <span aria-hidden="true">/</span> '.join(trail)}</nav>
      {kick}
      <h1>{esc(h1)}</h1>
      <p class="lede">{esc(lede)}</p>
      <div class="hero-actions">
        <a class="btn btn-yellow" href="#quote">Get a Free Estimate{icon("i-arrow")}</a>
        <a class="btn btn-outline" data-tel href="#">{icon("i-phone")}Call Now</a>
      </div>
      <ul class="trust-line">
        <li>{icon("i-check")}Free estimates</li>
        <li>{icon("i-check")}Reply within 1 business day</li>
        <li>{icon("i-check")}Insured</li>
      </ul>
    </div>
  </div>"""


def aside_card(root):
    return f"""      <aside class="side-card" aria-label="Get a quote">
        <img src="{root}images/brand/beaver-head.webp" width="256" height="230" alt="">
        <h2>Get a clear price</h2>
        <ul>
          <li>{icon("i-camera")}Send a few photos</li>
          <li>{icon("i-clock")}Reply within 1 business day</li>
          <li>{icon("i-tag")}Free, no obligation</li>
          <li>{icon("i-shield")}Insured</li>
        </ul>
        <a class="btn btn-yellow" href="#quote">Get a Free Estimate</a>
        <p class="side-offer" data-offer-only>New customer? <a href="#offer" data-open-offer>$50 off your first job</a></p>
      </aside>"""


# ---------- before / after gallery ----------

WORK = [
    ("slat-wall-sconces", 1283, 753, "Wall panels", "Slat accent wall, TV and sconces", "Before: bare wall with slat panels going up. After: full slat accent wall with a mounted TV and two sconces."),
    ("slat-wall-tv", 1283, 753, "TV mounting", "Framed TV on a slat wall", "Before: slat wall with TV brackets and loose cables. After: TV mounted in a wood frame, cables tucked away."),
    ("tv-over-fireplace", 1284, 749, "TV mounting", "TV over the fireplace", "Before: empty wall above a fireplace mantel. After: TV mounted above the fireplace."),
    ("floating-shelves", 1280, 753, "Shelves", "Floating shelves", "Before: three hidden shelf brackets on a wall. After: three wood floating shelves installed."),
    ("porch-handrail", 1280, 753, "General repairs", "Front step handrail", "Before: front step with no railing. After: black metal handrail installed by the front door."),
    ("bedroom-tv", 1284, 749, "TV mounting", "Bedroom TV mount", "Before: blank bedroom wall above a dresser. After: TV mounted above the dresser."),
    ("living-room-tv", 1281, 753, "TV mounting", "Living room TV mount", "Before: empty living room wall. After: large TV mounted on the wall."),
]


def work_gallery(root):
    items = []
    for slug, w, h, tag, title, alt in WORK:
        items.append(f"""        <li><button class="shot" type="button" data-full="{root}images/work/{slug}.webp" data-title="{esc(title)}">
          <img src="{root}images/work/{slug}.webp" width="{w}" height="{h}" loading="lazy" alt="{esc(alt)}">
          <span class="ba ba-before">Before</span><span class="ba ba-after">After</span>
          <span class="shot-caption"><span><span class="shot-tag">{esc(tag)}</span>{esc(title)}</span><span class="shot-zoom">{icon("i-zoom")}</span></span>
        </button></li>""")
    return f"""  <!-- Our work: real before/after photos -->
  <section class="work" id="work" aria-labelledby="work-title">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">{icon("i-camera")}Our work</p>
        <h2 id="work-title">Before and after</h2>
        <p>Real jobs, real homes. Tap a photo to open it, then tap again to zoom in on the details.</p>
      </div>
      <ul class="gallery">
{chr(10).join(items)}
      </ul>
    </div>
  </section>"""


# ---------- hero: looping workbench video behind the headline ----------

HERO_VIDEO = ROOT / "images" / "hero" / "workbench-loop.mp4"


def video_hero(root):
    return f"""<!-- a) Hero: the workbench video plays on a loop behind the headline (still frame with reduced motion) -->
  <section class="video-hero on-choc" aria-labelledby="hero-title">
    <video class="hero-video" muted loop playsinline preload="none" poster="{root}images/hero/workbench-poster.jpg"
           data-src="{root}images/hero/workbench-loop.mp4" aria-hidden="true" tabindex="-1"></video>
    <div class="hero-scrim" aria-hidden="true"></div>
    <div class="wrap hero-grid">
      <div class="hero-copy">
        <p class="hero-kicker">{icon("i-pin")}Handyman in Lexington, KY</p>
        <h1 id="hero-title">Busy fixing <span class="hl">Lexington</span>, one home at a time.</h1>
        <p class="lede">Repairs, installs and small upgrades for homes in Lexington and nearby Central Kentucky towns. Send us a few photos and get a clear price before we start.</p>
        <div class="hero-actions">
          <a class="btn btn-yellow" href="#quote">Get a Free Estimate{icon("i-arrow")}</a>
          <a class="btn btn-outline" data-tel href="#">{icon("i-phone")}Call Now</a>
        </div>
        <ul class="trust-line">
          <li>{icon("i-check")}Reliable</li>
          <li>{icon("i-check")}Local</li>
          <li>{icon("i-check")}Quality Work</li>
        </ul>
      </div>
    </div>
    <button class="video-toggle" type="button" aria-label="Pause background video" hidden>
      <svg viewBox="0 0 24 24" aria-hidden="true"><path class="ic-pause" d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z"/><path class="ic-play" d="M8 5v14l11-7z"/></svg>
    </button>
  </section>"""


# ---------- reviews: Thumbtack rating + scrolling review cards ----------

def stars_row(label=True):
    stars = "".join(icon("i-star") for _ in range(5))
    return f'<div class="stars" role="img" aria-label="5 out of 5 stars">{stars}</div>' if label else f'<div class="stars" aria-hidden="true">{stars}</div>'


def review_card(r, hidden=False):
    initials = "".join(w[0] for w in r["name"].replace(".", "").split()[:2]).upper()
    meta = " · ".join(x for x in (r.get("service"), r.get("town")) if x) or "Thumbtack customer"
    wide = " review-wide" if len(r["text"]) > 200 else ""
    return f"""<li class="review-card{wide}"{' aria-hidden="true"' if hidden else ''}>
            <div class="review-top">{stars_row(label=False)}<span class="review-src">via {esc(RATING["source"])}</span></div>
            <blockquote>“{esc(r["text"])}”</blockquote>
            <div class="review-who"><span class="avatar">{esc(initials)}</span><span><strong>{esc(r["name"])}</strong><small>{esc(meta)}</small></span></div>
          </li>"""


def reviews_section(root):
    r = RATING
    head = f"""<section id="reviews" class="reviews" aria-labelledby="reviews-title">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">{icon("i-star")}Reviews</p>
        <h2 id="reviews-title">What our neighbors say</h2>
      </div>"""
    if not REVIEWS:
        return f"""<!-- c) Reviews: rating from our Thumbtack profile; add review texts in src/reviews.py -->
  {head}
      <div class="reviews-box">
        <div class="rating-score"><strong>{r["score"]}</strong>{stars_row()}</div>
        <div>
          <h3>Rated {r["score"]} from {r["count"]} reviews on {r["source"]}</h3>
          <p>{r["badge"]} on {r["source"]}, hired {r["hires"]} times. Real customers from Lexington and nearby towns.</p>
          <ul class="rating-facts">
            <li>{icon("i-star")}{r["score"]} average rating</li>
            <li>{icon("i-star")}{r["badge"]}</li>
            <li>{icon("i-star")}Hired {r["hires"]} times</li>
          </ul>
        </div>
        <a class="btn btn-yellow btn-sm" href="#quote">Get a Free Estimate</a>
      </div>
    </div>
  </section>"""
    half = (len(REVIEWS) + 1) // 2
    rows = [REVIEWS[:half], REVIEWS[half:]] if len(REVIEWS) >= 6 else [REVIEWS]
    tracks = []
    for i, row in enumerate(rows):
        cards = [review_card(x) for x in row] + [review_card(x, hidden=True) for x in row]
        secs = max(30, len(row) * 9)
        tracks.append(f"""      <div class="marquee{' marquee-rev' if i else ''}">
        <ul class="marquee-track" style="--dur:{secs}s">
          {chr(10).join("          " + c if j else c for j, c in enumerate(cards)).strip()}
        </ul>
      </div>""")
    return f"""<!-- c) Reviews: word for word from our Thumbtack profile (src/reviews.py) -->
  {head}
      <button class="marquee-toggle" type="button" aria-pressed="false">Pause scrolling reviews</button>
    </div>
{chr(10).join(tracks)}
    <div class="wrap">
      <div class="rating-line">{stars_row()}<p><strong>{r["score"]} out of 5</strong> · {r["count"]} reviews on {r["source"]} · {r["badge"]}</p></div>
    </div>
  </section>"""


# ---------- service area: ZIP check + map ----------

# ZIP codes we serve, by town (used by the ZIP checker)
SERVED_ZIPS = {
    "Lexington": ["40502", "40503", "40504", "40505", "40506", "40507", "40508", "40509", "40510", "40511", "40513", "40514", "40515", "40516", "40517"],
    "Nicholasville": ["40356"],
    "Georgetown": ["40324"],
    "Versailles": ["40383"],
    "Winchester": ["40391"],
    "Richmond": ["40475"],
    "Paris": ["40361"],
}

# Map positions follow real latitude/longitude, simplified
MAP_TOWNS = [
    ("Lexington", 208, 202), ("Nicholasville", 166, 323), ("Georgetown", 175, 73), ("Versailles", 72, 193),
    ("Winchester", 402, 240), ("Richmond", 333, 424), ("Paris", 358, 73),
]


def map_svg(root):
    spokes = "".join(f'<path d="M208 202 L{x} {y}"/>' for n, x, y in MAP_TOWNS[1:])
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="7"/>' for n, x, y in MAP_TOWNS[1:])
    label_pos = {"Nicholasville": (180, 328, "start"), "Georgetown": (190, 66, "start"), "Versailles": (60, 178, "middle"),
                 "Winchester": (402, 268, "middle"), "Richmond": (348, 430, "start"), "Paris": (372, 66, "start")}
    labels = "".join(f'<text x="{x}" y="{y}" text-anchor="{a}">{n}</text>' for n, (x, y, a) in label_pos.items())
    links = "".join(
        f'<a href="{root}service-areas/{t["slug"]}.html" aria-label="{t["name"]}, KY"><circle cx="{x}" cy="{y}" r="22" fill="transparent"/></a>'
        for (n, x, y) in MAP_TOWNS for t in TOWNS if t["name"] == n)
    return f"""<svg class="area-map" viewBox="0 0 470 470" role="img" aria-labelledby="map-title-{root.count('.')}">
          <title id="map-title-{root.count('.')}">Map of Lexington and the nearby towns Busy Beaver Handyman serves</title>
          <defs>
            <radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#F2B705" stop-opacity=".38"/><stop offset=".7" stop-color="#F2B705" stop-opacity=".12"/><stop offset="1" stop-color="#F2B705" stop-opacity="0"/></radialGradient>
          </defs>
          <circle cx="208" cy="226" r="235" fill="url(#glow)"/>
          <g fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" opacity=".95">{spokes}</g>
          <g fill="none" stroke="#C9A97F" stroke-width="3" stroke-linecap="round">
            <path d="M150 0 C175 70 196 150 214 210 S300 360 345 470"/>
            <path d="M0 180 C80 170 150 178 200 186 S330 220 470 236"/>
          </g>
          <g font-family="Inter, sans-serif" font-weight="800" font-size="12" text-anchor="middle">
            <g transform="translate(166 40)"><path d="M-14 -14h28v14c0 10-8 16-14 18-6-2-14-8-14-18z" fill="#3B2416"/><text y="3" fill="#F2B705">75</text></g>
            <g transform="translate(300 214)"><path d="M-14 -14h28v14c0 10-8 16-14 18-6-2-14-8-14-18z" fill="#3B2416"/><text y="3" fill="#F2B705">64</text></g>
          </g>
          <g fill="#8B5A2B" stroke="#FFF8EC" stroke-width="3">{dots}</g>
          <g font-family="Poppins, sans-serif" font-weight="700" font-size="14" fill="#3B2416">{labels}</g>
          <g transform="translate(208 202)">
            <path d="M0 0c-12-14-18-24-18-32a18 18 0 0 1 36 0c0 8-6 18-18 32z" fill="#F2B705" stroke="#3B2416" stroke-width="3"/>
            <circle cy="-32" r="6" fill="#3B2416"/>
          </g>
          <text x="208" y="232" text-anchor="middle" font-family="Poppins, sans-serif" font-weight="800" font-size="20" fill="#3B2416">Lexington</text>
          {links}
        </svg>"""


def area_checker(root):
    zips = ";".join(f"{town}:{','.join(z)}" for town, z in SERVED_ZIPS.items())
    return f"""  <!-- g) Service area: ZIP check + map -->
  <section class="area-check" id="areas" aria-labelledby="areas-title">
    <div class="wrap area-check-grid">
      <div class="area-copy">
        <p class="eyebrow">{icon("i-pin")}Ready when you are</p>
        <h2 id="areas-title">Do we come to <span class="mark">your street?</span></h2>
        <p class="area-sub">Type your ZIP code. If you're in our area, we'll take you straight to the quote form.</p>
        <form class="zip-form" id="zip-form" data-zips="{zips}" novalidate>
          <label class="vh" for="zip-input">ZIP code</label>
          <span class="zip-field">{icon("i-pin")}<input id="zip-input" type="text" inputmode="numeric" autocomplete="postal-code" maxlength="5" placeholder="Enter your ZIP code" aria-describedby="zip-result"></span>
          <button class="btn btn-yellow" type="submit">Check my area{icon("i-arrow")}</button>
        </form>
        <p class="zip-result" id="zip-result" role="status"></p>
        <ul class="area-trust">
          <li>{icon("i-clock")}Takes 10 seconds</li>
          <li>{icon("i-tag")}Free, no obligation</li>
          <li>{icon("s-door")}Local to Lexington</li>
        </ul>
        <p class="area-towns">Lexington · Nicholasville · Georgetown · Versailles · Winchester · Richmond · Paris · <a href="{root}service-areas.html">See all areas</a></p>
      </div>
      <div class="area-visual">
        {map_svg(root)}
        <div class="map-beaver" aria-hidden="true">
          <span class="bubble">We might be right<br>down the road!</span>
          <img src="{root}images/brand/mascot.webp" width="620" height="687" alt="" loading="lazy">
        </div>
      </div>
    </div>
  </section>"""


# ---------- page shell ----------

def render(path, title, description, main, root, schema="", noindex=False):
    head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#3B2416">
{'<meta name="robots" content="noindex">' + chr(10) if noindex else ""}<link rel="icon" href="{root}favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{root}apple-touch-icon.png">
<link rel="canonical" href="https://{DOMAIN}/{path.replace('index.html', '').replace('.html', '')}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:image" content="https://{DOMAIN}/images/brand/beaver-head-512.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/site.css">
{schema}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""
    footer = (part("footer.html")
              .replace("{{footer_services}}", footer_services(root))
              .replace("{{footer_areas}}", footer_areas(root)))
    doc = (head + part("sprite.html") + "\n" + part("header.html") + "\n<main id=\"main\">\n"
           + main + "\n</main>\n\n" + footer
           + f'\n<script src="{root}assets/site.js"></script>\n</body>\n</html>\n')
    doc = doc.replace("{{root}}", root)
    # Contact details straight into the HTML (works without JavaScript, readable by Google)
    doc = doc.replace('data-tel href="#"', f'data-tel href="tel:{PHONE_TEL}"')
    doc = re.sub(r'(<(\w+)[^>]*\bdata-phone\b[^>]*>)(</\2>)', lambda m: m.group(1) + PHONE_DISPLAY + m.group(3), doc)
    doc = doc.replace('data-email href="#"', f'data-email href="mailto:{EMAIL}"')
    doc = re.sub(r'(<(\w+)[^>]*\bdata-email-label\b[^>]*>)(</\2>)', lambda m: m.group(1) + EMAIL + m.group(3), doc)
    out = DIST / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    return out


# ---------- pages ----------

def build_home():
    root = ""
    before = (SRC / "pages" / "home-before-quote.html").read_text()
    after = (SRC / "pages" / "home-after-quote.html").read_text()
    before = re.sub(r'      <ul class="services-grid">.*?</ul>', lambda m: service_cards(root), before, flags=re.S)
    before = before.replace(
        '<a class="btn btn-yellow" href="#quote">Get a Free Estimate<svg aria-hidden="true"><use href="#i-arrow"/></svg></a>\n        <p>Don\'t see your job?',
        '<a class="btn btn-outline-dark" href="services.html">See all services</a>\n        <p>Don\'t see your job?')
    after = after.replace("{{area_checker}}", area_checker(root))
    after = re.sub(r'      <ul class="blog-grid">.*?</ul>', lambda m: post_cards(root, POSTS_SORTED[:3]), after, flags=re.S)
    after = re.sub(r'<a class="btn btn-outline-dark" href="blog/" data-soon>Visit the blog</a>', '<a class="btn btn-outline-dark" href="blog.html">Visit the blog</a>', after)
    after = after.replace('<a class="btn btn-yellow" href="#quote">Check my address</a>',
                          '<a class="btn btn-yellow" href="service-areas.html">See all service areas</a>')
    before = before.replace("{{work_gallery}}", work_gallery(root))
    before = before.replace("{{reviews}}", reviews_section(root))
    if HERO_VIDEO.exists():
        before = re.sub(r"  <!-- a\) Hero -->.*?\n  </div>\n(?=\n  <!-- b\))", lambda m: "  " + video_hero(root) + "\n", before, count=1, flags=re.S)
    main = before + "\n\n" + quote_block(root) + "\n\n" + after
    render("index.html", "Busy Beaver Handyman | Handyman in Lexington, KY",
           "Busy Beaver Handyman fixes, installs and maintains homes in Lexington, KY and nearby towns: Nicholasville, Georgetown, Versailles, Winchester, Richmond and Paris. Send photos for a free estimate.",
           main, root, schema=part("schema.html"))


def build_services_hub():
    root = ""
    main = page_hero(root, [("Services", "")], "Handyman services in Lexington, KY",
                     "Repairs, installs and upkeep for homes across Lexington and nearby Central Kentucky towns. Pick a service to see what's included, or send us your whole list.",
                     kicker="Services") + f"""

  <section aria-labelledby="all-services">
    <div class="wrap">
      <div class="section-head"><h2 id="all-services">Everything we can take off your list</h2><p>Most visits cover a few jobs at once. Tell us everything and we'll plan the day around it.</p></div>
{service_cards(root)}
    </div>
  </section>

{steps_block()}

{quote_block(root, "Tell us what needs doing", "Services")}"""
    render("services.html", "Handyman Services in Lexington, KY | Busy Beaver Handyman",
           "Drywall repair, painting, TV mounting, furniture assembly, doors and locks, gutter cleaning, light fixtures, junk removal and general repairs in Lexington, KY.",
           main, root)


def build_service(s):
    root = "../"
    others = [x["slug"] for x in SERVICES if x["slug"] != s["slug"]][:3]
    checklist = "\n".join(f'          <li>{icon("i-check")}{esc(i)}</li>' for i in s["includes"])
    body = "\n".join(f"        <p>{esc(p)}</p>" for p in s["body"])
    main = page_hero(root, [("Services", f"{root}services.html"), (s["name"], "")], s["title"], s["intro"],
                     kicker=s["name"], kicker_icon=s["icon"], bg=f"images/services/{s['slug']}.webp") + f"""

  <section aria-labelledby="included-title">
    <div class="wrap content-grid">
      <div class="prose">
        <h2 id="included-title">What's included</h2>
        <ul class="checklist">
{checklist}
        </ul>
        <h2>How we do it</h2>
{body}
      </div>
{aside_card(root)}
    </div>
  </section>

{steps_block()}

{faq_block(s["faq"], f"{s['name']}: common questions")}

  <section aria-labelledby="where-title">
    <div class="wrap">
      <div class="section-head"><h2 id="where-title">{esc(s['name'])} near you</h2><p>We do this work in Lexington and the towns around it.</p></div>
{town_links(root)}
    </div>
  </section>

  <section class="alt" aria-labelledby="more-title">
    <div class="wrap">
      <div class="section-head"><h2 id="more-title">Often booked together</h2></div>
{service_cards(root, others)}
    </div>
  </section>

{quote_block(root, f"Get a {s['name']} quote", s["name"])}"""
    render(f"services/{s['slug']}.html", f"{s['title']} | Busy Beaver Handyman",
           f"{s['intro']} Serving Lexington, Nicholasville, Georgetown and nearby towns. Free estimates from photos.",
           main, root)


def build_areas_hub():
    root = ""
    cards = "\n".join(
        f'        <li><a class="area-card" href="service-areas/{t["slug"]}.html"><strong>{icon("i-pin")}{esc(t["name"])}, KY</strong>'
        f'<span>{esc(t["county"])} · {esc(t["distance"])}</span></a></li>' for t in TOWNS)
    map_html = f'<figure class="map" style="margin:0">{map_svg(root)}<figcaption>Simplified map. Tap a town to see its page.</figcaption></figure>'
    main = page_hero(root, [("Service Areas", "")], "Handyman service areas around Lexington, KY",
                     "Based in Lexington and on the road every day to the towns around it. Find your town below.",
                     kicker="Service Areas") + f"""

  <section aria-labelledby="towns-title">
    <div class="wrap area-grid">
      <div>
        <h2 id="towns-title">Towns we serve</h2>
        <ul class="area-cards">
{cards}
        </ul>
        <p class="note">Close by but not listed? Send your address with your request and we'll let you know.</p>
      </div>
      {map_html}
    </div>
  </section>

{quote_block(root, "Check your address and get a quote", "Service Areas")}"""
    render("service-areas.html", "Service Areas | Busy Beaver Handyman, Lexington KY",
           "Busy Beaver Handyman serves Lexington, Nicholasville, Georgetown, Versailles, Winchester, Richmond and Paris, Kentucky.",
           main, root)


def build_town(t):
    root = "../"
    local = "\n".join(f"        <p>{esc(p)}</p>" for p in t["local"])
    nearby = town_links(root, t["nearby"])
    faqs = [
        (f"How soon can you get to {t['name']}?", "We reply to every request within 1 business day, then offer you the next open time that fits your schedule."),
        (f"What jobs do you do in {t['name']}?", "Everything on our services list: general repairs, drywall, painting, TV mounting, furniture assembly, doors and locks, gutter cleaning, light fixtures and junk removal."),
        ("Are you insured?", "Yes, Busy Beaver Handyman is insured. We're happy to send proof of coverage before the job."),
    ]
    main = page_hero(root, [("Service Areas", f"{root}service-areas.html"), (f"{t['name']}, KY", "")], t["title"], t["intro"],
                     kicker=f"{t['county']} · {t['distance']}") + f"""

  <section aria-labelledby="local-title">
    <div class="wrap content-grid">
      <div class="prose">
        <h2 id="local-title">Handyman help in {esc(t['name'])}</h2>
{local}
      </div>
{aside_card(root)}
    </div>
  </section>

  <section class="alt" aria-labelledby="popular-title">
    <div class="wrap">
      <div class="section-head"><h2 id="popular-title">Popular jobs in {esc(t['name'])}</h2></div>
{service_cards(root, t["popular"])}
      <div class="services-foot"><a class="btn btn-outline-dark" href="{root}services.html">See all services</a></div>
    </div>
  </section>

{faq_block(faqs, f"{t['name']} handyman questions")}

  <section aria-labelledby="nearby-title">
    <div class="wrap">
      <div class="section-head"><h2 id="nearby-title">Nearby towns we serve</h2></div>
{nearby}
    </div>
  </section>

{quote_block(root, f"Get a quote in {t['name']}", t["name"], town=t["name"])}"""
    render(f"service-areas/{t['slug']}.html", f"{t['title']} | Busy Beaver Handyman",
           f"Handyman services in {t['name']}, KY ({t['county']}): repairs, drywall, painting, TV mounting and more. Free estimates from photos, reply within 1 business day.",
           main, root)


def build_contact():
    root = ""
    tiles = [
        ("#quote", "i-clipboard", "Get a free estimate", "Takes about 2 minutes", ""),
        ("#", "i-phone", "Call or text", '<span data-phone></span>', " data-tel"),
        ("#quote", "i-camera", "Send photos", "Fastest way to a price", ""),
        ("#", "i-chat", "Ask Busy Beaver", "Quick answers, right now", " data-open-helper"),
    ]
    tile_html = "\n".join(
        f'          <li><a class="contact-tile" href="{h}"{extra}><span class="tile-icon">{icon(ic)}</span><strong>{t}</strong><span>{sub}</span></a></li>'
        for h, ic, t, sub, extra in tiles)
    main = f"""  <div class="contact-hero">
    <div class="wrap contact-hero-grid">
      <div>
        <nav class="breadcrumb dark" aria-label="Breadcrumb"><a href="index.html">Home</a> <span aria-hidden="true">/</span> <span aria-current="page">Contact</span></nav>
        <p class="pill-label"><span class="dot" aria-hidden="true"></span>Contact Busy Beaver</p>
        <h1>Let's get it <span class="hl-under">done.</span></h1>
        <p class="lede">Pick whatever's easiest for you. We reply within 1 business day.</p>
        <ul class="contact-tiles">
{tile_html}
        </ul>
      </div>
      <figure class="contact-photo">
        <img src="images/blog/quote-from-photos.webp" width="1600" height="900" alt="Busy Beaver Handyman technician checking job photos by the company van">
        <figcaption><img src="images/brand/beaver-head.webp" width="256" height="230" alt=""><span><strong>A real person reads every request.</strong> No call centers, no runaround.</span></figcaption>
      </figure>
    </div>
  </div>

  <section class="alt" aria-labelledby="next-title">
    <div class="wrap">
      <div class="section-head center"><h2 id="next-title">What happens after you reach out</h2></div>
      <ol class="next-steps">
        <li><span class="when">Today</span><h3>You send the details</h3><p>A short description and a few photos. Your address helps us plan the trip.</p></li>
        <li><span class="when">Within 1 business day</span><h3>We reply with a price</h3><p>A clear price for the whole list, or a couple of quick questions if we need them.</p></li>
        <li><span class="when">When it suits you</span><h3>We book the visit</h3><p>You pick a time that works. We show up, get it done and clean up.</p></li>
      </ol>
    </div>
  </section>

{quote_block(root, "Send us a message", "Contact")}

  <section aria-labelledby="where-title">
    <div class="wrap contact-where">
      <figure class="contact-van"><img src="images/hero/hero-handyman.webp" width="2000" height="1125" loading="lazy" alt="Busy Beaver Handyman van parked outside a Lexington home"></figure>
      <div>
        <h2 id="where-title">Where we work</h2>
        <p class="note">Based in Lexington and on the road every day to the towns around it.</p>
{town_links(root)}
        <p class="note" style="margin-top:14px">Not on the list? <a href="service-areas.html">Check your area</a> or just ask.</p>
      </div>
    </div>
  </section>"""
    render("contact.html", "Contact | Busy Beaver Handyman, Lexington KY",
           "Contact Busy Beaver Handyman in Lexington, KY. Call, text, send photos or request a free estimate. Reply within 1 business day.",
           main, root)


# ---------- blog ----------

POSTS_SORTED = sorted(POSTS, key=lambda p: p["date"], reverse=True)


def read_time(post):
    words = sum(len((b[1] if isinstance(b[1], str) else " ".join(b[1])).split()) for b in post["body"])
    return max(2, math.ceil(words / 200))


def nice_date(d):
    return datetime.date.fromisoformat(d).strftime("%B %-d, %Y")


def post_image(root, post, cls=""):
    img = ROOT / "images" / "blog" / f"{post['slug']}.webp"
    if img.exists():
        return f'<img src="{root}images/blog/{post["slug"]}.webp" width="1600" height="900" loading="lazy" alt="">'
    return f'<div class="post-art {cls}" aria-hidden="true">{icon(post["icon"])}</div>'


def inline(root, text):
    text = esc(text)
    def link(m):
        target, label = m.group(1), m.group(2)
        href = target if target.startswith("#") else f"{root}services/{target}.html"
        return f'<a href="{href}">{label}</a>'
    return re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", link, text)


def post_body(root, post):
    out = []
    for kind, val in post["body"]:
        if kind == "h2":
            out.append(f"        <h2>{esc(val)}</h2>")
        elif kind == "p":
            out.append(f"        <p>{inline(root, val)}</p>")
        elif kind == "ul":
            out.append("        <ul>" + "".join(f"<li>{inline(root, i)}</li>" for i in val) + "</ul>")
        elif kind == "tip":
            out.append(f'        <div class="tip">{icon("i-check")}<p><strong>Tip:</strong> {inline(root, val)}</p></div>')
    return "\n".join(out)


def post_cards(root, posts, cta=False):
    items = []
    for p in posts:
        items.append(f"""        <li><article class="post">
          {post_image(root, p)}
          <div class="post-body">
            <p class="post-meta">{esc(p["category"])} · {read_time(p)} min read</p>
            <h3><a href="{root}blog/{p["slug"]}.html">{esc(p["title"])}</a></h3>
            <p>{esc(p["summary"])}</p>
            <span class="read-more" aria-hidden="true">Read article{icon("i-arrow")}</span>
          </div>
        </article></li>""")
    if cta and len(posts) % 3:
        items.append(f"""        <li><div class="post post-cta">
          <img src="{root}images/brand/mascot.webp" width="620" height="687" alt="" loading="lazy">
          <h3>Rather not DIY it?</h3>
          <p>Send us a few photos of the job. You'll get a clear price within 1 business day.</p>
          <a class="btn btn-yellow" href="#quote">Get a Free Estimate</a>
          <a class="cta-offer" href="#offer" data-open-offer data-offer-only>New customer? $50 off your first job</a>
        </div></li>""")
    return '      <ul class="blog-grid">\n' + "\n".join(items) + "\n      </ul>"


def build_blog_hub():
    root = ""
    top, rest = POSTS_SORTED[0], POSTS_SORTED[1:]
    main = page_hero(root, [("Blog", "")], "Homeowner tips from Busy Beaver",
                     "Seasonal checklists, how-tos and straight answers about home repairs in Central Kentucky.",
                     kicker="Blog", kicker_icon="s-leaf") + f"""

  <section aria-labelledby="latest-title">
    <div class="wrap">
      <h2 id="latest-title" class="vh">Latest article</h2>
      <a class="featured" href="blog/{top["slug"]}.html">
        {post_image(root, top)}
        <div class="featured-body">
          <p class="post-meta">Latest · {esc(top["category"])} · {read_time(top)} min read</p>
          <h2>{esc(top["title"])}</h2>
          <p>{esc(top["summary"])}</p>
          <span class="read-more">Read article{icon("i-arrow")}</span>
        </div>
      </a>
    </div>
  </section>

  <section class="alt" aria-labelledby="all-title">
    <div class="wrap">
      <div class="section-head"><h2 id="all-title">All articles</h2></div>
{post_cards(root, rest, cta=True)}
    </div>
  </section>

{quote_block(root, "Rather have us do it?", "Blog")}"""
    render("blog.html", "Homeowner Tips & Guides | Busy Beaver Handyman Blog",
           "Seasonal maintenance checklists, repair how-tos and handyman advice for homeowners in Lexington and Central Kentucky.",
           main, root)


def build_post(post):
    root = "../"
    chips = "".join(f'<li><a href="{root}services/{s}.html">{esc(SERVICE_BY_SLUG[s]["name"])}</a></li>' for s in post["services"])
    more = [p for p in POSTS_SORTED if p["slug"] != post["slug"]][:3]
    schema = f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BlogPosting","headline":{json_str(post["title"])},"description":{json_str(post["summary"])},"datePublished":"{post["date"]}","author":{{"@type":"Organization","name":"Busy Beaver Handyman"}},"publisher":{{"@type":"Organization","name":"Busy Beaver Handyman"}},"mainEntityOfPage":"https://{DOMAIN}/blog/{post["slug"]}"}}
</script>
"""
    main = f"""  <div class="page-hero article-hero on-choc">
    <div class="wrap">
      <nav class="breadcrumb" aria-label="Breadcrumb"><a href="{root}index.html">Home</a> <span aria-hidden="true">/</span> <a href="{root}blog.html">Blog</a> <span aria-hidden="true">/</span> <span aria-current="page">{esc(post["category"])}</span></nav>
      <p class="meta"><span>{esc(post["category"])}</span><span>{read_time(post)} min read</span><span>{nice_date(post["date"])}</span></p>
      <h1>{esc(post["title"])}</h1>
      <p class="lede">{esc(post["summary"])}</p>
    </div>
  </div>

  <section aria-label="Article">
    <div class="wrap">
      <figure class="article-figure">{post_image(root, post)}</figure>
      <div class="content-grid">
        <article class="prose">
{post_body(root, post)}
          <div class="callout">
            <img src="{root}images/brand/mascot.webp" width="620" height="687" alt="">
            <div>
              <strong>Rather not DIY it?</strong>
              <p>Busy Beaver can take care of it. Send a few photos and get a clear price, usually within 1 business day.</p>
              <a class="btn btn-yellow btn-sm" href="#quote">Get a Free Estimate</a>
            </div>
          </div>
          <h2>Related services</h2>
          <ul class="chips">{chips}</ul>
        </article>
{aside_card(root)}
      </div>
    </div>
  </section>

  <section class="alt" aria-labelledby="more-posts">
    <div class="wrap">
      <div class="section-head"><h2 id="more-posts">More homeowner tips</h2></div>
{post_cards(root, more)}
    </div>
  </section>

{quote_block(root, "Get a quote for this job", "Blog: " + post["title"])}"""
    render(f"blog/{post['slug']}.html", f"{post['title']} | Busy Beaver Handyman",
           post["summary"], main, root, schema=schema)


def json_str(text):
    import json
    return json.dumps(text)


# ---------- property managers & about ----------

def pm_figure(root, slug, alt, cls="article-figure"):
    if not (ROOT / "images" / "pm" / f"{slug}.webp").exists():
        return ""
    return f'<figure class="{cls}"><img src="{root}images/pm/{slug}.webp" width="1600" height="900" loading="lazy" alt="{esc(alt)}"></figure>'


def build_property_managers():
    root = ""
    checklist = "\n".join(f'          <li>{icon("i-check")}{esc(i)}</li>' for i in [
        "Make-ready and turnover repairs between tenants",
        "Drywall patches and paint touch-ups",
        "Locks and deadbolts replaced for new tenants",
        "Doors, cabinets and hardware adjusted or replaced",
        "Light fixtures, faucets and bath hardware swapped",
        "Smoke and CO detectors checked and replaced",
        "Gutter cleaning and small exterior repairs",
        "Junk and leftover furniture hauled away",
    ])
    main = page_hero(root, [("Property Managers", "")], "Handyman help for property managers and landlords",
                     "Turnovers, work orders and the punch-list items that keep rentals ready. Send the list with photos and get a clear price within 1 business day.",
                     kicker="Property Managers", kicker_icon="s-door",
                     bg="images/pm/turnover.webp" if (ROOT / "images/pm/turnover.webp").exists() else HERO_BG_DEFAULT) + f"""

  <section aria-labelledby="pm-what">
    <div class="wrap content-grid">
      <div class="prose">
        <h2 id="pm-what">What we handle for rentals</h2>
        <ul class="checklist">
{checklist}
        </ul>
        <h2>How it works with us</h2>
        {pm_figure(root, "keys", "Property manager handing rental keys to a handyman", "prose-figure")}
        <p>Send the work order the way you already write it: the address, what needs doing, photos if you have them, and how we get in (lockbox, tenant contact or office pickup). We'll reply within 1 business day with a price for the whole list.</p>
        <p>Once you approve, we schedule the work and let you know when it's done. If we find something on site that wasn't on the list, we check with you before doing extra work.</p>
        <h2>Where we work</h2>
        <p>Rentals in Lexington and nearby towns, including Richmond, Georgetown, Nicholasville, Winchester, Versailles and Paris. See all <a href="service-areas.html">service areas</a>.</p>
      </div>
{aside_card(root)}
    </div>
  </section>

  <section class="alt" aria-labelledby="pm-services">
    <div class="wrap">
      <div class="section-head"><h2 id="pm-services">Most requested for rentals</h2></div>
{service_cards(root, ["drywall-repair", "painting", "doors-and-locks", "general-repairs", "lights-and-fixtures", "junk-removal"])}
    </div>
  </section>

{quote_block(root, "Send us a work order", "Property Managers")}"""
    render("property-managers.html", "Handyman for Property Managers & Landlords in Lexington, KY | Busy Beaver",
           "Make-ready repairs, turnovers and work orders for rental properties in Lexington and nearby Kentucky towns. Clear prices within 1 business day.",
           main, root)


def build_privacy():
    root = ""
    def sec(title, *paras):
        out = f"        <h2>{esc(title)}</h2>\n"
        for p in paras:
            if isinstance(p, list):
                out += "        <ul>" + "".join(f"<li>{x}</li>" for x in p) + "</ul>\n"
            else:
                out += f"        <p>{p}</p>\n"
        return out
    body = (
        '        <p class="updated">Last updated: October 17, 2026</p>\n'
        "        <p>This policy explains what information Busy Beaver Handyman collects through this website, how we use it, and the choices you have. We keep it short and plain.</p>\n"
        + sec("Information you give us",
              "When you request an estimate, contact us or chat with our website helper, you may give us:",
              ["Your name, phone number and email address",
               "Your town and ZIP code",
               "A description of the work you need",
               "Photos of the job you choose to upload",
               "Whether you claimed a website offer, such as the new customer discount"])
        + sec("Information collected automatically",
              "Like most websites, our hosting provider records basic technical data such as your browser type, device type and the pages you visit. "
              "Our website also saves a small note in your browser so the new customer offer doesn't keep popping up. "
              "If we use analytics or advertising tools such as Google Analytics or Google Ads, they may use cookies to measure visits and ad results. "
              "You can block or delete cookies in your browser settings.")
        + sec("How we use your information",
              ["To reply to your request and prepare an estimate",
               "To schedule and complete the work",
               "To contact you about your job by phone, text or email",
               "To apply offers you claimed",
               "To improve our website and understand which ads bring customers"])
        + sec("Who we share it with",
              "We do not sell your personal information. We share it only with services that help us run the business, such as our website host and form provider, email and phone providers, and advertising and analytics tools. These services may only use it to provide their service to us. We may also share information if the law requires it.")
        + sec("Text messages",
              "If you give us your phone number, we may call or text you about your estimate and job. We don't send marketing texts without your consent. Reply STOP to any text to stop receiving them.")
        + sec("How long we keep it",
              "We keep estimate requests and job records as long as we need them to serve you and keep normal business records, then delete them.")
        + sec("Your choices",
              f'You can ask us to see, correct or delete the personal information we hold about you. Email us at <a data-email href="#" data-email-label></a> or call or text <a data-tel href="#" data-phone></a>.')
        + sec("Children",
              "Our website is meant for adults. We don't knowingly collect information from children under 13.")
        + sec("Changes to this policy",
              "If we update this policy, we'll change the date at the top of this page.")
        + sec("Contact",
              f'Busy Beaver Handyman, Lexington, Kentucky. Email <a data-email href="#" data-email-label></a>, phone <a data-tel href="#" data-phone></a>.')
    )
    main = page_hero(root, [("Privacy Policy", "")], "Privacy Policy",
                     "What we collect when you contact us, how we use it, and your choices.", kicker="Busy Beaver Handyman", kicker_icon="i-shield") + f"""

  <section aria-label="Privacy policy">
    <div class="wrap">
      <article class="prose legal">
{body}      </article>
    </div>
  </section>"""
    render("privacy.html", "Privacy Policy | Busy Beaver Handyman", "How Busy Beaver Handyman collects, uses and protects information you share through our website.", main, root)


def build_about():
    root = ""
    main = page_hero(root, [("About", "")], "About Busy Beaver Handyman",
                     "A local handyman service for homes in Lexington and the Central Kentucky towns around it.",
                     kicker="About us", kicker_icon="i-pin") + f"""

  <section aria-labelledby="about-title">
    <div class="wrap content-grid">
      <div class="prose">
        <h2 id="about-title">Why we do this</h2>
        <p>Every house has a list. The closet door that won't stay shut, the TV still leaning against the wall, the hole from the old curtain rod. None of it is big enough for a contractor, and all of it is easy to put off.</p>
        <p>Busy Beaver Handyman exists for that list. We show up, get through it properly and leave the place clean. Like the beaver on our logo, we like work that's done right and built to last.</p>
        <!-- OWNER STORY: add the owner's name, a short real story and a real photo here -->
        <h2>What you can count on</h2>
        <ul class="checklist">
          <li>{icon("i-check")}A clear price before any work starts</li>
          <li>{icon("i-check")}A reply within 1 business day</li>
          <li>{icon("i-check")}Insured work</li>
          <li>{icon("i-check")}A clean space when we leave</li>
          <li>{icon("i-check")}Straight answers, including when a job needs a specialist</li>
          <li>{icon("i-check")}Local to Lexington and nearby towns</li>
        </ul>
      </div>
      <aside class="side-card" aria-label="Get a quote">
        <img src="{root}images/brand/mascot.webp" width="620" height="687" alt="Busy Beaver mascot" style="width:140px">
        <h2>Meet the beaver</h2>
        <p style="color:var(--ink-2);margin:0 0 18px">Busy, careful and a little proud of his teeth. He's our mascot, and our standard.</p>
        <a class="btn btn-yellow" href="#quote">Get a Free Estimate</a>
      </aside>
    </div>
  </section>

{steps_block()}

{quote_block(root, "Let's take care of your list", "About")}"""
    render("about.html", "About | Busy Beaver Handyman, Lexington KY",
           "Busy Beaver Handyman is a local handyman service for homes in Lexington and nearby Central Kentucky towns.",
           main, root)


def build_thank_you():
    # Absolute paths: Netlify serves this from the site root
    root = "/"
    picks = POSTS_SORTED[:3]
    main = f"""  <div class="ty-hero">
    <div class="wrap ty-grid">
      <div>
        <p class="pill-label"><span class="dot" aria-hidden="true"></span>Request received</p>
        <h1>Thanks! Your request is <span class="hl-under">in.</span></h1>
        <p class="lede">A real person will look at your job and reply within 1 business day, usually with a price, sometimes with a quick question.</p>
        <ol class="ty-steps">
          <li><strong>We review your photos and details</strong><span>Today or the next business day.</span></li>
          <li><strong>You get a clear price</strong><span>By text, call or email, whichever you gave us.</span></li>
          <li><strong>You pick a time</strong><span>We show up, get it done and clean up.</span></li>
        </ol>
        <div class="hero-actions">
          <a class="btn btn-yellow" href="{root}index.html">Back to home</a>
          <a class="btn btn-outline-dark" data-tel href="#">{icon("i-phone")}Need it sooner? Call</a>
        </div>
        <p class="ty-offer" data-offer-only>Claimed the new customer deal? It's noted on your request. You'll see $50 off your first job.</p>
      </div>
      <img class="ty-beaver" src="{root}images/brand/mascot.webp" width="620" height="687" alt="Busy Beaver mascot giving a thumbs up">
    </div>
  </div>

  <section class="alt" aria-labelledby="ty-read">
    <div class="wrap">
      <div class="section-head"><h2 id="ty-read">While you wait</h2><p>A few tips homeowners find useful.</p></div>
{post_cards(root, picks)}
    </div>
  </section>
  <!-- Google Ads conversion tag goes here when the Ads account is set up -->"""
    render("thank-you.html", "Thank You | Busy Beaver Handyman", "Your estimate request was received.", main, root, noindex=True)


def build_404():
    root = "/"
    main = f"""  <div class="ty-hero">
    <div class="wrap ty-grid">
      <div>
        <p class="pill-label"><span class="dot" aria-hidden="true"></span>Error 404</p>
        <h1>This page got <span class="hl-under">chewed up.</span></h1>
        <p class="lede">The link may be old or mistyped. Let's get you where you were going.</p>
        <div class="hero-actions">
          <a class="btn btn-yellow" href="{root}index.html">Go to the home page</a>
          <a class="btn btn-outline-dark" href="{root}services.html">See our services</a>
        </div>
        <ul class="chips" style="margin-top:22px">
          <li><a href="{root}service-areas.html">Service areas</a></li>
          <li><a href="{root}blog.html">Blog</a></li>
          <li><a href="{root}contact.html">Contact</a></li>
          <li><a href="{root}index.html#quote">Get a free estimate</a></li>
        </ul>
      </div>
      <img class="ty-beaver" src="{root}images/brand/mascot.webp" width="620" height="687" alt="">
    </div>
  </div>"""
    render("404.html", "Page Not Found | Busy Beaver Handyman", "This page could not be found.", main, root, noindex=True)


def build_sitemap(paths):
    urls = "\n".join(f"  <url><loc>https://{DOMAIN}/{p.replace('index.html', '').replace('.html', '')}</loc></url>" for p in paths)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: https://{DOMAIN}/sitemap.xml\n")


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    for d in ("assets", "images"):
        shutil.copytree(ROOT / d, DIST / d)
    for f in ("favicon-32.png", "apple-touch-icon.png"):
        shutil.copy(ROOT / f, DIST / f)
    build_home()
    build_services_hub()
    for s in SERVICES:
        build_service(s)
    build_areas_hub()
    for t in TOWNS:
        build_town(t)
    build_contact()
    build_blog_hub()
    build_property_managers()
    build_about()
    build_privacy()
    build_thank_you()
    build_404()
    for p in POSTS:
        build_post(p)
    pages = sorted(str(p.relative_to(DIST)) for p in DIST.rglob("*.html"))
    seo_pages = [p for p in pages if p not in ("thank-you.html", "404.html")]
    build_sitemap(seo_pages)
    print(f"Built {len(pages)} pages into dist/")


if __name__ == "__main__":
    main()
