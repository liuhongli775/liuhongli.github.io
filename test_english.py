"""Offline integrity tests; Python standard library only."""
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import hashlib
import json
import re
import runpy
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
BUILDER = runpy.run_path(str(ROOT/'site.py'))
DATA = json.loads((ROOT/'site.json').read_text(encoding='utf-8'))


class Parser(HTMLParser):
    def __init__(self, file):
        super().__init__()
        self.ids, self.urls, self.tags = [], [], []
        self.feed(file.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag in ['a','link'] and 'href' in attrs:
            self.urls.append(attrs['href'])
        if tag in ['img','script'] and 'src' in attrs:
            self.urls.append(attrs['src'])


class EnglishHomepage(unittest.TestCase):
    def test_build_reproducible(self):
        self.assertEqual((ROOT/'index.html').read_text(encoding='utf-8'),BUILDER['render']())
        self.assertEqual((ROOT/'zh/index.html').read_text(encoding='utf-8'),BUILDER['legacy_redirect']())

    def test_english_only_and_structure(self):
        page = Parser(ROOT/'index.html')
        html = (ROOT/'index.html').read_text(encoding='utf-8')
        self.assertIsNone(re.search(r'[\u4e00-\u9fff]',html))
        self.assertNotIn('hreflang="zh',html)
        self.assertNotIn('language-switch',html)
        self.assertEqual(len(page.ids),len(set(page.ids)))
        self.assertEqual(sum(tag=='h1' for tag,_ in page.tags),1)
        self.assertEqual(sum(tag=='main' for tag,_ in page.tags),1)
        self.assertEqual(sum(tag=='section' for tag,_ in page.tags),5)
        self.assertEqual([attrs['id'] for tag,attrs in page.tags if tag=='section'], ['background','publications','honors','materials','beyond'])
        self.assertNotIn('data-page-turn=',html)
        self.assertNotIn('data-prev',html)
        self.assertNotIn('data-next',html)
        self.assertNotIn('page-controls',html)
        self.assertIn('assets/main.css?v='+DATA['asset_version'],html)
        self.assertIn('assets/main.js?v='+DATA['asset_version'],html)
        self.assertIn('assets/handbook-cover.png?v='+DATA['asset_version'],html)
        self.assertIn('hiking, running, working out, and playing badminton', html)

    def test_publications_and_presentation_together(self):
        html = (ROOT/'index.html').read_text(encoding='utf-8')
        output = html.split('id="publications"',1)[1].split('</section>',1)[0]
        background = html.split('id="background"',1)[1].split('</section>',1)[0]
        self.assertIn('Publications &amp; Presentations',output)
        self.assertEqual(output.count('class="output-entry'),3)
        self.assertEqual(output.count('class="output-type">Journal article'),2)
        self.assertIn('Conference poster',output)
        self.assertEqual(re.findall(r'data-date="([^"]+)"',output),['2026','2025-06','2025-05'])
        self.assertEqual([p['date'] for p in BUILDER['ordered_outputs']()],['2026','2025-06','2025-05'])
        self.assertIn(escape(DATA['presentation']['title']),output)
        self.assertNotIn(escape(DATA['presentation']['title']),background)
        self.assertEqual(html.count(escape(DATA['presentation']['title'])),1)
        self.assertIn('Article citations (.bib)',output)

    def test_expanded_research(self):
        html = (ROOT/'index.html').read_text(encoding='utf-8')
        background = html.split('id="background"',1)[1].split('</section>',1)[0]
        self.assertEqual(background.count('class="research-project"'),3)
        primary = background.split('<details',1)[0]
        for research in DATA['research']:
            self.assertIn(escape(research['title']),primary)
            for contribution in research['contributions']:
                self.assertIn(escape(contribution),primary)
        self.assertIn('228 participants across the behavioral and EEG experiments',primary)
        self.assertIn('recruited 60 participants',primary)
        self.assertIn('recruiting 30 participants',primary)
        self.assertIn('Earlier work in linguistics',background)
        self.assertIn('Methods &amp; tools',background)

    def test_complete_visible_honors(self):
        expected = [
            ('National Scholarship','2025'),
            ('Outstanding Graduate of Sichuan University','2025'),
            ('Outstanding Graduate Student of Sichuan University','2023–2024'),
            ('Outstanding Graduate Student Leader, College of Literature and Journalism','2023–2024, 2024–2025'),
            ('Outstanding Teaching Assistant of Sichuan University','2024'),
            ('Outstanding Student','2024'),
        ]
        self.assertEqual([(h['title'],h['years']) for h in DATA['honors']],expected)
        html = (ROOT/'index.html').read_text(encoding='utf-8')
        honors = html.split('id="honors"',1)[1].split('</section>',1)[0]
        self.assertNotIn('<details',honors)
        self.assertEqual(honors.count('class="honor-item"'),6)
        for title, years in expected:
            self.assertIn(escape(title),honors)
            self.assertIn(years,honors)
        self.assertIn('Jinan University',honors)
        self.assertNotIn('Selected honors',html)

    def test_cool_palette(self):
        css = (ROOT/'assets/main.css').read_text(encoding='utf-8')
        self.assertIn('--paper: #f8fafc',css)
        self.assertIn('--ink: #20334b',css)
        self.assertIn('--accent: #315e8a',css)
        for old_color in ['#f8f5ef','#332d28','#85533f','#eee8df','#e5d5c5','#9f755e']:
            self.assertNotIn(old_color,css)
        self.assertIn('content="#f8fafc"',(ROOT/'index.html').read_text(encoding='utf-8'))

    def test_local_links(self):
        for file in [ROOT/'index.html',ROOT/'zh/index.html']:
            for link in Parser(file).urls:
                url = urlsplit(link)
                if url.scheme or url.netloc:
                    continue
                target = (file.parent/unquote(url.path)).resolve() if url.path else file
                self.assertTrue(target.is_file(),str(target))
                if url.fragment:
                    self.assertIn(url.fragment,Parser(target).ids)
            for _,attrs in Parser(file).tags:
                if attrs.get('target')=='_blank':
                    self.assertIn('noopener',attrs.get('rel',''))

    def test_ra_and_material(self):
        html = (ROOT/'index.html').read_text(encoding='utf-8')
        self.assertIn('Research Assistant',html)
        self.assertIn('The Hong Kong Polytechnic University',html)
        self.assertIn('Dr. Jiaqiang Zhu',html)
        self.assertIn('datetime="2026-08-10"',html)
        self.assertIn('August 10, 2026 – present',html)
        self.assertIn('23 pages',html)
        self.assertIn('Attachment 2',html)
        for resource in DATA['materials']:
            self.assertTrue((ROOT/resource['file']).read_bytes().startswith(b'%PDF-'))

    def test_bibliography(self):
        bib = (ROOT/'publications.bib').read_text(encoding='utf-8')
        self.assertEqual(bib.count('@article{'),2)
        self.assertEqual(bib.count('{'),bib.count('}'))
        self.assertIn('10.1016/j.jneuroling.2025.101249',bib)
        self.assertIn('10.1016/j.cortex.2025.04.003',bib)

    def test_no_obsolete_or_private_content(self):
        html = (ROOT/'index.html').read_text(encoding='utf-8')
        for token in ['cv_Liu','tel:','Chengdu','Master\'s student','fonts.googleapis.com','PsychoPy','cortex.2024.08.009']:
            self.assertNotIn(token,html)
        self.assertIsNone(re.search(r'(?<!\d)1\d{2}[- ]\d{4}[- ]\d{4}(?!\d)',html))
        self.assertEqual(len(ET.parse(ROOT/'sitemap.xml').findall('.//{*}loc')),1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
