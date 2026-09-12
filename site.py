"""Build Hongli Liu's editorial academic homepage."""
from datetime import date
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


DATA = load_json("site.json")
INTERESTS = load_json("data/themes.json")
PROJECTS = load_json("data/projects.json")
READINGS = load_json("data/readings.json")
PUBLICATIONS = {item["id"]: item for item in DATA["publications"]}


def e(value):
    return escape(str(value), quote=True)


def bibtex(pub):
    return (
        f"@article{{{pub['id']},\n"
        f"  author = {{{pub['bib_authors']}}},\n"
        f"  title = {{{{{pub['title']}}}}},\n"
        f"  journal = {{{pub['journal']}}},\n"
        f"  year = {{{pub['year']}}},\n"
        f"  volume = {{{pub['volume']}}},\n"
        f"  pages = {{{pub['pages'].replace('–', '--')}}},\n"
        f"  doi = {{{pub['doi']}}}\n}}"
    )


def link(label, href, class_name=""):
    if not href:
        return ""
    external = href.startswith("http")
    attrs = ' target="_blank" rel="noopener noreferrer"' if external else ""
    css = f' class="{e(class_name)}"' if class_name else ""
    return f'<a{css} href="{e(href)}"{attrs}>{e(label)}</a>'


def author_line(authors):
    if len(authors) == 1:
        return authors[0]
    return ", ".join(authors[:-1]) + ", &amp; " + authors[-1]


def interest_entry(item):
    return f'''<article class="interest-entry">
      <h3>{e(item['title'])}</h3>
      <p>{e(item['text'])}</p>
    </article>'''


def research_entry(item):
    if item["source"] == "publication":
        pub = PUBLICATIONS[item["publication_id"]]
        doi_url = "https://doi.org/" + pub["doi"]
        meta = f"Journal article · {pub['journal']} · {pub['year']}"
        doi_link = link(doi_url, doi_url, "citation-doi")
        citation = (
            f"{author_line(pub['authors'])} ({e(pub['year'])}). "
            f"{e(pub['title'])}. <em>{e(pub['journal'])}</em>, "
            f"<em>{e(pub['volume'])}</em>, {e(pub['pages'])}. {doi_link}"
        )
        title_html = link(item["title"], doi_url, "research-title-link")
    else:
        presentation = DATA["presentation"]
        meta = f"{item['meta']} · {presentation['year']}"
        citation = f"{presentation['venue']}. <em>{presentation['theme']}</em>."
        title_html = e(item["title"])

    methods = " · ".join(item["methods"])
    return f'''<article class="research-entry">
      <header class="research-header">
        <div><h3>{title_html}</h3><p class="research-subtitle">{e(item['subtitle'])}</p></div>
        <p class="research-meta">{e(meta)}</p>
      </header>
      <div class="research-body">
        <p class="research-question">{e(item['question'])}</p>
        <p>{e(item['text'])}</p>
        <p class="research-citation">{citation}</p>
        <p class="research-methods"><span>Methods:</span> {e(methods)}</p>
      </div>
    </article>'''


def reading_entry(item):
    title = link(item["title"], item.get("url", "")) or e(item["title"])
    note_label = item.get("note_label") or "Why I’m reading this"
    return f'''<article class="reading-entry">
      <h3>{title}</h3>
      <p class="reading-meta">{e(item['authors'])} · {e(item['year'])} · {e(item['venue'])}</p>
      <p><span>{e(note_label)}:</span> {e(item['note'])}</p>
    </article>'''


def render():
    d = DATA
    role = d["position"]
    version = e(d["asset_version"])
    profile = d["images"]["profile"]
    hobbies = d["images"]["hobbies"]
    for image in [profile, *hobbies]:
        if not (ROOT / image["file"]).is_file():
            raise FileNotFoundError(f"Missing image: {ROOT / image['file']}")

    about_links = [
        ("CV", d["links"].get("cv")),
        ("Google Scholar", d["links"].get("scholar")),
        ("GitHub", d["github"]),
        ("Email", "mailto:" + d["email"]),
    ]
    about_link_html = ' <span aria-hidden="true">·</span> '.join(
        link(label, href) for label, href in about_links if href
    )

    nav_items = [
        ("About Me", "#about"),
        ("Interests", "#interests"),
        ("Publications & Presentations", "#research"),
        ("Reading", "#reading"),
        ("Hobbies", "#hobbies"),
    ]
    nav_html = "".join(link(label, href) for label, href in nav_items)

    interests_html = "".join(interest_entry(item) for item in INTERESTS)
    research_html = "".join(research_entry(item) for item in PROJECTS)

    if READINGS:
        readings_html = "".join(reading_entry(item) for item in READINGS)
    else:
        readings_html = '<p class="reading-empty">waiting</p>'

    hobby_images_html = "".join(
        f'<figure><img src="./{e(item["file"])}?v={version}" alt="{e(item["alt"])}" width="{e(item["width"])}" height="{e(item["height"])}"></figure>'
        for item in hobbies
    )

    background_html = e(d["background"])
    for item in d.get("background_links", []):
        if item.get("url"):
            linked_name = (
                f'<a href="{e(item["url"])}" target="_blank" rel="noopener noreferrer">'
                f'<strong>{e(item["name"])}</strong></a>'
            )
            background_html = background_html.replace(e(item["name"]), linked_name)
    structured = json.dumps({
        "@context": "https://schema.org",
        "@type": "Person",
        "name": d["name"],
        "url": d["url"],
        "image": d["url"] + "/" + profile["file"],
        "jobTitle": role["title"],
        "worksFor": {"@type": "Organization", "name": role["institution"], "url": role["institution_url"]},
        "sameAs": [value for value in [d["github"], d["links"].get("scholar")] if value],
        "knowsAbout": [item["title"] for item in INTERESTS],
    }, ensure_ascii=False).replace("<", "\\u003c")
    description = "Hongli Liu studies language comprehension through psycholinguistics, cognitive neuroscience, and computational modeling."

    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Hongli Liu | Psycholinguistics &amp; Cognitive Neuroscience</title>
  <meta name="description" content="{e(description)}"><meta name="author" content="{e(d['name'])}">
  <meta name="theme-color" content="#ffffff"><meta name="referrer" content="strict-origin-when-cross-origin">
  <link rel="canonical" href="{e(d['url'])}/"><meta property="og:type" content="profile">
  <meta property="og:title" content="Hongli Liu | Psycholinguistics &amp; Cognitive Neuroscience">
  <meta property="og:description" content="{e(description)}"><meta property="og:url" content="{e(d['url'])}/">
  <meta property="og:locale" content="en_US"><meta name="twitter:card" content="summary">
  <link rel="icon" type="image/svg+xml" href="./assets/favicon.svg?v={version}">
  <link rel="stylesheet" href="./assets/main.css?v={version}">
  <script defer src="./assets/main.js?v={version}"></script><script type="application/ld+json">{structured}</script>
</head>
<body id="top">
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="top-nav"><div class="site-width nav-inner">
    <a class="wordmark" href="#top">Hongli Liu</a>
    <nav aria-label="Main navigation">{nav_html}</nav>
  </div></header>

  <main id="main">
    <section class="about site-width" id="about" aria-labelledby="about-heading">
      <div class="about-copy">
        <h1 id="about-heading">{e(d['name'])}</h1>
        <p class="position"><span>{e(role['title'])}</span><br><a href="{e(role['institution_url'])}" target="_blank" rel="noopener noreferrer">{e(role['institution'])}</a></p>
        <p class="identity-line">{e(d['identity_line'])}</p>
        <p class="research-intro">{e(d['research_statement'])}</p>
        <p class="background">{background_html}</p>
        <p class="about-links">{about_link_html}</p>
      </div>
      <figure class="about-portrait"><img src="./{e(profile['file'])}?v={version}" alt="{e(profile['alt'])}" width="1280" height="1703"></figure>
    </section>

    <section class="section site-width" id="interests" aria-labelledby="interests-heading">
      <h2 id="interests-heading">Research Interests</h2>
      <p class="section-intro">My research centers on how linguistic representations emerge during comprehension and how theoretically defined linguistic categories relate to more continuous properties of linguistic experience.</p>
      <div class="interest-list">{interests_html}</div>
    </section>

    <section class="section site-width" id="research" aria-labelledby="research-heading">
      <h2 id="research-heading">Publications &amp; Presentations</h2>
      <div class="research-list">{research_html}</div>
    </section>

    <section class="section site-width" id="reading" aria-labelledby="reading-heading">
      <h2 id="reading-heading">Recent Reading</h2>
      <!-- Reading entry format: edit data/readings.json, then run python site.py.
      [
        {{
          "title": "Paper title",
          "authors": "Authors",
          "year": "2026",
          "venue": "Journal or conference",
          "url": "https://doi.org/...",
          "note_label": "Why I’m reading this",
          "note": "One short sentence."
        }}
      ]
      -->
      {readings_html}
    </section>

    <section class="section hobbies-section site-width" id="hobbies" aria-labelledby="hobbies-heading">
      <div class="hobbies-layout">
        <div><h2 id="hobbies-heading">{e(d['personal']['heading'])}</h2><p>{e(d['personal']['text'])}</p></div>
        <div class="hobby-photos">{hobby_images_html}</div>
      </div>
    </section>

    <section class="section message-section site-width" id="message" aria-labelledby="message-heading">
      <h2 id="message-heading">{e(d['message']['heading'])}</h2>
      <p class="section-intro">{e(d['message']['text'])}</p>
      <form class="message-form" data-message-form action="https://formsubmit.co/{e(d['email'])}" method="post">
        <input type="hidden" name="_subject" value="Message from academic homepage">
        <input type="hidden" name="_next" value="{e(d['url'])}/?message=sent#message">
        <input type="hidden" name="_url" value="{e(d['url'])}/#message">
        <label class="form-honey" aria-hidden="true">Leave this field empty<input type="text" name="_honey" tabindex="-1" autocomplete="off"></label>
        <label class="sr-only" for="message-text">Message</label><textarea id="message-text" name="message" rows="7" required maxlength="2000" placeholder="Your message"></textarea>
        <div class="form-actions"><button type="submit">Send</button></div>
        <p class="form-note">You can leave this message anonymously. <a href="https://formsubmit.co/privacy.pdf" target="_blank" rel="noopener noreferrer">Privacy information</a></p>
        <p class="message-status" data-message-status role="status" aria-live="polite"></p>
      </form>
      <p class="message-email"><a href="mailto:{e(d['email'])}">{e(d['email'])}</a></p>
    </section>
  </main>

  <footer class="site-footer"><div class="site-width"><p>© {date.fromisoformat(d['updated']).year} {e(d['name'])}</p><a href="#top">Back to top</a></div></footer>
</body>
</html>'''
    return "\n".join(line.rstrip() for line in html.splitlines()) + "\n"


def legacy_redirect():
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hongli Liu — English homepage</title><meta name="robots" content="noindex">
<link rel="canonical" href="https://liuhongli775.github.io/"><meta http-equiv="refresh" content="0;url=../index.html">
<script>const map={'#home':'#about','#themes':'#interests','#computational':'#research','#notes':'#reading','#publications':'#research','#materials':'#about','#beyond':'#hobbies','#contact':'#message','#message':'#message','#background':'#about'};window.location.replace('../index.html'+(map[location.hash]||location.hash));</script>
</head><body><p>This homepage is now in English. <a href="../index.html">Continue to Hongli Liu’s homepage</a>.</p></body></html>
'''


def build():
    (ROOT / "index.html").write_text(render(), encoding="utf-8", newline="\n")
    (ROOT / "zh").mkdir(exist_ok=True)
    (ROOT / "zh/index.html").write_text(legacy_redirect(), encoding="utf-8", newline="\n")
    papers = sorted(DATA["publications"], key=lambda item: item["date"], reverse=True)
    (ROOT / "publications.bib").write_text("\n\n".join(bibtex(item) for item in papers) + "\n", encoding="utf-8", newline="\n")
    (ROOT / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: " + DATA["url"] + "/sitemap.xml\n", encoding="utf-8")
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>' + e(DATA["url"]) + "/</loc></url></urlset>\n", encoding="utf-8")
    print("Built the editorial academic homepage.")


if __name__ == "__main__":
    build()
