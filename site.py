"""Build Hongli Liu's research-focused academic homepage."""
from datetime import date
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


DATA = load_json("site.json")
THEMES = load_json("data/themes.json")
PROJECTS = load_json("data/projects.json")
QUESTIONS = load_json("data/questions.json")
READINGS = load_json("data/readings.json")


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


def project_links(items):
    return "".join(link(item["label"] + " ↗" if item["href"].startswith("http") else item["label"], item["href"]) for item in items)


def tags(items):
    return "".join(f"<li>{e(item)}</li>" for item in items)


def publication_entry(pub):
    authors = []
    for author in pub["authors"]:
        authors.append(f"<strong>{e(author)}</strong>" if author == "Liu, H." else e(author))
    author_line = ", ".join(authors[:-1]) + ", &amp; " + authors[-1]
    return f'''<li class="publication-entry">
      <p class="publication-year">{e(pub['year'])}</p>
      <div><p class="publication-authors">{author_line}</p>
        <h3><a href="https://doi.org/{e(pub['doi'])}" target="_blank" rel="noopener noreferrer">{e(pub['title'])}</a></h3>
        <p class="publication-venue"><em>{e(pub['journal'])}, {e(pub['volume'])}</em>, {e(pub['pages'])}.</p>
        <div class="publication-links"><a href="https://doi.org/{e(pub['doi'])}" target="_blank" rel="noopener noreferrer">Paper ↗</a>
          <details class="citation"><summary>BibTeX<span class="sr-only"> for {e(pub['title'])}</span></summary>
            <pre id="{e(pub['id'])}" tabindex="0">{e(bibtex(pub))}</pre>
            <button type="button" class="copy-button js-only" data-copy="{e(pub['id'])}">Copy citation</button><span class="copy-status" role="status" aria-live="polite"></span>
          </details>
        </div>
      </div>
    </li>'''


def render():
    d = DATA
    role = d["position"]
    version = e(d["asset_version"])
    profile = d["images"]["profile"]
    activities = d["images"]["activities"]
    for image in [profile, *activities]:
        if not (ROOT / image["file"]).is_file():
            raise FileNotFoundError(f"Missing image: {ROOT / image['file']}")

    hero_links = [
        ("CV", d["links"].get("cv")),
        ("Google Scholar", d["links"].get("scholar")),
        ("GitHub", d["github"]),
        ("Email", "mailto:" + d["email"]),
    ]
    hero_link_html = "".join(link(label, href) for label, href in hero_links if href)
    nav_items = [("Home", "#home"), ("Research", "#research"), ("Publications", "#publications"), ("Notes", "#notes"), ("About", "#about")]
    if d["links"].get("cv"):
        nav_items.append(("CV", d["links"]["cv"]))
    nav_html = "".join(link(label, href) for label, href in nav_items)

    themes_html = "".join(
        f'''<article class="theme"><span>{index:02d}</span><h3>{e(item['title'])}</h3><p>{e(item['text'])}</p></article>'''
        for index, item in enumerate(THEMES, 1)
    )

    selected = PROJECTS["selected_research"]
    featured = selected[0]
    featured_html = f'''<article class="featured-project">
      <div class="project-kicker"><span>Current focus</span><span>01</span></div>
      <div class="featured-content"><p class="project-subtitle">{e(featured['subtitle'])}</p><h3>{e(featured['title'])}</h3>
        <p class="research-question">{e(featured['question'])}</p><p>{e(featured['text'])}</p>
        <ul class="tag-list">{tags(featured['methods'])}</ul><div class="text-links">{project_links(featured['links'])}</div>
      </div>
    </article>'''
    secondary_html = "".join(
        f'''<article class="research-card"><p class="project-subtitle">{e(item['subtitle'])}</p><h3>{e(item['title'])}</h3>
          <p class="research-question">{e(item['question'])}</p><p>{e(item['text'])}</p>
          <ul class="tag-list">{tags(item['methods'])}</ul><div class="text-links">{project_links(item['links'])}</div>
        </article>'''
        for item in selected[1:]
    )

    computational_html = "".join(
        f'''<article class="computational-card"><div class="card-heading"><p>{e(item['status'])}</p><h3>{e(item['title'])}</h3></div>
          <dl><div><dt>Research problem</dt><dd>{e(item['problem'])}</dd></div>
            <div><dt>Data / model</dt><dd>{e(item['data'])}</dd></div>
            <div><dt>Method</dt><dd>{e(item['method'])}</dd></div>
            <div><dt>Output</dt><dd>{e(item['output'])}</dd></div></dl>
        </article>'''
        for item in PROJECTS["computational_projects"]
    )

    questions_html = "".join(
        f'<li><span>{index:02d}</span><p>{e(question)}</p></li>'
        for index, question in enumerate(QUESTIONS, 1)
    )
    if READINGS:
        readings_html = "".join(
            f'''<article class="reading-entry"><p class="reading-meta">{e(item['authors'])} · {e(item['year'])}</p>
              <h3><a href="{e(item['url'])}" target="_blank" rel="noopener noreferrer">{e(item['title'])}</a></h3>
              <p class="reading-venue">{e(item['venue'])}</p><p><strong>{e(item['note_label'])}:</strong> {e(item['note'])}</p>
            </article>'''
            for item in READINGS
        )
    else:
        readings_html = '''<div class="reading-placeholder"><p>Reading notes will appear here.</p></div>'''

    publications = sorted(d["publications"], key=lambda item: item["date"], reverse=True)
    publications_html = "".join(publication_entry(pub) for pub in publications)
    poster = d["presentation"]
    poster_html = f'''<li class="publication-entry presentation-entry" id="presentation">
      <p class="publication-year">{e(poster['year'])}</p><div><p class="publication-authors">{e(poster['type'])}</p>
        <h3>{e(poster['title'])}</h3><p class="publication-venue">{e(poster['venue'])}. <em>{e(poster['theme'])}</em>.</p>
      </div>
    </li>'''

    education_html = "".join(
        f'''<article><p>{e(item['dates'])}</p><h3>{e(item['title'])}</h3>
          <a href="{e(item['institution_url'])}" target="_blank" rel="noopener noreferrer">{e(item['institution'])}</a></article>'''
        for item in d["education"]
    )
    activities_html = "".join(
        f'<figure><img src="./{e(item["file"])}?v={version}" alt="{e(item["alt"])}" width="{e(item["width"])}" height="{e(item["height"])}"></figure>'
        for item in activities
    )
    resource = d["materials"][0]
    resource_path = ROOT / resource["file"]
    if not resource_path.is_file():
        raise FileNotFoundError(f"Missing material: {resource_path}")
    resource_size = f"{resource_path.stat().st_size / (1024 * 1024):.1f} MB"

    structured = json.dumps({
        "@context": "https://schema.org", "@type": "Person", "name": d["name"], "url": d["url"],
        "image": d["url"] + "/" + profile["file"], "jobTitle": role["title"],
        "worksFor": {"@type": "Organization", "name": role["institution"], "url": role["institution_url"]},
        "sameAs": [value for value in [d["github"], d["links"].get("scholar")] if value],
        "knowsAbout": [theme["title"] for theme in THEMES],
    }, ensure_ascii=False).replace("<", "\\u003c")
    description = "Hongli Liu studies language comprehension through psycholinguistics, cognitive neuroscience, and computational modeling."

    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Hongli Liu | Psycholinguistics &amp; Cognitive Neuroscience</title>
  <meta name="description" content="{e(description)}"><meta name="author" content="{e(d['name'])}">
  <meta name="theme-color" content="#f7f8fa"><meta name="referrer" content="strict-origin-when-cross-origin">
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
    <a class="wordmark" href="#home" aria-label="Hongli Liu — home">HL</a>
    <nav aria-label="Main navigation">{nav_html}</nav>
    <a class="nav-email" href="mailto:{e(d['email'])}">Email ↗</a>
  </div></header>

  <main id="main">
    <section class="hero site-width" id="home" aria-labelledby="hero-heading">
      <div class="hero-copy"><p class="eyebrow">{e(role['title'])} · <a href="{e(role['institution_url'])}" target="_blank" rel="noopener noreferrer">{e(role['institution'])}</a></p>
        <h1 id="hero-heading">{e(d['name'])}</h1><p class="identity-line">{e(d['identity_line'])}</p>
        <p class="research-statement">{e(d['research_statement'])}</p><div class="hero-links">{hero_link_html}</div>
      </div>
      <figure class="hero-portrait"><img src="./{e(profile['file'])}?v={version}" alt="{e(profile['alt'])}" width="1280" height="1703"></figure>
    </section>

    <section class="themes-section site-width" id="themes" aria-labelledby="themes-heading">
      <header class="section-intro"><p class="eyebrow">Research themes</p><h2 id="themes-heading">One research program, three connected perspectives.</h2></header>
      <div class="theme-grid">{themes_html}</div>
    </section>

    <section class="section site-width" id="research" aria-labelledby="research-heading">
      <header class="section-intro"><p class="eyebrow">Selected research</p><h2 id="research-heading">Questions first. Methods in conversation.</h2>
        <p>My projects ask how categorical linguistic structure and continuous probabilistic information jointly shape behavioral and neural responses.</p></header>
      {featured_html}<div class="research-grid">{secondary_html}</div>
    </section>

    <section class="section computational-section" id="computational" aria-labelledby="computational-heading"><div class="site-width">
      <header class="section-intro"><p class="eyebrow">Selected computational projects</p><h2 id="computational-heading">Computational work as part of the science.</h2>
        <p>These research workflows connect linguistic hypotheses, computational predictors, and neural data.</p></header>
      <div class="computational-grid">{computational_html}</div>
    </div></section>

    <section class="section notes-section site-width" id="notes" aria-labelledby="notes-heading">
      <header class="section-intro"><p class="eyebrow">Research notebook</p><h2 id="notes-heading">Questions and reading notes.</h2></header>
      <div class="notes-grid"><article class="questions-panel"><p class="panel-label">Questions I’m Thinking About</p><ol>{questions_html}</ol></article>
        <article class="reading-panel"><p class="panel-label">What I’m Reading</p>{readings_html}</article></div>
    </section>

    <section class="section publications-section site-width" id="publications" aria-labelledby="publications-heading">
      <header class="section-intro publication-heading"><div><p class="eyebrow">Publications</p><h2 id="publications-heading">Research output.</h2></div>
        <a href="./publications.bib" download>Article citations (.bib) ↓</a></header>
      <ol class="publication-list">{poster_html}{publications_html}</ol>
    </section>

    <section class="section about-section" id="about" aria-labelledby="about-heading"><div class="site-width">
      <header class="section-intro"><p class="eyebrow">About</p><h2 id="about-heading">Short Bio.</h2></header>
      <div class="about-grid"><div class="bio-copy"><p>I am a {e(role['title'])} at <a href="{e(role['institution_url'])}" target="_blank" rel="noopener noreferrer">{e(role['institution'])}</a>, supervised by <a href="{e(role['supervisor_url'])}" target="_blank" rel="noopener noreferrer">Dr. {e(role['supervisor'])}</a>. I received my M.A. and B.A. from <a href="https://en.scu.edu.cn/" target="_blank" rel="noopener noreferrer">Sichuan University</a>.</p>
          <div class="education-list">{education_html}</div></div>
        <aside class="resource-card"><p class="eyebrow">Open resource</p><h3>{e(resource['title'])}</h3><p>{e(resource['subtitle'])}</p>
          <span>PDF · {e(resource['pages'])} pages · {resource_size}</span>
          <div class="text-links"><a href="./{e(resource['file'])}" target="_blank" rel="noopener noreferrer">Read ↗</a><a href="./{e(resource['file'])}" download>Download ↓</a></div></aside>
      </div>
      <div class="life-row"><div><p class="eyebrow">Beyond research</p><p>{e(d['personal']['text'])}</p></div><div class="life-images">{activities_html}</div></div>
    </div></section>

    <section class="section contact-section site-width" id="contact" aria-labelledby="contact-heading">
      <div class="contact-copy"><p class="eyebrow">Contact</p><h2 id="contact-heading">Leave an anonymous message.</h2>
        <p>You do not need to provide your name or email address. Messages are processed by FormSubmit and forwarded to my inbox.</p>
        <a href="mailto:{e(d['email'])}">{e(d['email'])}</a></div>
      <form class="message-form" data-message-form action="https://formsubmit.co/{e(d['email'])}" method="post">
        <input type="hidden" name="_subject" value="Anonymous message from academic homepage">
        <input type="hidden" name="_next" value="{e(d['url'])}/?message=sent#contact">
        <input type="hidden" name="_url" value="{e(d['url'])}/#contact">
        <label class="form-honey" aria-hidden="true">Leave this field empty<input type="text" name="_honey" tabindex="-1" autocomplete="off"></label>
        <label for="message-text">Anonymous message</label><textarea id="message-text" name="message" rows="7" required maxlength="2000" placeholder="Write your message here…"></textarea>
        <div class="form-actions"><button type="submit">Send anonymously</button><a href="https://formsubmit.co/privacy.pdf" target="_blank" rel="noopener noreferrer">Privacy information ↗</a></div>
        <p class="message-status" data-message-status role="status" aria-live="polite"></p>
      </form>
    </section>
  </main>

  <footer class="site-footer"><div class="site-width"><p>© {date.fromisoformat(d['updated']).year} {e(d['name'])}</p>
    <p>Psycholinguistics · Cognitive Neuroscience · Computational Modeling</p><a href="#top">Back to top ↑</a></div></footer>
</body>
</html>'''
    return "\n".join(line.rstrip() for line in html.splitlines()) + "\n"


def legacy_redirect():
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hongli Liu — English homepage</title><meta name="robots" content="noindex">
<link rel="canonical" href="https://liuhongli775.github.io/"><meta http-equiv="refresh" content="0;url=../index.html">
<script>const map={'#background':'#home','#research':'#research','#publications':'#publications','#materials':'#about','#beyond':'#about','#message':'#contact'};window.location.replace('../index.html'+(map[location.hash]||location.hash));</script>
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
    print("Built the research-focused academic homepage.")


if __name__ == "__main__":
    build()
