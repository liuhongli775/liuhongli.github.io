# Hongli Liu — Academic website

[Visit the website](https://liuhongli775.github.io/)

English academic homepage for Hongli Liu, Research Assistant at The Hong Kong Polytechnic University. The site presents academic background, publications and presentations, research experience, honors, EEG/ERP materials, and interests outside research.





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
| `assets/hiking-1.jpg`, `assets/daily.jpg` | Beyond Research hiking and daily-life photographs |
| `publications.bib` | Downloadable journal-article citations |
| `materials/` | Downloadable research resources |
| `test_english.py` | Content, structure, privacy, and local-link checks |


## Research resource

The EEG/ERP Preprocessing Manual is a set of personal research notes, not an official EEGLAB or ERPLAB manual. The downloadable PDF is unchanged from the supplied version; the cover thumbnail is rendered from its first page. The batch-processing script referred to as Attachment 2 is not included.

## Deployment

The generated site is served from the repository root through GitHub Pages. The historical `/zh/index.html` address redirects to the English homepage. Preserve the existing Pages configuration when updating the repository.

The anonymous message form uses FormSubmit to forward message text to the public PolyU contact address. It requests no visitor name or email. FormSubmit processes submissions and requires one-time activation for the receiving address.

With JavaScript enabled, each main section is shown as one page. Clicking any non-interactive area advances to the next section; links, forms, disclosures, code blocks, and text selection remain interactive. The final page loops back to Background. The sidebar and arrow/Page Up/Page Down keys provide direct and backward navigation. Without JavaScript, the complete page remains continuously readable.
