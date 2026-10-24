# RRB Group D Test Series — folder structure

The existing ten `test-N/index.html` pages remain in place so their public URLs are unchanged.

```text
docs/test-series/
├── index.html
├── Mock Test & Practice Set Quiz Engine.html
└── rrb-group-d/
    ├── index.html                  # batch landing page; links to all ten tests
    ├── chronology.json             # test order, question counts and audit metadata
    ├── STRUCTURE.md                # this structure guide
    ├── assets/
    │   ├── css/                    # shared quiz-engine styles (next extraction step)
    │   └── js/                     # shared quiz-engine logic (next extraction step)
    ├── data/                       # question-bank JSON with media/table markup preserved
    ├── templates/                  # reusable test-page template
    ├── test-1/index.html            # existing standalone test page
    ├── test-2/index.html
    ├── test-3/index.html
    ├── test-4/index.html
    ├── test-5/index.html
    ├── test-6/index.html
    ├── test-7/index.html
    ├── test-8/index.html
    ├── test-9/index.html
    └── test-10/index.html
```

## Safe migration rules

- Keep `test-1/` through `test-10/` URLs stable.
- Do not strip question HTML: images, tables, equations, and formatting must survive extraction to JSON.
- Extract shared CSS/JS only after checking all ten pages for differences; avoid changing quiz behavior during a structure-only change.
- Keep the question data for each test separate and validate question count, options, answer key, and explanations before switching a page to shared assets.
- Update `chronology.json` if a test's path or counts change.

`assets/`, `data/`, and `templates/` are intended staging folders; the current test pages have not yet been rewritten to depend on them.