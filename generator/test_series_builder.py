from pathlib import Path
import json
import html
import re
import shutil
import os

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "test-series"
OUTPUT = ROOT / "docs" / "test-series"
TEMPLATES = ROOT / "templates"
SITE_URL = os.getenv("SITE_URL", "https://dolatrammpi-coder.github.io/Quiz").rstrip("/")


def esc(value):
    return html.escape(str(value), quote=True)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def slugify(value):
    value = str(value).strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "item"


def validate_test(data, path):
    required = ["exam", "title", "questions"]
    for key in required:
        if key not in data:
            raise ValueError(f"{path}: missing '{key}'")
    if not isinstance(data["questions"], list) or not data["questions"]:
        raise ValueError(f"{path}: questions must be a non-empty list")

    for number, q in enumerate(data["questions"], 1):
        for key in ("question", "options", "answer", "explanation"):
            if key not in q:
                raise ValueError(f"{path}: question {number}: missing '{key}'")
        if not isinstance(q["options"], list) or len(q["options"]) != 4:
            raise ValueError(f"{path}: question {number}: exactly 4 options required")
        answer = q["answer"]
        if isinstance(answer, int):
            if answer < 0 or answer > 3:
                raise ValueError(f"{path}: question {number}: answer index must be 0-3")
        elif isinstance(answer, str):
            if answer.upper() not in {"A", "B", "C", "D"} and answer not in q["options"]:
                raise ValueError(f"{path}: question {number}: answer must be A-D, 0-3, or exact option text")
        else:
            raise ValueError(f"{path}: question {number}: invalid answer")


def answer_index(q):
    answer = q["answer"]
    if isinstance(answer, int):
        return answer
    if isinstance(answer, str):
        upper = answer.upper().strip()
        if upper in {"A", "B", "C", "D"}:
            return "ABCD".index(upper)
        if answer in q["options"]:
            return q["options"].index(answer)
    raise ValueError("Unable to normalize answer")


def render(template, replacements):
    for key, value in replacements.items():
        template = template.replace("{{ " + key + " }}", str(value))
    return template


def make_breadcrumb_schema(items):
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(items)
        ]
    }, ensure_ascii=False)


def build_exam_page(template, exam, tests, exam_slug):
    base_url = "../../"
    exam_url = f"{SITE_URL}/test-series/{exam_slug}/"
    test_cards = []
    for test in tests:
        test_cards.append(f'''<a class="test-card" href="{esc(test["slug"])}/index.html">
  <div class="test-card-main">
    <span class="test-number">Test {esc(test.get("test_number", ""))}</span>
    <h2>{esc(test["title"])}</h2>
    <p>{esc(test.get("short_description", test.get("description", "")))}</p>
  </div>
  <div class="test-card-meta">
    <span>{len(test["questions"])} प्रश्न</span>
    <span>{esc(test.get("duration_label", "समय निर्धारित नहीं"))}</span>
    <strong>शुरू करें →</strong>
  </div>
</a>''')

    seo = exam.get("seo_content", "")
    if not seo:
        seo = f"<p>{esc(exam.get('description', ''))}</p>"

    breadcrumb = make_breadcrumb_schema([
        ("Home", SITE_URL + "/"),
        ("Test Series", SITE_URL + "/test-series/"),
        (exam["name"], exam_url),
    ])
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": exam["name"] + " Test Series",
        "description": exam.get("description", ""),
        "url": exam_url,
        "isPartOf": {"@type": "WebSite", "name": "My Study Portal", "url": SITE_URL + "/"}
    }, ensure_ascii=False)

    return render(template, {
        "exam_name": esc(exam["name"]),
        "exam_description": esc(exam.get("description", "")),
        "meta_description": esc(exam.get("meta_description", exam.get("description", ""))),
        "tests_html": "\n".join(test_cards),
        "seo_content": seo,
        "base_url": base_url,
        "series_url": "../../index.html",
        "canonical_url": esc(exam_url),
        "breadcrumb_schema": breadcrumb,
        "page_schema": schema,
    })


def build_textual_content(test):
    """Build crawlable, test-specific text from optional JSON content fields.

    Supported fields:
      overview / overview_text: short useful overview
      preparation_tips / tips: list of practical tips
      seo_content: optional HTML supplied intentionally by the content author
    """
    parts = []

    overview = test.get("overview", test.get("overview_text", ""))
    if overview:
        parts.append(f"<p>{esc(overview)}</p>")

    tips = test.get("preparation_tips", test.get("tips", []))
    if isinstance(tips, list) and tips:
        parts.append("<h3>तैयारी के उपयोगी सुझाव</h3><ul>")
        parts.extend(f"<li>{esc(item)}</li>" for item in tips if str(item).strip())
        parts.append("</ul>")

    seo = test.get("seo_content", "")
    if seo:
        parts.append(str(seo))

    if not parts:
        description = test.get("description", "")
        if description:
            parts.append(f"<p>{esc(description)}</p>")

    return "\n".join(parts)


def build_test_page(template, exam, test, exam_slug, test_slug, ordered_tests):
    base_url = "../../../"
    exam_url = f"{SITE_URL}/test-series/{exam_slug}/"
    test_url = f"{exam_url}{test_slug}/"

    questions = []
    for number, q in enumerate(test["questions"], 1):
        questions.append({
            "id": number,
            "question": q["question"],
            "options": q["options"],
            "answer": answer_index(q),
            "explanation": q.get("explanation", ""),
        })

    instructions = test.get("instructions")
    if not isinstance(instructions, list) or not instructions:
        instructions = [
            "सभी प्रश्न बहुविकल्पीय हैं।",
            "प्रत्येक प्रश्न का केवल एक सही उत्तर है।",
            "समय समाप्त होने पर परीक्षा स्वतः सबमिट हो जाएगी।",
        ]
    instructions_html = "".join(f"<li>{esc(x)}</li>" for x in instructions if str(x).strip())

    faq = test.get("faq", [])
    if not isinstance(faq, list):
        faq = []
    faq_parts = []
    for item in faq:
        if not isinstance(item, dict):
            continue
        question = item.get("question", "")
        answer = item.get("answer", "")
        if question and answer:
            faq_parts.append(f"<details><summary>{esc(question)}</summary><p>{esc(answer)}</p></details>")
    faq_html = "".join(faq_parts)
    if not faq_html:
        faq_html = "<p>इस टेस्ट से संबंधित सामान्य जानकारी ऊपर दिए गए विवरण और परीक्षा निर्देशों में उपलब्ध है।</p>"

    related = []
    for other in ordered_tests:
        if other["slug"] == test_slug:
            continue
        related.append(f'<a href="../{esc(other["slug"])}/index.html">{esc(other["title"])}</a>')
    related_html = "".join(related[:8])

    negative = float(test.get("negative_marking", 0))
    duration = int(test.get("duration_minutes", 0))
    marks = float(test.get("marks", len(questions)))

    seo = build_textual_content(test)

    breadcrumb = make_breadcrumb_schema([
        ("Home", SITE_URL + "/"),
        ("Test Series", SITE_URL + "/test-series/"),
        (exam["name"], exam_url),
        (test["title"], test_url),
    ])
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": test["title"],
        "description": test.get("description", ""),
        "url": test_url,
        "isPartOf": {"@type": "CollectionPage", "name": exam["name"], "url": exam_url}
    }, ensure_ascii=False)

    return render(template, {
        "title": esc(test["title"]),
        "exam_name": esc(exam["name"]),
        "description": esc(test.get("description", "")),
        "meta_description": esc(test.get("meta_description", test.get("description", ""))),
        "questions_json": json.dumps(questions, ensure_ascii=False).replace("</", "<\\/"),
        "total_questions": len(questions),
        "duration_minutes": duration,
        "duration_label": esc(test.get("duration_label", f"{duration} मिनट" if duration else "समय निर्धारित नहीं")),
        "marks": marks,
        "negative_marking": negative,
        "negative_label": esc(test.get("negative_marking_label", f"{negative:g} अंक" if negative else "नहीं")),
        "instructions_html": instructions_html,
        "faq_html": faq_html,
        "related_tests_html": related_html,
        "seo_content": seo,
        "base_url": base_url,
        "exam_url": "../../index.html",
        "series_url": "../../../index.html",
        "canonical_url": esc(test_url),
        "breadcrumb_schema": breadcrumb,
        "page_schema": schema,
    })


def build():
    if not CONTENT.exists():
        print("Test Series: content/test-series/ not found; nothing to build.")
        return

    test_template_path = TEMPLATES / "test-series-test.html"
    exam_template_path = TEMPLATES / "test-series-exam.html"
    if not test_template_path.exists() or not exam_template_path.exists():
        raise FileNotFoundError("Dedicated Test Series exam/test templates are missing.")

    exam_template = exam_template_path.read_text(encoding="utf-8")
    test_template = test_template_path.read_text(encoding="utf-8")

    exams = []
    for exam_dir in sorted(p for p in CONTENT.iterdir() if p.is_dir()):
        exam_slug = exam_dir.name
        series_path = exam_dir / "series.json"

        if series_path.exists():
            exam = load_json(series_path)
        else:
            exam = {
                "name": exam_slug.replace("-", " ").title(),
                "slug": exam_slug,
            }
            print(f"Info: {exam_dir}: series.json missing; using folder name.")

        exam.setdefault("name", exam_slug.replace("-", " ").title())
        exam.setdefault("slug", exam_slug)

        tests = []
        for path in sorted(exam_dir.glob("*.json")):
            if path.name == "series.json":
                continue
            try:
                test = load_json(path)
                validate_test(test, path)
                test["slug"] = test.get("slug", path.stem)
                test.setdefault("test_number", len(tests) + 1)
                tests.append(test)
            except Exception as exc:
                print(f"Skipping {path}: {exc}")

        if not tests:
            print(f"Skipping {exam_dir}: no valid tests")
            continue

        tests.sort(key=lambda x: (int(x.get("test_number", 999999)), x["slug"]))
        exams.append({"slug": exam_slug, "name": exam["name"], "description": exam.get("description", ""), "tests": tests})

        exam_output = OUTPUT / exam_slug
        exam_output.mkdir(parents=True, exist_ok=True)
        (exam_output / "index.html").write_text(build_exam_page(exam_template, exam, tests, exam_slug), encoding="utf-8")

        for test in tests:
            test_slug = test["slug"]
            test_output = exam_output / test_slug
            test_output.mkdir(parents=True, exist_ok=True)
            html_text = build_test_page(test_template, exam, test, exam_slug, test_slug, tests)
            (test_output / "index.html").write_text(html_text, encoding="utf-8")

    if not exams:
        print("Test Series: no valid exam/test content found; existing docs/test-series pages left untouched.")
        return

    print(f"TEST SERIES BUILD SUCCESSFUL! {len(exams)} exams generated.")


if __name__ == "__main__":
    build()
