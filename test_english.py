"""Offline integrity tests for the research-focused academic homepage."""
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import runpy
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
BUILDER = runpy.run_path(str(ROOT / "site.py"))
DATA = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
THEMES = json.loads((ROOT / "data/themes.json").read_text(encoding="utf-8"))
PROJECTS = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
QUESTIONS = json.loads((ROOT / "data/questions.json").read_text(encoding="utf-8"))
READINGS = json.loads((ROOT / "data/readings.json").read_text(encoding="utf-8"))


class Parser(HTMLParser):
    def __init__(self, file):
        super().__init__()
        self.ids, self.urls, self.tags = [], [], []
        self.feed(file.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag in {"a", "link"} and "href" in attrs:
            self.urls.append(attrs["href"])
        if tag in {"img", "script"} and "src" in attrs:
            self.urls.append(attrs["src"])


class ResearchHomepage(unittest.TestCase):
    def test_build_reproducible(self):
        self.assertEqual((ROOT / "index.html").read_text(encoding="utf-8"), BUILDER["render"]())
        self.assertEqual((ROOT / "zh/index.html").read_text(encoding="utf-8"), BUILDER["legacy_redirect"]())

    def test_information_architecture(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        parser = Parser(ROOT / "index.html")
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        self.assertEqual(sum(tag == "h1" for tag, _ in parser.tags), 1)
        self.assertEqual(sum(tag == "main" for tag, _ in parser.tags), 1)
        section_ids = [attrs["id"] for tag, attrs in parser.tags if tag == "section" and "id" in attrs]
        self.assertEqual(section_ids, ["home", "themes", "research", "computational", "notes", "publications", "about", "contact"])
        order = [
            "Psycholinguistics · Cognitive Neuroscience · Computational Modeling",
            "Research themes",
            "Selected research",
            "Selected computational projects",
            "Questions I’m Thinking About",
            "What I’m Reading",
            "Short Bio",
            "Leave an anonymous message",
        ]
        positions = [html.index(item) for item in order]
        self.assertEqual(positions, sorted(positions))

    def test_research_identity_first(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn(DATA["research_statement"], html)
        self.assertIn(DATA["position"]["title"], html)
        self.assertIn(DATA["position"]["institution"], html)
        self.assertIn('href="' + DATA["github"] + '"', html)
        self.assertIn('href="mailto:' + DATA["email"] + '"', html)
        self.assertNotIn(">CV</a>", html)
        self.assertNotIn("Google Scholar</a>", html)

    def test_data_driven_content(self):
        self.assertEqual(len(THEMES), 3)
        self.assertEqual(len(PROJECTS["selected_research"]), 3)
        self.assertEqual(len(PROJECTS["computational_projects"]), 4)
        self.assertEqual(len(QUESTIONS), 4)
        self.assertEqual(READINGS, [])
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for theme in THEMES:
            self.assertIn(escape(theme["title"]), html)
        for project in PROJECTS["selected_research"]:
            self.assertIn(escape(project["title"]), html)
            for method in project["methods"]:
                self.assertIn(escape(method), html)
        for project in PROJECTS["computational_projects"]:
            self.assertIn(project["title"], html)
            for field in ["problem", "data", "method", "output"]:
                self.assertIn(project[field], html)
        for question in QUESTIONS:
            self.assertIn(question, html)
        self.assertIn("Reading notes will appear here.", html)
        self.assertNotIn('class="reading-entry"', html)

    def test_publications_conventional_and_secondary(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        publication = html.split('id="publications"', 1)[1].split("</section>", 1)[0]
        titles = [DATA["presentation"]["title"]] + [
            item["title"] for item in sorted(DATA["publications"], key=lambda item: item["date"], reverse=True)
        ]
        positions = [publication.index(title) for title in titles]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(publication.count('class="publication-entry'), 3)
        self.assertIn("Article citations (.bib)", publication)
        for item in DATA["publications"]:
            self.assertIn("https://doi.org/" + item["doi"], publication)

    def test_about_resources_and_images(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("Short Bio.", html)
        self.assertNotIn("National Scholarship", html)
        self.assertIn("Sichuan University", html)
        self.assertIn("EEG/ERP Preprocessing Manual", html)
        images = [attrs for tag, attrs in Parser(ROOT / "index.html").tags if tag == "img"]
        self.assertEqual(len(images), 4)
        self.assertTrue(all(item.get("alt", "").strip() for item in images))
        for image in [DATA["images"]["profile"], *DATA["images"]["activities"]]:
            self.assertTrue((ROOT / image["file"]).is_file())
            self.assertIn(image["file"] + "?v=" + DATA["asset_version"], html)
        for resource in DATA["materials"]:
            self.assertTrue((ROOT / resource["file"]).read_bytes().startswith(b"%PDF-"))

    def test_anonymous_message_form(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('action="https://formsubmit.co/' + DATA["email"] + '"', html)
        self.assertIn('name="message"', html)
        self.assertIn('name="_honey"', html)
        self.assertNotIn('name="name"', html)
        self.assertNotIn('name="email"', html)
        self.assertIn("Send anonymously", html)

    def test_no_pagination_or_decorative_motion(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "assets/main.css").read_text(encoding="utf-8")
        script = (ROOT / "assets/main.js").read_text(encoding="utf-8")
        for token in ["page-track", "folio-page", "page-progress", "data-page-status", "data-page-turn", "showPage(", "translateX"]:
            self.assertNotIn(token, html + css + script)
        self.assertNotIn("@keyframes", css)
        self.assertNotIn("linear-gradient", css)
        self.assertIn("font: 1rem/", css)

    def test_local_links_and_external_safety(self):
        for file in [ROOT / "index.html", ROOT / "zh/index.html"]:
            parser = Parser(file)
            for raw_link in parser.urls:
                url = urlsplit(raw_link)
                if url.scheme or url.netloc:
                    continue
                target = (file.parent / unquote(url.path)).resolve() if url.path else file
                self.assertTrue(target.is_file(), str(target))
                if url.fragment:
                    self.assertIn(url.fragment, Parser(target).ids)
            for _, attrs in parser.tags:
                if attrs.get("target") == "_blank":
                    self.assertIn("noopener", attrs.get("rel", ""))

    def test_bibliography_and_privacy(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bib = (ROOT / "publications.bib").read_text(encoding="utf-8")
        self.assertEqual(bib.count("@article{"), 2)
        self.assertLess(bib.index("yu2025graspability"), bib.index("liu2025nd250"))
        for token in ["15082195267@163.com", "hongliliu.research@gmail.com", "cv_Liu", "tel:", "fonts.googleapis.com"]:
            self.assertNotIn(token, html)
        self.assertIsNone(re.search(r"(?<!\d)1\d{2}[- ]\d{4}[- ]\d{4}(?!\d)", html))
        self.assertEqual(len(ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc")), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
