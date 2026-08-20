# Dedicated Test Series System

This system is separate from the existing `generator/build.py` and `templates/quiz.html`.

Structure:

content/test-series/
  <exam-slug>/
    series.json
    test-01.json
    test-02.json

generator/test_series_builder.py
templates/test-series-index.html
templates/test-series-test.html

The builder creates:

docs/test-series/index.html
docs/test-series/<exam>/index.html
docs/test-series/<exam>/<test>/index.html

JSON test fields:
- exam
- title
- slug (optional; defaults to filename)
- test_number (optional; defaults to order)
- description
- duration_minutes
- duration_label (optional)
- marks
- negative_marking
- negative_marking_label (optional)
- instructions (optional list)
- seo_content (optional HTML)
- faq (optional list of question/answer objects)
- questions

Each question requires:
- question
- options: exactly 4
- answer: A/B/C/D, 0-3, or exact option text
- explanation

Important:
The existing quiz builder is untouched. This builder only reads `content/test-series/`.

GitHub Actions:
After the existing `python generator/build.py` step, add:

  - name: 4. Build Dedicated Test Series
    run: |
      python generator/test_series_builder.py

Then keep the existing docs commit/push step.
