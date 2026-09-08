# Hongli Liu — Academic website

[Visit the website](https://liuhongli775.github.io/)

English academic homepage for Hongli Liu, Research Assistant at The Hong Kong Polytechnic University. The site presents academic background, publications and presentations, research experience, honors, EEG/ERP materials, and interests outside research.

The layout is inspired by the information hierarchy of a traditional university faculty page: a clear name-and-role header, a compact navigation and contact sidebar, and one continuous reading column. It uses its own cool navy visual system and does not reproduce institutional branding from the reference.

## Features

- Continuous desktop and mobile reading; no slide or page-turn interaction
- Background first, followed by publications and presentations in reverse chronological order
- Three detailed research projects and two earlier linguistics projects
- Complete honors list
- Downloadable BibTeX and EEG/ERP manual
- Responsive navigation, print styles, reduced-motion support, and keyboard-accessible disclosures
- No framework, external fonts, analytics, trackers, or API keys

## Development

Open `index.html` directly, or serve the repository locally:

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Edit `site.json`, then rebuild and check:

```sh
python site.py
python test_english.py
```

The builder and integrity tests use the Python standard library only. When changing CSS, JavaScript, or images, update `asset_version` in `site.json` so visitors receive the current assets after deployment.

## Main files

| File | Purpose |
| --- | --- |
| `site.json` | Profile, research, publications, honors, images, and materials |
| `site.py` | Static HTML and bibliography builder |
| `assets/main.css` | Responsive and print styles |
| `assets/main.js` | Section navigation, citation copying, and printing |
| `assets/profile.jpg` | Profile portrait |
| `assets/outdoors.jpg` | Beyond Research photograph |
| `publications.bib` | Downloadable journal-article citations |
| `materials/` | Downloadable research resources |
| `test_english.py` | Content, structure, privacy, and local-link checks |

## Images and privacy

The two displayed photographs were selected from images supplied by the site owner. They are copied without generative alteration. Both selected JPEGs contained no EXIF entries, GPS data, embedded comments, or ICC profiles when reviewed.

The original CV, local reference library, and participant datasets are not included. Contact links on the site are public. Review privacy, permissions, and lab data-sharing requirements before adding future downloadable resources.

## Research resource

The EEG/ERP Preprocessing Manual is a set of personal research notes, not an official EEGLAB or ERPLAB manual. The downloadable PDF is unchanged from the supplied version; the cover thumbnail is rendered from its first page. The batch-processing script referred to as Attachment 2 is not included.

## Deployment

The generated site is served from the repository root through GitHub Pages. The historical `/zh/index.html` address redirects to the English homepage. Preserve the existing Pages configuration when updating the repository.
