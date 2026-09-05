# Hongli Liu — Academic website

[Visit the website](https://liuhongli775.github.io/)

Personal academic website for Hongli Liu, featuring research in language and cognition, publications and presentations, academic background, honors, and EEG/ERP resources.

Built as a static, English-only site for GitHub Pages. No framework, external fonts, analytics, or API keys are required.

## Reading the site

- Desktop: five horizontally transitioning pages with a fixed profile and contents rail. Click the left half of the page to go back or the right half to advance; links and text selection remain interactive. The directory and left/right arrow keys also work.
- Long pages scroll vertically; the footer indicates when more content is available below.
- Continuous view provides a single scrolling document. Narrow screens, short windows, and browsers without JavaScript use this mode automatically.
- Section links, browser Back/Forward, and reload preserve the selected page.
- Reduced-motion preferences are respected. Print / Save as PDF includes every section.

## Development

Open `index.html` directly, or serve this directory locally:

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Edit `site.json` to update content, then rebuild and check:

```sh
python site.py
python test_english.py
```

The build and integrity tests use the Python standard library only.

| File | Purpose |
| --- | --- |
| `site.json` | Profile, research, publications, presentations, honors, and resources |
| `site.py` | Static HTML and bibliography builder |
| `assets/main.css` | Responsive and print styles |
| `assets/main.js` | Paging, reading modes, navigation, and citation copying |
| `publications.bib` | Downloadable journal-article citations |
| `materials/` | Downloadable research resources |
| `test_english.py` | Content, structure, and local-link checks |

Research outputs are sorted newest first. Journal article dates refer to issue months; conference entries retain only the date precision supplied. The bibliography includes journal articles, not the conference poster.

## Deployment

The generated HTML, assets, bibliography, and resources are served from the repository root. Commit generated files alongside changes to the source data.

See [GitHub Pages publishing documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site). Preserve the repository's existing Pages configuration.

The historical `/zh/index.html` address redirects to the English homepage.

## Research resources

The EEG/ERP Preprocessing Manual is a set of personal research notes, not an official EEGLAB or ERPLAB manual. The downloadable PDF is unchanged from the supplied version; the cover thumbnail is rendered from its first page. The batch-processing script referred to as Attachment 2 is not included.

References and third-party screenshots remain attributed in the document. No blanket licence is granted to third-party material.

The original CV, local reference library, and participant datasets are not included. Contact links are public. Review privacy, permissions, and lab data-sharing requirements before adding further downloadable resources.
