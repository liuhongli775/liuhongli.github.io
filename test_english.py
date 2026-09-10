"""Offline integrity tests for the editorial academic homepage."""
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
INTERESTS = json.loads((ROOT / "data/themes.json").read_text(encoding="utf-8"))
PROJECTS = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
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


class EditorialHomepage(unittest.TestCase):
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
        self.assertEqual(section_ids, ["about", "interests", "research", "reading", "hobbies", "message"])
        headings = re.findall(r'<h2[^>]*>(.*?)</h2>', html)
        self.assertEqual(headings, ["Research Interests", "Research", "Recent Reading", "Hobbies", "Message Me"])
        self.assertEqual(html.count('class="research-entry"'), 3)

    def test_about_identity_and_real_links_only(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn(DATA["name"], html)
        self.assertIn(DATA["research_statement"], html)
        self.assertIn(DATA["background"], html)
        self.assertIn(DATA["position"]["title"], html)
        self.assertIn(DATA["position"]["institution"], html)
        self.assertIn('href="' + DATA["github"] + '"', html)
        self.assertIn('href="mailto:' + DATA["email"] + '"', html)
        self.assertNotIn(">CV</a>", html)
        self.assertNotIn("Google Scholar</a>", html)
        self.assertIn('class="wordmark" href="#top">Hongli Liu</a>', html)

    def test_data_driven_interests_and_research(self):
        self.assertEqual(len(INTERESTS), 4)
        self.assertEqual(len(PROJECTS), 3)
        self.assertEqual(READINGS, [])
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for interest in INTERESTS:
            self.assertIn(escape(interest["title"]), html)
            self.assertIn(escape(interest["text"]), html)
        for project in PROJECTS:
            self.assertIn(escape(project["title"]), html)
            self.assertIn(escape(project["question"]), html)
            self.assertIn(escape(project["text"]), html)
            for method in project["methods"]:
                self.assertIn(escape(method), html)
            if project["source"] == "publication":
                publication = next(item for item in DATA["publications"] if item["id"] == project["publication_id"])
                self.assertIn(publication["journal"], html)
                self.assertIn(publication["year"], html)
                self.assertIn("https://doi.org/" + publication["doi"], html)
        presentation = DATA["presentation"]
        self.assertIn(escape(PROJECTS[0]["title"]), html)
        self.assertIn(escape(PROJECTS[0]["subtitle"]), html)
        self.assertIn(presentation["venue"], html)
        self.assertNotIn(">Poster<", html)

    def test_removed_legacy_structure_and_wording(self):
        page = "\n".join([
            (ROOT / "index.html").read_text(encoding="utf-8"),
            (ROOT / "assets/main.css").read_text(encoding="utf-8"),
            (ROOT / "assets/main.js").read_text(encoding="utf-8"),
        ])
        for token in [
            "One research program, three connected perspectives.",
            "Questions first. Methods in conversation.",
            "Computational work as part of the science.",
            "Research output.",
            "Short Bio.",
            "Current focus",
            "Boxed HL",
            "Beyond Research",
            'id="publications"',
            'id="computational"',
            'id="contact"',
            "reading-placeholder",
            "computational-card",
            "featured-project",
            "@keyframes",
            "linear-gradient",
            "box-shadow",
            "rotate(",
        ]:
            self.assertNotIn(token, page)

    def test_empty_reading_is_intentional(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        reading = html.split('id="reading"', 1)[1].split("</section>", 1)[0]
        self.assertIn("Notes from recent reading will appear here.", reading)
        self.assertNotIn("dashed", reading)
        self.assertNotIn("reading-placeholder", reading)

    def test_hobbies_use_two_existing_photos(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        images = [attrs for tag, attrs in Parser(ROOT / "index.html").tags if tag == "img"]
        self.assertEqual(len(images), 3)
        self.assertTrue(all(item.get("alt", "").strip() for item in images))
        self.assertNotIn("assets/daily.jpg", html)
        for image in [DATA["images"]["profile"], *DATA["images"]["hobbies"]]:
            self.assertTrue((ROOT / image["file"]).is_file())
            self.assertIn(image["file"] + "?v=" + DATA["asset_version"], html)
        self.assertEqual(len(DATA["images"]["hobbies"]), 2)

    def test_anonymous_message_form(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('action="https://formsubmit.co/' + DATA["email"] + '"', html)
        self.assertEqual(html.count("<textarea"), 1)
        self.assertIn('name="message"', html)
        self.assertIn('name="_honey"', html)
        self.assertNotIn('name="name"', html)
        self.assertNotIn('name="email"', html)
        self.assertIn(">Send</button>", html)
        self.assertIn("You can leave this message anonymously.", html)

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

    def test_bibliography_materials_and_privacy(self):
        bib = (ROOT / "publications.bib").read_text(encoding="utf-8")
        self.assertEqual(bib.count("@article{"), 2)
        self.assertLess(bib.index("yu2025graspability"), bib.index("liu2025nd250"))
        for material in DATA["materials"]:
            self.assertTrue((ROOT / material["file"]).read_bytes().startswith(b"%PDF-"))
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for token in ["15082195267@163.com", "hongliliu.research@gmail.com", "cv_Liu", "tel:", "fonts.googleapis.com"]:
            self.assertNotIn(token, html)
        self.assertIsNone(re.search(r"(?<!\d)1\d{2}[- ]\d{4}[- ]\d{4}(?!\d)", html))
        self.assertEqual(len(ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc")), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
