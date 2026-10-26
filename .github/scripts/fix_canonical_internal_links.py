#!/usr/bin/env python3
"""Replace internal /index.html link aliases only when sitemap confirms the canonical URL."""
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, urljoin
import re
import xml.etree.ElementTree as ET

ROOT = Path("docs")
ORIGIN = "https://lagale.in"

def load_sitemap_urls():
    tree = ET.parse(ROOT / "sitemap.xml")
    urls = set()
    for node in tree.getroot().iter():
        if node.tag.rsplit("}", 1)[-1] == "loc" and node.text:
            p = urlsplit(node.text.strip())
            urls.add(urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or "/", "", "")))
    return urls

def rewrite_href(href, sitemap_urls):
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
    if canonical_url not in sitemap_urls:
        return href
    if href.startswith("/"):
        return urlunsplit(("", "", canonical_path, current.query, current.fragment))
    if href.startswith(("http://", "https://")):
        return urlunsplit((current.scheme, current.netloc, canonical_path, current.query, current.fragment))
    return href

def main():
    sitemap_urls = load_sitemap_urls()
    pattern = re.compile(r'(?i)(\bhref\s*=\s*)(["\'])(.*?)\2', re.DOTALL)
    changed_files = 0
    replacements = 0
    html_files = list(ROOT.rglob("*.html"))
    sample = []
    for path in html_files:
        if not path.is_file():
            continue
        original = path.read_text(encoding="utf-8")
        local_changes = []
        def sub(match):
            nonlocal replacements
            old = match.group(3)
            new = rewrite_href(old, sitemap_urls)
            if new != old:
                replacements += 1
                if len(sample) < 15 and len(local_changes) < 3:
                    local_changes.append((old, new))
                return match.group(1) + match.group(2) + new + match.group(2)
            return match.group(0)
        updated = pattern.sub(sub, original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed_files += 1
            if len(sample) < 15:
                sample.append((str(path), local_changes))
    print(f"HTML files scanned: {len(html_files)}")
    print(f"Files changed: {changed_files}")
    print(f"Internal canonical-link replacements: {replacements}")
    for file_name, changes in sample:
        print(f"- {file_name}")
        for old, new in changes:
            print(f"  {old} -> {new}")
    if replacements == 0:
        raise SystemExit("No eligible links changed; refusing to create an empty fix commit.")

if __name__ == "__main__":
    main()
