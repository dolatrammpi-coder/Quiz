# Test Series Directory Structure

This directory contains the public test-series landing page, the reusable quiz-engine reference, and exam-specific test batches.

## Current layout

```text
docs/test-series/
├── index.html                         # Test-series category landing page
├── Mock Test & Practice Set Quiz Engine.html
│                                       # Standalone quiz-engine reference/template
├── README.md                          # This structure guide
└── rrb-group-d/
    ├── index.html                     # RRB Group D series page; links to each test
    ├── chronology.json                # Batch order, URLs, question counts and section outline
    ├── test-1/
    │   └── index.html                 # Self-contained quiz page and question bank
    ├── test-2/
    │   └── index.html
    ├── test-3/
    │   └── index.html
    ├── test-4/
    │   └── index.html
    ├── test-5/
    │   └── index.html
    ├── test-6/
    │   └── index.html
    ├── test-7/
    │   └── index.html
    ├── test-8/
    │   └── index.html
    ├── test-9/
    │   └── index.html
    └── test-10/
        └── index.html
```

## Responsibilities

- `docs/test-series/index.html`: all exam-series categories and links to each exam.
- `docs/test-series/rrb-group-d/index.html`: RRB Group D series overview and navigation to Test 1–10.
- `docs/test-series/rrb-group-d/chronology.json`: machine-readable test order and expected question/section counts.
- `docs/test-series/rrb-group-d/test-N/index.html`: each test's UI, timer, question bank, response state, submission, and result/solution view.

## URL convention

Keep folder and page names lowercase and URL-safe. Each test is published at:

`/test-series/rrb-group-d/test-N/`

The root `docs/` directory is deployed as the site root, so use root-relative links that match these public paths.

## Adding another exam series

Create a separate folder under `docs/test-series/<exam-slug>/` with its own `index.html`, chronology/manifest if useful, and numbered test folders. Add the exam card to `docs/test-series/index.html`. Do not mix question banks from different exams.

## Safe maintenance

- Preserve the question bank and quiz-engine behavior when changing layouts or styles.
- Retain media, diagrams, and tables that are part of question content; verify that they render correctly in both mobile and desktop views.
- Update links and metadata when a folder is renamed.
- Keep `chronology.json` in sync with the actual tests and question counts.
