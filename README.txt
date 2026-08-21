HISTORY GROUPING FIX

This builder keeps the requested architecture:
- Main 8-subject Notes landing page is untouched.
- A grouped subject such as History can have a group named Modern History.
- Modern History is a NON-CLICKABLE group heading.
- Chapters inside the group are numbered clickable rows.
- Clicking a chapter opens /subject/chapter/index.html (Chapter Notes).
- No separate Modern History page is generated.
- Existing grouped-subject behavior such as Polity remains grouping-based.

Install:
  cd ~/Quiz
  unzip -o /sdcard/Download/history-grouping-fix.zip -d ~/Quiz

Build:
  python generator/build_notes.py

IMPORTANT:
The CSS in templates/grouped-history-visual.css must be included in
templates/subject-page.html's <style> block. The builder emits the required
.chapter-card/.topic-list/.topic markup.
