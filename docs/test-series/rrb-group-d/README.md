# RRB Group D Test Batch

## Layout

- `index.html` — series landing page with links to all ten practice tests.
- `chronology.json` — ordered manifest containing test URL, question range/count, and expected section distribution.
- `test-1/index.html` through `test-10/index.html` — independent quiz pages, each with its own question bank and quiz engine.

## Expected batch shape

The current manifest specifies 10 tests × 100 questions = 1,000 question entries. Each test is expected to use the following section counts:

| Section | Questions |
|---|---:|
| General Science | 25 |
| Mathematics | 25 |
| General Intelligence & Reasoning | 30 |
| General Awareness / Current Affairs | 20 |
| **Total** | **100** |

Confirm the actual question bank and section labels before modifying a test. Do not adjust the manifest merely to hide a mismatch.

## URLs

- Series page: `/test-series/rrb-group-d/`
- Test pages: `/test-series/rrb-group-d/test-1/` … `/test-series/rrb-group-d/test-10/`

## Editing rules

1. Make presentation-only changes without replacing the question bank or quiz-engine logic.
2. Question content can include text, mathematical notation, images, diagrams, or tables. Preserve all such content when transferring or normalizing source data.
3. After changes, verify navigation, timer, answer selection, question palette, review marking, submit confirmation, scoring, and explanations.
4. Check mobile and desktop widths, and ensure no table or diagram causes horizontal overflow.
5. If a test is added, removed, or reordered, update both the series page and `chronology.json`.
