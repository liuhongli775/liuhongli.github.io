# Hongli Liu — Academic homepage

[Visit the website](https://liuhongli775.github.io/)

A research-focused academic homepage for Hongli Liu, Research Assistant at The Hong Kong Polytechnic University. The site presents an emerging research program at the intersection of psycholinguistics, cognitive neuroscience, and computational modeling.

## Information architecture

The homepage is intentionally organized around scientific questions rather than a CV timeline:

1. Research identity and a short research statement
2. Three connected research themes
3. Selected empirical research
4. Computational research workflows
5. Questions and reading notes
6. Conventional publications and presentations
7. Compact bio, open resource, life outside research, and contact

Awards and exhaustive experience details remain in `site.json` but do not dominate the homepage.

## Editing recurring content

| Content | Edit here |
| --- | --- |
| Research themes | `data/themes.json` |
| Selected and computational projects | `data/projects.json` |
| Questions I’m Thinking About | `data/questions.json` |
| What I’m Reading | `data/readings.json` |
| Publications, identity, bio, education, images | `site.json` |
| Page structure and rendering | `site.py` |
| Visual design | `assets/main.css` |
| Citation copy and anonymous form status | `assets/main.js` |

`data/readings.json` is intentionally empty. Add a JSON object with `title`, `authors`, `year`, `venue`, `url`, `note_label`, and `note` when a reading should appear.

The optional `links.cv` and `links.scholar` values in `site.json` are blank. The site hides those links until verified public URLs are added.

## Local build

```sh
python site.py
python test_english.py
python -m http.server 8000 --bind 127.0.0.1
```

The site has no framework, external fonts, analytics, trackers, or runtime dependencies. The builder and integrity tests use the Python standard library only.

When changing CSS, JavaScript, or images, update `asset_version` in `site.json` so visitors receive current assets after deployment.

## Publications

Publications link to their DOI records. Publisher-formatted subscription PDFs are not hosted unless public distribution rights are verified. `publications.bib` contains the two journal-article citations.

## Anonymous message form

The anonymous message form uses FormSubmit to forward message text to `hongli.liu@polyu.edu.hk`. It requests no visitor name or email. FormSubmit processes submissions and requires one-time activation for the receiving address.

## Privacy and resources

The original CV, local reference library, participant datasets, and unpublished research data are not included. The EEG/ERP Preprocessing Manual remains available as a personal research resource; it is not an official EEGLAB or ERPLAB manual.

The displayed photographs were supplied by the site owner. Contact links are public.

## Deployment

The generated static files are served from the repository root through GitHub Pages. The historical `/zh/index.html` address redirects to the English homepage.
