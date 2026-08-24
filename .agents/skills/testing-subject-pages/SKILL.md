---
name: testing-subject-pages
description: Build and locally preview the Quiz site's generated pages (subject pages, quizzes, notes) end-to-end. Use when verifying changes to generator/build.py, templates, or generated docs/ HTML.
---

# Testing the Quiz site locally

## Build
- Syntax check: `python -m py_compile generator/build.py generator/build_notes.py`
- Full build (also runs test-series and notes builders): `python generator/build.py`
- Output goes to `docs/` (GitHub Pages). Subject pages are generated from `templates/subject-page.html`.

## Local preview under the /Quiz/ base path
Generated pages contain `<base href="/Quiz/">` and absolute `/Quiz/...` links, so serving `docs/` directly at the server root breaks links. Instead:

```bash
mkdir -p ~/serve && ln -sfn /path/to/repo/docs ~/serve/Quiz
cd ~/serve && python3 -m http.server 8000
```

Then open e.g. `http://localhost:8000/Quiz/polity/index.html`.

## What to verify on subject pages
- No unresolved tokens: `rg -o '\{\{[A-Z_]+\}\}' docs/*/index.html` should return nothing.
- Quiz wording (not notes wording) in title/kicker/h1/breadcrumb; chapter titles in Hindi (mappings live in `SUBJECT_LABELS_HI` / `TOPIC_LABELS_HI` in `generator/build.py` — new English topic names must be added there).
- Quiz-card links open working quiz pages; the search box filters quiz rows client-side.

## Pitfalls
- Subject folder slugs are overridden in `SUBJECT_FOLDERS` (e.g. `art-culture`, `uttar-pradesh-gk`); generic slugging may produce wrong folders.
- Typing Devanagari text via GUI automation may fail silently; filter tests can use Latin text present in quiz titles (e.g. "quiz - 02").
- `python generator/build.py` also regenerates notes/test-series pages and `docs/index.html`; unrelated diffs may appear — commit only files in scope.
- A GitHub Action ("Auto-generated HTML pages from Dashboard JSON") may push commits to your branch; pull/review before pushing.

## Devin Secrets Needed
- None (static site, no auth required).
