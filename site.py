"""Build the English academic folio. Python 3; no third-party dependencies."""
from datetime import date
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'site.json').read_text(encoding='utf-8'))
SECTIONS = [('background', 'Background'), ('publications', 'Publications & Presentations'),
            ('honors', 'Honors & Awards'), ('materials', 'Materials'), ('beyond', 'Beyond Research')]


def e(value):
    return escape(str(value), quote=True)


def bibtex(pub):
    return (f"@article{{{pub['id']},\n"
            f"  author = {{{pub['bib_authors']}}},\n"
            f"  title = {{{{{pub['title']}}}}},\n"
            f"  journal = {{{pub['journal']}}},\n"
            f"  year = {{{pub['year']}}},\n"
            f"  volume = {{{pub['volume']}}},\n"
            f"  pages = {{{pub['pages'].replace('–', '--')}}},\n"
            f"  doi = {{{pub['doi']}}}\n}}")


def ordered_outputs():
    entries = [dict(p, kind='article') for p in DATA['publications']]
    entries.append(dict(DATA['presentation'], kind='poster', date=DATA['presentation']['year']))
    return sorted(entries, key=lambda p: p['date'], reverse=True)


def output_entry(p):
    if p['kind'] == 'poster':
        return f'''<li class="output-entry conference-presentation" data-date="{e(p['date'])}">
          <p class="output-date"><time datetime="{e(p['year'])}">{e(p['year'])}</time></p>
          <div><p class="output-type">{e(p['type'])}</p><h3 class="pub-title">{e(p['title'])}</h3>
          <p class="pub-venue">{e(p['venue'])}, {e(p['year'])}.</p>
          <p class="conference-theme">{e(p['theme'])}</p></div></li>'''
    people = [f'<strong>{e(a)}</strong>' if a == 'Liu, H.' else e(a) for a in p['authors']]
    authors = ', '.join(people[:-1]) + ', &amp; ' + people[-1]
    return f'''<li class="output-entry publication" data-date="{e(p['date'])}">
      <p class="output-date"><time datetime="{e(p['date'])}">{e(p['date_label'])}</time></p>
      <div><p class="output-type">Journal article</p>
        <h3 class="pub-title"><a href="https://doi.org/{e(p['doi'])}" target="_blank" rel="noopener noreferrer">{e(p['title'])}</a></h3>
        <p class="pub-authors">{authors} ({e(p['year'])}).</p>
        <p class="pub-journal"><em>{e(p['journal'])}, {e(p['volume'])}</em>, {e(p['pages'])}.</p>
        <div class="pub-links"><a href="https://doi.org/{e(p['doi'])}" target="_blank" rel="noopener noreferrer">Read paper <span aria-hidden="true">↗</span></a>
          <details class="citation"><summary>BibTeX<span class="sr-only"> for {e(p['title'])}</span></summary>
            <pre id="{e(p['id'])}" tabindex="0">{e(bibtex(p))}</pre>
            <button type="button" class="copy-button js-only" data-copy="{e(p['id'])}">Copy citation</button><span class="copy-status" role="status" aria-live="polite"></span>
          </details>
        </div>
      </div></li>'''


def heading(index, subtitle, extra=''):
    sid, title = SECTIONS[index]
    return f'''<header class="folio-heading"><p class="eyebrow">{index + 1:02d} / {e(subtitle)}</p>
      <div class="heading-row"><h2 id="{sid}-heading" tabindex="-1">{e(title)}</h2>{extra}</div></header>'''


def render():
    d, role = DATA, DATA['position']
    supervisor = f'<a href="{e(role["supervisor_url"])}" target="_blank" rel="noopener noreferrer">Dr. {e(role["supervisor"])}</a>'
    education = []
    for index, p in enumerate(d['education']):
        advisor = '<p class="supervisor">Supervisor: Dr. Feng Gu</p>' if index == 0 else ''
        education.append(f'''<article class="experience-item"><p class="dates">{e(p['dates'])}</p><h4>{e(p['title'])}</h4><p class="institution">{e(p['institution'])}</p>{advisor}</article>''')
    research = []
    for i, p in enumerate(d['research']):
        paper = f'<a class="research-link" href="https://doi.org/{e(p["doi"])}" target="_blank" rel="noopener noreferrer">Related paper ↗</a>' if p.get('doi') else ''
        research.append(f'''<article class="research-project"><p class="project-context">{e(p['context'])}</p>
          <h4><span class="project-number" aria-hidden="true">{i+1:02d}</span>{e(p['title'])}</h4><p>{e(p['text'])}</p>
          <ul class="contributions">{''.join('<li>'+e(t)+'</li>' for t in p['contributions'])}</ul>
          <p class="method-line">{e(p['methods'])}</p>{paper}</article>''')
    earlier = ''.join(f'<article><h4>{e(p["title"])}</h4><p class="dates">{e(p["dates"])}</p><p>{e(p["text"])}</p></article>' for p in d['earlier_research'])
    skills = ''.join(f'<div><dt>{e(s["label"])}</dt><dd>{e(s["text"])}</dd></div>' for s in d['skills'])
    honors = []
    for h in d['honors']:
        detail = f'<p class="honor-detail">{e(h["detail"])}</p>' if h.get('detail') else ''
        honors.append(f'<li class="honor-item"><p class="dates">{e(h["years"])}</p><h3>{e(h["title"])}</h3>{detail}</li>')
    materials = []
    for m in d['materials']:
        asset = ROOT / m['file']
        if not asset.is_file():
            raise FileNotFoundError(f'Missing material: {asset}')
        size = f'{asset.stat().st_size / (1024 * 1024):.1f} MB'
        materials.append(f'''<article class="material" id="{e(m['id'])}">
          <a class="material-cover" href="./{e(m['file'])}" target="_blank" rel="noopener noreferrer"><img src="./assets/handbook-cover.png" alt="Cover of the EEG/ERP Preprocessing Manual" width="560" height="792"></a>
          <div class="material-body"><p class="eyebrow">Research notes / EEG &amp; ERP</p>
            <h3><a href="./{e(m['file'])}" target="_blank" rel="noopener noreferrer">{e(m['title'])}</a></h3>
            <p class="material-subtitle">{e(m['subtitle'])}</p><p class="material-description">{e(m['description'])}</p>
            <dl class="resource-facts"><div><dt>Format</dt><dd>{e(m['language'])} · PDF · {e(m['pages'])} pages</dd></div><div><dt>Updated</dt><dd><time datetime="{e(m['date'])}">{e(m['date_label'])}</time></dd></div><div><dt>File size</dt><dd>{size}</dd></div></dl>
            <div class="material-links"><a class="pdf-button" href="./{e(m['file'])}" target="_blank" rel="noopener noreferrer">Read PDF <span aria-hidden="true">↗</span></a><a href="./{e(m['file'])}" download>Download <span aria-hidden="true">↓</span></a></div>
            <details class="material-note"><summary>About this resource</summary><p>{e(m['note'])}</p></details>
          </div></article>''')
    navigation = ''.join(f'<a href="#{sid}"'+(' aria-current="location"' if i == 0 else '')+f'><span class="nav-number" aria-hidden="true">{i+1:02d}</span><span>{e(title)}</span></a>' for i, (sid, title) in enumerate(SECTIONS))
    structured = json.dumps({
        '@context':'https://schema.org', '@type':'Person', 'name':d['name'],
        'url':d['url'], 'jobTitle':role['title'],
        'worksFor':{'@type':'Organization','name':role['institution'],'url':role['institution_url']},
        'sameAs':[d['github']], 'knowsAbout':d['interests'],
    },ensure_ascii=False).replace('<','\\u003c')
    description = 'Hongli Liu, Research Assistant at The Hong Kong Polytechnic University. Research in language and cognition, publications, academic background, and EEG/ERP materials.'
    hobbies = ''.join(f'<li><span aria-hidden="true">{i+1:02d}</span>{e(h)}</li>' for i, h in enumerate(d['personal']['hobbies']))
    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hongli Liu | Language &amp; Cognition</title>
  <meta name="description" content="{e(description)}"><meta name="author" content="{e(d['name'])}">
  <meta name="theme-color" content="#f8fafc"><meta name="referrer" content="strict-origin-when-cross-origin">
  <link rel="canonical" href="{e(d['url'])}/"><meta property="og:type" content="profile">
  <meta property="og:title" content="Hongli Liu | Language &amp; Cognition"><meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{e(d['url'])}/"><meta property="og:locale" content="en_US"><meta name="twitter:card" content="summary">
  <link rel="icon" type="image/svg+xml" href="./assets/favicon.svg"><link rel="stylesheet" href="./assets/main.css">
  <script defer src="./assets/main.js"></script><script type="application/ld+json">{structured}</script>
</head>
<body id="top">
  <a class="skip-link" href="#main">Skip to content</a>
  <div class="academic-folio">
    <header class="profile-rail">
      <div class="profile-top"><p class="eyebrow">Language &amp; Cognition</p><h1>{e(d['name'])}</h1>
        <p class="role-line">{e(role['title'])}<br>{e(role['institution'])}</p>
        <div class="contact-links" id="contact"><a href="mailto:{e(d['email'])}" aria-label="Email Hongli Liu">Email ↗</a><a href="{e(d['github'])}" target="_blank" rel="noopener noreferrer">GitHub ↗</a></div>
      </div>
      <nav class="section-nav" aria-label="Main navigation">{navigation}</nav>
      <div class="rail-bottom"><p class="eyebrow">Research interests</p><p>{' · '.join(e(i) for i in d['interests'])}</p><span class="rail-year">Academic profile / {date.fromisoformat(d['updated']).year}</span></div>
      <p class="print-contact">{e(d['email'])} · {e(d['url'])}</p>
    </header>
    <div class="folio-workspace">
      <div class="folio-toolbar"><span>Hongli Liu <span class="toolbar-slash">/</span> Academic profile</span><button class="view-toggle js-only" type="button" data-view-toggle aria-pressed="false">Continuous view</button></div>
      <main id="main" tabindex="-1">
        <div class="page-track">
          <section class="section folio-page" id="background" aria-labelledby="background-heading">
            {heading(0, 'Academic background')}
            <p class="intro-copy">{e(d['about'])}</p>
            <div class="background-layout">
              <div class="background-column">
                <h3 class="subheading">Appointments &amp; education</h3>
                <article class="experience-item current-position"><p class="dates"><time datetime="{e(role['start'])}">{e(role['date_label'])}</time></p><h4>{e(role['title'])}</h4><p class="institution">{e(role['institution'])}</p><p class="supervisor">Supervisor: {supervisor}</p></article>
                {''.join(education)}
                <h3 class="subheading toolkit-heading">Methods &amp; tools</h3><dl class="skill-list">{skills}</dl>
              </div>
              <div class="research-column"><h3 class="subheading">Research experience</h3>{''.join(research)}
                <details class="extra-details"><summary>Earlier work in linguistics</summary><div class="extra-content">{earlier}</div></details>
              </div>
            </div>
          </section>
          <section class="section folio-page" id="publications" aria-labelledby="publications-heading">
            {heading(1, 'Research output', '<a class="download-bib" href="./publications.bib" download>Article citations (.bib) ↓</a>')}
            <p class="section-deck">Journal articles and conference contributions, most recent first.</p>
            <ol class="pub-list">{''.join(output_entry(p) for p in ordered_outputs())}</ol>
          </section>
          <section class="section folio-page" id="honors" aria-labelledby="honors-heading">
            {heading(2, 'Academic recognition')}
            <ul class="honors-list">{''.join(honors)}</ul>
          </section>
          <section class="section folio-page" id="materials" aria-labelledby="materials-heading">
            {heading(3, 'Notes & resources')}
            <p class="section-deck">A practical resource from my EEG/ERP work.</p>{''.join(materials)}
          </section>
          <section class="section folio-page beyond" id="beyond" aria-labelledby="beyond-heading">
            {heading(4, 'Outside the lab')}
            <div class="personal-layout"><div><p class="beyond-copy">{e(d['personal']['text'])}</p><ul class="hobby-list">{hobbies}</ul></div>
              <div class="landscape" aria-hidden="true">
                <svg viewBox="0 0 360 420" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="265" cy="85" r="34" stroke="currentColor" stroke-width="1"/><path d="M15 245L110 108L160 178L198 136L345 320M15 286L87 202L138 255L220 182L345 354M15 325L100 275L185 316L246 275L345 387M15 362L75 336L143 371L215 341L292 397" stroke="currentColor" stroke-width="1.4"/><path d="M110 108L101 146L121 137L137 165M198 136L184 176L209 163L220 182" stroke="currentColor"/><path d="M5 398H355" stroke="currentColor"/></svg>
                <span>Beyond the desk</span>
              </div>
            </div>
          </section>
        </div>
      </main>
      <footer class="folio-footer"><span class="footer-credit">© {date.fromisoformat(d['updated']).year} {e(d['name'])}</span>
        <div class="page-controls" aria-label="Page navigation"><button type="button" data-prev aria-label="Previous page">←</button><span class="page-status" aria-live="polite" aria-atomic="true">01 / 05</span><button type="button" data-next aria-label="Next page">→</button><span class="keyboard-hint">Use ← → to turn pages</span></div>
        <button type="button" class="print-button js-only" data-print>Print / Save as PDF</button>
      </footer>
    </div>
  </div>
</body>
</html>'''
    return '\n'.join(line.rstrip() for line in html.splitlines()) + '\n'


def legacy_redirect():
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hongli Liu — English homepage</title><meta name="robots" content="noindex">
<link rel="canonical" href="https://liuhongli775.github.io/">
<meta http-equiv="refresh" content="0;url=../index.html">
<script>
const oldSections = {'#about':'#background','#experience':'#background','#skills':'#background','#research':'#background'};
window.location.replace('../index.html' + (oldSections[window.location.hash] || window.location.hash));
</script></head><body><p>This homepage is now in English. <a href="../index.html">Continue to Hongli Liu’s homepage</a>.</p></body></html>
'''


def build():
    (ROOT/'index.html').write_text(render(),encoding='utf-8',newline='\n')
    (ROOT/'zh').mkdir(exist_ok=True)
    (ROOT/'zh/index.html').write_text(legacy_redirect(),encoding='utf-8',newline='\n')
    papers = sorted(DATA['publications'],key=lambda p:p['date'],reverse=True)
    (ROOT/'publications.bib').write_text('\n\n'.join(bibtex(p) for p in papers)+'\n',encoding='utf-8',newline='\n')
    (ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+DATA['url']+'/sitemap.xml\n',encoding='utf-8')
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+e(DATA['url'])+'/</loc></url></urlset>\n',encoding='utf-8')
    print('Built the five-page academic folio with reverse-chronological research outputs.')


if __name__ == '__main__':
    build()
