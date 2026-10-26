#!/usr/bin/env python3
"""Replace internal /index.html link aliases only when sitemap confirms the canonical URL."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, urljoin
import xml.etree.ElementTree as ET

ROOT = Path("docs")
SITEMAP = ROOT / "sitemap.xml"
ORIGIN = "https://lagale.in"

def load_sitemap_urls():
    tree = ET.parse(SITEMAP)
    urls = set()
    for node in tree.getroot().iter():
        if node.tag.rsplit("}", 1)[-1] == "loc" and node.text:
            p = urlsplit(node.text.strip())
            urls.add(urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or "/", "", "")))
    return urls

class HrefRewriter(HTMLParser):
    def __init__(self, text, sitemap_urls):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.sitemap_urls = sitemap_urls
        self.replacements = 0
        self.changed = []
        self.output = []
        self._rewrite()

    def _rewrite(self):
        # Work on original source with a narrow href-attribute regex so all other
        # whitespace, quoting, markup, and page content remain byte-for-byte intact.
        import re
        pattern = re.compile(r'(?i)(\\bhref\\s*=\\s*)(["\'])(.*?)\\2', re.DOTALL)
        last = 0
        for match in pattern.finditer(self.text):
            original = match.group(3)
            new = self._canonical_href(original)
            if new != original:
                self.output.append(self.text[last:match.start()])
                self.output.append(match.group(1) + match.group(2) + new + match.group(2))
                last = match.end()
                self.replacements += 1
                self.changed.append((original, new))
        if self.replacements:
            self.output.append(self.text[last:])
        self.result = "".join(self.output) if self.replacements else self.text

    def _canonical_href(self, href):
        # Only same-site absolute URLs or root-relative links are eligible.
        if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
            return href
        absolute = urljoin(ORIGIN + "/", href)
        current = urlsplit(absolute)
        if current.scheme.lower() not in ("http", "https") or current.netloc.lower() != "lagale.in":
            return href
        if not (current.path == "/index.html" or current.path.endswith("/index.html")):
            return href
        canonical_path = current.path[:-len("index.html")]
        canonical_url = urlunsplit(("https", "lagale.in", canonical_path, "", ""))
        if canonical_url not in self.sitemap_urls:
            return href
        rewritten_absolute = urlunsplit((current.scheme, current.netloc, canonical_path, current.query, current.fragment))
        # Preserve the author's URL style: root-relative links stay root-relative.
        if href.startswith("/"):
            rewritten = urlunsplit(("", "", canonical_path, current.query, current.fragment))
            return rewritten
        # For same-origin absolute links, retain their original scheme and host.
        if href.startswith("http://") or href.startswith("https://"):
            return rewritten_absolute
        return href

def main():
    sitemap_urls = load_sitemap_urls()
    changed_files = 0
    replacements = 0
    sample = []
    for path in ROOT.rglob("*.html"):
        if not path.is_file():
            continue
        original = path.read_text(encoding="utf-8")
        rewritten = HrefRewriter(original, sitemap_urls)
        if rewritten.replacements:
            path.write_text(rewritten.result, encoding="utf-8")
            changed_files += 1
            replacements += rewritten.replacements
            if len(sample) < 15:
                sample.append((str(path), rewritten.replacements, rewritten.changed[:3]))
    print(f"HTML files scanned: {sum(1 for p in ROOT.rglob('*.html') if p.is_file())}")
    print(f"Files changed: {changed_files}")
    print(f"Internal canonical-link replacements: {replacements}")
    print("Examples:")
    for file_name, count, changes in sample:
        print(f"- {file_name}: {count}")
        for old, new in changes:
            print(f"  {old} -> {new}")
    if replacements == 0:
        raise SystemExit("No eligible links changed; refusing to create an empty fix commit.")

if __name__ == "__main__":
    main()
