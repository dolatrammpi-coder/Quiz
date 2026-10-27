# UKPSC GS-I English Test Series — Local Draft

Status: NOT READY TO PUBLISH. No remote push has been performed.

## Required translation standard

- Translate every question, option, explanation, subject/unit label, test title, instruction, and result/review interface into natural exam-quality English.
- Preserve question IDs, option ordering, `correctIndex`, marks, negative marks, difficulty, and timer/scoring logic exactly.
- Translate tables, match-the-following lists, statements, and code/options semantically; preserve their relationships and numbering.
- Keep official proper nouns and established terminology accurate (for example, Dholavira, Citadel, Middle Town, Lower Town, ASI, UNESCO).
- Do not use mechanical word substitution. Do not change a question's factual meaning to make the English sound smoother.

## QA gates before any local review build is called complete

1. Exactly 150 questions per test and 11 tests total.
2. Every question and all four options are English; no Hindi text remains in user-facing question data unless it is a proper noun/script item that must be preserved.
3. Explanations are natural English and omit Hindi-only metadata boilerplate.
4. IDs, option counts/order, `correctIndex`, marks, negative marks, duration, and total score equal the Hindi source.
5. Syntax check for HTML/JavaScript and a browser smoke test for navigation, timer, submit, score, review, and mobile UI.
6. Human review of ambiguous/history/polity/economy claims against the original source; unresolved items are flagged, never guessed.

## Local-only workflow

The English draft belongs under this directory. Original Hindi tests remain untouched. Do not push or publish until all QA gates pass and the owner reviews the local preview.
