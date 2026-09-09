"""Offline integrity tests for the English academic homepage."""
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


class EnglishHomepage(unittest.TestCase):
    def test_build_reproducible(self):
        self.assertEqual((ROOT / "index.html").read_text(encoding="utf-8"), BUILDER["render"]())
        self.assertEqual((ROOT / "zh/index.html").read_text(encoding="utf-8"), BUILDER["legacy_redirect"]())

    def test_continuous_english_structure(self):
        page = Parser(ROOT / "index.html")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"[\u4e00-\u9fff]", html))
        self.assertEqual(len(page.ids), len(set(page.ids)))
        self.assertEqual(sum(tag == "h1" for tag, _ in page.tags), 1)
        self.assertEqual(sum(tag == "main" for tag, _ in page.tags), 1)
        self.assertEqual(
            [attrs["id"] for tag, attrs in page.tags if tag == "section"],
            ["background", "publications", "research", "honors", "materials", "beyond"],
        )
        for obsolete in ["page-track", "folio-page", "page-indicator", "data-page-turn", "data-view-toggle"]:
            self.assertNotIn(obsolete, html)
        self.assertNotIn("<svg", html)
        self.assertIn("assets/profile.jpg?v=" + DATA["asset_version"], html)
        for image in DATA["images"]["activities"]:
            self.assertIn(image["file"] + "?v=" + DATA["asset_version"], html)
        self.assertIn("assets/main.css?v=" + DATA["asset_version"], html)
        self.assertIn("assets/main.js?v=" + DATA["asset_version"], html)

    def test_images_and_accessible_names(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        parser = Parser(ROOT / "index.html")
        images = [attrs for tag, attrs in parser.tags if tag == "img"]
        self.assertEqual(len(images), 5)
        self.assertTrue(all(image.get("alt", "").strip() for image in images))
        expected_images = [DATA["images"]["profile"], *DATA["images"]["activities"]]
        for item in expected_images:
            file = ROOT / item["file"]
            self.assertTrue(file.is_file())
            self.assertTrue(file.read_bytes().startswith(b"\xff\xd8\xff"))
        self.assertIn(escape(DATA["images"]["profile"]["alt"]), html)
        for item in DATA["images"]["activities"]:
            self.assertIn(escape(item["alt"]), html)
        self.assertEqual(html.count('class="activity-photo"'), 3)

    def test_local_links(self):
        for file in [ROOT / "index.html", ROOT / "zh/index.html"]:
            parser = Parser(file)
            for link in parser.urls:
                url = urlsplit(link)
                if url.scheme or url.netloc:
                    continue
                target = (file.parent / unquote(url.path)).resolve() if url.path else file
                self.assertTrue(target.is_file(), str(target))
                if url.fragment:
                    self.assertIn(url.fragment, Parser(target).ids)
            for _, attrs in parser.tags:
                if attrs.get("target") == "_blank":
                    self.assertIn("noopener", attrs.get("rel", ""))

    def test_profile_research_and_honors(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for value in [
            "Research Assistant",
            "The Hong Kong Polytechnic University",
            "Dr. Jiaqiang Zhu",
            "Research Experience",
            "Methods &amp; tools",
            "Earlier work in linguistics",
        ]:
            self.assertIn(value, html)
        self.assertIn("hongli.liu@polyu.edu.hk", html)
        self.assertIn("incrementally processes language", html)
        self.assertIn("I received my M.A. and B.A. from Sichuan University.", html)
        self.assertEqual(html.count('class="research-project"'), 3)
        for item in DATA["research"]:
            self.assertIn(escape(item["title"]), html)
            for point in item["contributions"]:
                self.assertIn(escape(point), html)
        self.assertEqual(html.count('class="dates"'), 10)
        self.assertEqual(html.count("<li><p class=\"dates\""), 6)
        for item in DATA["honors"]:
            self.assertIn(escape(item["title"]), html)

    def test_outputs_reverse_chronological(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        section = html.split('id="publications"', 1)[1].split("</section>", 1)[0]
        self.assertEqual(re.findall(r'data-date="([^"]+)"', section), ["2026", "2025-06", "2025-05"])
        self.assertEqual([item["date"] for item in BUILDER["ordered_outputs"]()], ["2026", "2025-06", "2025-05"])
        self.assertEqual(section.count('class="output-entry publication"'), 2)
        self.assertEqual(section.count("conference-presentation"), 1)
        self.assertIn("Article citations (.bib)", section)

    def test_material_and_hobbies(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("23 pages", html)
        self.assertIn("Attachment 2", html)
        self.assertIn("hiking, running, working out, and playing badminton", html)
        for resource in DATA["materials"]:
            self.assertTrue((ROOT / resource["file"]).read_bytes().startswith(b"%PDF-"))

    def test_bibliography(self):
        bib = (ROOT / "publications.bib").read_text(encoding="utf-8")
        self.assertEqual(bib.count("@article{"), 2)
        self.assertEqual(bib.count("{"), bib.count("}"))
        self.assertLess(bib.index("yu2025graspability"), bib.index("liu2025nd250"))
        self.assertIn("10.1016/j.jneuroling.2025.101249", bib)
        self.assertIn("10.1016/j.cortex.2025.04.003", bib)

    def test_no_obsolete_or_private_content(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for token in ["cv_Liu", "tel:", "Chengdu", "Master's student", "fonts.googleapis.com", "PsychoPy", "cortex.2024.08.009", "15082195267@163.com", "hongliliu.research@gmail.com", "incremenrtally", "Assistantat"]:
            self.assertNotIn(token, html)
        self.assertIsNone(re.search(r"(?<!\d)1\d{2}[- ]\d{4}[- ]\d{4}(?!\d)", html))
        self.assertEqual(len(ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc")), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
