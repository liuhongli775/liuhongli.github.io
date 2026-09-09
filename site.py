"""Build Hongli Liu's English academic homepage. Python 3; no third-party dependencies."""
from datetime import date
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
SECTIONS = [
    ("background", "Background"),
    ("publications", "Publications & Presentations"),
    ("research", "Research"),
    ("honors", "Honors"),
    ("materials", "Materials"),
    ("beyond", "Beyond Research"),
    ("message", "Leave a Message"),
]


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


def ordered_outputs():
    entries = [dict(pub, kind="article") for pub in DATA["publications"]]
    entries.append(dict(DATA["presentation"], kind="poster", date=DATA["presentation"]["year"]))
    return sorted(entries, key=lambda item: item["date"], reverse=True)


def output_entry(item):
    if item["kind"] == "poster":
        return f'''<li class="output-entry conference-presentation" data-date="{e(item['date'])}">
          <p class="output-date"><time datetime="{e(item['year'])}">{e(item['year'])}</time></p>
          <div class="output-body"><p class="output-type">{e(item['type'])}</p>
            <h3>{e(item['title'])}</h3>
            <p class="output-meta">{e(item['venue'])}, {e(item['year'])}.</p>
            <p class="conference-theme">{e(item['theme'])}</p>
          </div>
        </li>'''
    authors = []
    for author in item["authors"]:
        authors.append(f"<strong>{e(author)}</strong>" if author == "Liu, H." else e(author))
    author_line = ", ".join(authors[:-1]) + ", &amp; " + authors[-1]
    return f'''<li class="output-entry publication" data-date="{e(item['date'])}">
      <p class="output-date"><time datetime="{e(item['date'])}">{e(item['date_label'])}</time></p>
      <div class="output-body"><p class="output-type">Journal article</p>
        <h3><a href="https://doi.org/{e(item['doi'])}" target="_blank" rel="noopener noreferrer">{e(item['title'])}</a></h3>
        <p class="output-meta">{author_line} ({e(item['year'])}). <em>{e(item['journal'])}, {e(item['volume'])}</em>, {e(item['pages'])}.</p>
        <div class="output-links"><a href="https://doi.org/{e(item['doi'])}" target="_blank" rel="noopener noreferrer">Paper ↗</a>
          <details class="citation"><summary>BibTeX<span class="sr-only"> for {e(item['title'])}</span></summary>
            <pre id="{e(item['id'])}" tabindex="0">{e(bibtex(item))}</pre>
            <button type="button" class="copy-button js-only" data-copy="{e(item['id'])}">Copy citation</button>
            <span class="copy-status" role="status" aria-live="polite"></span>
          </details>
        </div>
      </div>
    </li>'''


def render():
    d = DATA
    role = d["position"]
    asset_version = e(d["asset_version"])
    profile = d["images"]["profile"]
    activities = d["images"]["activities"]
    for image in [profile, *activities]:
        if not (ROOT / image["file"]).is_file():
            raise FileNotFoundError(f"Missing image: {ROOT / image['file']}")
    supervisor = f'<a href="{e(role["supervisor_url"])}" target="_blank" rel="noopener noreferrer">Dr. {e(role["supervisor"])}</a>'

    nav = "".join(
        f'<a href="#{e(section_id)}"' + (' aria-current="location"' if index == 0 else "") +
        f'>{e(label)}</a>'
        for index, (section_id, label) in enumerate(SECTIONS)
    )
    interests = "".join(f"<li>{e(item)}</li>" for item in d["interests"])
    skill_rows = "".join(
        f'<div><dt>{e(item["label"])}</dt><dd>{e(item["text"])}</dd></div>'
        for item in d["skills"]
    )
    education = []
    for index, item in enumerate(d["education"]):
        advisor = '<p>Supervisor: Dr. Feng Gu</p>' if index == 0 else ""
        education.append(
            f'''<article class="education-item"><p class="dates">{e(item['dates'])}</p>
              <div><h4>{e(item['title'])}</h4><p><a href="{e(item['institution_url'])}" target="_blank" rel="noopener noreferrer">{e(item['institution'])}</a></p>{advisor}</div></article>'''
        )

    research = []
    for item in d["research"]:
        link = (
            f'<a class="research-link" href="https://doi.org/{e(item["doi"])}" '
            f'target="_blank" rel="noopener noreferrer">Related paper ↗</a>'
            if item.get("doi") else ""
        )
        contributions = "".join(f"<li>{e(point)}</li>" for point in item["contributions"])
        research.append(
            f'''<article class="research-project"><p class="project-context">{e(item['context'])}</p>
              <h3>{e(item['title'])}</h3><p>{e(item['text'])}</p>
              <ul>{contributions}</ul><p class="method-line">{e(item['methods'])}</p>{link}</article>'''
        )
    earlier = "".join(
        f'''<article class="earlier-item"><p class="dates">{e(item['dates'])}</p>
          <div><h3>{e(item['title'])}</h3><p>{e(item['text'])}</p></div></article>'''
        for item in d["earlier_research"]
    )

    honors = []
    for item in d["honors"]:
        detail = f'<p>{e(item["detail"])}</p>' if item.get("detail") else ""
        honors.append(
            f'<li><p class="dates">{e(item["years"])}</p><h3>{e(item["title"])}</h3>{detail}</li>'
        )

    materials = []
    for item in d["materials"]:
        resource = ROOT / item["file"]
        if not resource.is_file():
            raise FileNotFoundError(f"Missing material: {resource}")
        size = f"{resource.stat().st_size / (1024 * 1024):.1f} MB"
        materials.append(
            f'''<article class="material" id="{e(item['id'])}">
              <a class="material-cover" href="./{e(item['file'])}" target="_blank" rel="noopener noreferrer">
                <img src="./assets/handbook-cover.png?v={asset_version}" alt="Cover of the EEG/ERP Preprocessing Manual" width="560" height="792">
              </a>
              <div><p class="section-label">Research notes</p>
                <h3><a href="./{e(item['file'])}" target="_blank" rel="noopener noreferrer">{e(item['title'])}</a></h3>
                <p class="material-subtitle">{e(item['subtitle'])}</p>
                <p>{e(item['description'])}</p>
                <p class="resource-meta">{e(item['language'])} · PDF · {e(item['pages'])} pages · {size} · <time datetime="{e(item['date'])}">{e(item['date_label'])}</time></p>
                <div class="material-links"><a class="primary-link" href="./{e(item['file'])}" target="_blank" rel="noopener noreferrer">Read PDF ↗</a><a href="./{e(item['file'])}" download>Download ↓</a></div>
                <details class="material-note"><summary>About this resource</summary><p>{e(item['note'])}</p></details>
              </div>
            </article>'''
        )

    structured = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": d["name"],
            "url": d["url"],
            "image": d["url"] + "/" + profile["file"],
            "jobTitle": role["title"],
            "worksFor": {"@type": "Organization", "name": role["institution"], "url": role["institution_url"]},
            "sameAs": [d["github"]],
            "knowsAbout": d["interests"],
        },
        ensure_ascii=False,
    ).replace("<", "\\u003c")
    description = (
        "Hongli Liu, Research Assistant at The Hong Kong Polytechnic University. "
        "Research in language comprehension, visual word recognition, semantic processing, and EEG/ERP."
    )
    hobby_items = "".join(f"<li>{e(item)}</li>" for item in d["personal"]["hobbies"])
    activity_gallery = "".join(
        f'''<figure class="activity-photo"><img src="./{e(item['file'])}?v={asset_version}" alt="{e(item['alt'])}" width="{e(item['width'])}" height="{e(item['height'])}"><figcaption>{e(item['label'])}</figcaption></figure>'''
        for item in activities
    )

    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hongli Liu | Language &amp; Cognition</title>
  <meta name="description" content="{e(description)}"><meta name="author" content="{e(d['name'])}">
  <meta name="theme-color" content="#193650"><meta name="referrer" content="strict-origin-when-cross-origin">
  <link rel="canonical" href="{e(d['url'])}/"><meta property="og:type" content="profile">
  <meta property="og:title" content="Hongli Liu | Language &amp; Cognition"><meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{e(d['url'])}/"><meta property="og:locale" content="en_US"><meta name="twitter:card" content="summary">
  <link rel="icon" type="image/svg+xml" href="./assets/favicon.svg?v={asset_version}">
  <link rel="stylesheet" href="./assets/main.css?v={asset_version}">
  <script defer src="./assets/main.js?v={asset_version}"></script>
  <script type="application/ld+json">{structured}</script>
</head>
<body id="top">
  <a class="skip-link" href="#main">Skip to content</a>
  <div class="utility-bar"><div class="site-width"><span>Language · Cognition · EEG/ERP</span>
    <div><a href="mailto:{e(d['email'])}">Email</a><a href="{e(d['github'])}" target="_blank" rel="noopener noreferrer">GitHub</a></div>
  </div></div>
  <header class="site-header"><div class="site-width">
    <div><h1>{e(d['name'])}</h1><p>{e(role['title'])} · {e(role['institution'])}</p></div>
    <span class="monogram" aria-hidden="true">HL</span>
  </div></header>
  <div class="site-width site-layout">
    <aside class="sidebar">
      <nav class="section-nav" aria-label="Main navigation">{nav}</nav>
      <div class="sidebar-block"><h2>Contact</h2><p><a href="mailto:{e(d['email'])}">{e(d['email'])}</a></p><p><a href="{e(d['github'])}" target="_blank" rel="noopener noreferrer">GitHub profile ↗</a></p></div>
      <div class="sidebar-block"><h2>Research interests</h2><ul>{interests}</ul></div>
      <div class="sidebar-block"><h2>Methods &amp; tools</h2><dl>{skill_rows}</dl></div>
    </aside>
    <main id="main" tabindex="-1">
      <section class="content-section about-section" id="background" aria-labelledby="background-heading">
        <h2 id="background-heading">About</h2>
        <div class="about-grid">
          <div class="about-copy"><p class="lead">{e(d['about'])}</p>
            <p>I am currently a <strong>{e(role['title'])}</strong> at <a href="{e(role['institution_url'])}" target="_blank" rel="noopener noreferrer">{e(role['institution'])}</a>, supervised by {supervisor}. I received my M.A. and B.A. from <a href="https://en.scu.edu.cn/" target="_blank" rel="noopener noreferrer">Sichuan University</a>.</p>
            <h3>Research interests</h3><ul class="interest-list">{interests}</ul>
          </div>
          <figure class="profile-photo"><img src="./{e(profile['file'])}?v={asset_version}" alt="{e(profile['alt'])}" width="1280" height="1703"></figure>
        </div>
        <div class="education"><h3>Education</h3>{''.join(education)}</div>
      </section>

      <section class="content-section" id="publications" aria-labelledby="publications-heading">
        <div class="section-heading"><h2 id="publications-heading">Publications &amp; Presentations</h2>
          <a href="./publications.bib" class="download-bib" download>Article citations (.bib) ↓</a></div>
        <ol class="output-list">{''.join(output_entry(item) for item in ordered_outputs())}</ol>
      </section>

      <section class="content-section" id="research" aria-labelledby="research-heading">
        <h2 id="research-heading">Research Experience</h2>
        <div class="research-list">{''.join(research)}</div>
        <div class="earlier-research"><h3>Earlier work in linguistics</h3>{earlier}</div>
      </section>

      <section class="content-section" id="honors" aria-labelledby="honors-heading">
        <h2 id="honors-heading">Honors &amp; Awards</h2>
        <ul class="honors-list">{''.join(honors)}</ul>
      </section>

      <section class="content-section" id="materials" aria-labelledby="materials-heading">
        <h2 id="materials-heading">Materials</h2>{''.join(materials)}
      </section>

      <section class="content-section" id="beyond" aria-labelledby="beyond-heading">
        <h2 id="beyond-heading">{e(d['personal']['heading'])}</h2>
        <div class="beyond-intro"><p class="beyond-copy">{e(d['personal']['text'])}</p><ul class="hobby-list">{hobby_items}</ul></div>
        <div class="activity-gallery">{activity_gallery}</div>
      </section>

      <section class="content-section message-section" id="message" aria-labelledby="message-heading">
        <h2 id="message-heading">{e(d['message']['heading'])}</h2>
        <p class="message-intro">{e(d['message']['text'])} You do not need to provide your name or email address.</p>
        <form class="message-form" data-message-form action="https://formsubmit.co/{e(d['email'])}" method="post">
          <input type="hidden" name="_subject" value="Anonymous message from academic homepage">
          <input type="hidden" name="_next" value="{e(d['url'])}/?message=sent#message">
          <input type="hidden" name="_url" value="{e(d['url'])}/#message">
          <label class="form-honey" aria-hidden="true">Leave this field empty<input type="text" name="_honey" tabindex="-1" autocomplete="off"></label>
          <label>Anonymous message<textarea name="message" rows="7" required maxlength="2000" placeholder="Write your message here…"></textarea></label>
          <div class="form-actions"><button type="submit">Send anonymously</button><p>Messages are processed by FormSubmit and forwarded to my inbox. <a href="https://formsubmit.co/privacy.pdf" target="_blank" rel="noopener noreferrer">Privacy information ↗</a></p></div>
          <p class="message-status" data-message-status role="status" aria-live="polite"></p>
        </form>
      </section>
    </main>
  </div>
  <footer class="site-footer"><div class="site-width"><p>© {date.fromisoformat(d['updated']).year} {e(d['name'])}</p>
    <div><button type="button" class="js-only" data-print>Print / Save as PDF</button><a href="#top">Back to top ↑</a></div>
  </div></footer>
  <p class="print-contact">{e(d['email'])} · {e(d['url'])}</p>
</body>
</html>'''
    return "\n".join(line.rstrip() for line in html.splitlines()) + "\n"


def legacy_redirect():
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hongli Liu — English homepage</title><meta name="robots" content="noindex">
<link rel="canonical" href="https://liuhongli775.github.io/">
<meta http-equiv="refresh" content="0;url=../index.html">
<script>
const oldSections = {'#about':'#background','#experience':'#background','#skills':'#research'};
window.location.replace('../index.html' + (oldSections[window.location.hash] || window.location.hash));
</script></head><body><p>This homepage is now in English. <a href="../index.html">Continue to Hongli Liu’s homepage</a>.</p></body></html>
'''


def build():
    (ROOT / "index.html").write_text(render(), encoding="utf-8", newline="\n")
    (ROOT / "zh").mkdir(exist_ok=True)
    (ROOT / "zh/index.html").write_text(legacy_redirect(), encoding="utf-8", newline="\n")
    papers = sorted(DATA["publications"], key=lambda item: item["date"], reverse=True)
    (ROOT / "publications.bib").write_text(
        "\n\n".join(bibtex(item) for item in papers) + "\n", encoding="utf-8", newline="\n"
    )
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: " + DATA["url"] + "/sitemap.xml\n", encoding="utf-8"
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'
        + e(DATA["url"])
        + "</loc></url></urlset>\n",
        encoding="utf-8",
    )
    print("Built the continuous academic homepage.")


if __name__ == "__main__":
    build()
