from pathlib import Path
import json
import shutil
import re
import html
from collections import defaultdict
from test_series_builder import build as build_test_series
from build_notes import build as build_notes

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUTPUT = ROOT / "docs"
TEMPLATES = ROOT / "templates"

SUBJECT_LABELS_HI = {
    "History": "इतिहास",
    "Geography": "भूगोल",
    "Environment": "पर्यावरण",
    "Art & Culture": "कला व संस्कृति",
    "Polity": "राजव्यवस्था",
    "Current Affairs": "करंट अफेयर्स",
    "Science": "विज्ञान",
    "Economy": "अर्थव्यवस्था",
    "Economics": "अर्थशास्त्र",
    "Hindi": "हिंदी",
    "English": "अंग्रेजी",
    "UP GK": "उत्तर प्रदेश सामान्य ज्ञान",
    "Uttarakhand GK": "उत्तराखंड सामान्य ज्ञान",
    "Miscellaneous GK": "विविध सामान्य ज्ञान",
}

SUBJECT_PAGE_NAMES = (
    "History",
    "Geography",
    "Environment",
    "Art & Culture",
    "Polity",
    "Current Affairs",
    "Science",
    "Economy",
    "Hindi",
    "English",
    "UP GK",
    "Uttarakhand GK",
    "Miscellaneous GK",
)

SUBJECT_FOLDERS = {
    "Art & Culture": "art-culture",
    "UP GK": "uttar-pradesh-gk",
    "Uttarakhand GK": "uttarakhand-gk",
}

TOPIC_LABELS_HI = {
    "Constitutional Evolution": "संवैधानिक विकास",
    "Features of Constitution": "संविधान की विशेषताएँ",
    "Economic Planning in India": "भारत में आर्थिक नियोजन",
    "Economic Planning In India": "भारत में आर्थिक नियोजन",
    "Monthly Current Affairs": "मासिक करंट अफेयर्स",
    "Modern India": "आधुनिक भारत",
}


def escape_html(value):
    return html.escape(str(value or ""), quote=True)


def hindi_label(value, labels):
    value = str(value or "").strip()
    return labels.get(value, value)


def load_explanations(quiz_path):
    explanation_path = quiz_path.with_name(quiz_path.stem + ".explanations.json")
    if not explanation_path.exists():
        return {}
    try:
        data = json.loads(explanation_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error reading explanation: {e}")
        return {}
    if "explanations" in data:
        data = data["explanations"]
    return {str(k): str(v) for k, v in data.items()}

def validate_quiz(data, path):
    required = ["title", "subject", "topic", "questions"]
    for key in required:
        if key not in data:
            raise ValueError(f"{path}: missing '{key}'")

def generate_quiz_html(data, explanations, master_template_text, depth):
    questions_json = []
    for number, q in enumerate(data["questions"], 1):
        questions_json.append({
            "id": number,
            "q": q["question"],
            "options": q["options"],
            "correct": q["answer"],
            "explanation": explanations.get(str(number), "")
        })
    questions_js_str = json.dumps(questions_json, ensure_ascii=False)
    base_url = "../" * depth
    subject_folder = str(data.get("subject", "Uncategorized")).strip().lower().replace(" ", "-")

    html = master_template_text.replace("{{ title }}", str(data["title"]))
    html = html.replace("{{ description }}", str(data.get("description", "")))
    html = html.replace("{{ subject }}", str(data["subject"]))
    html = html.replace("{{ questions_json }}", questions_js_str)
    html = html.replace("{{ base_url }}", base_url)
    html = html.replace("{{ seo_content }}", str(data.get("seo_content", "")))
    html = html.replace("{{ subject_folder }}", subject_folder)
    
    # 🌟 "Self-Aware" Meta Tag Injection 🌟 (HTML के अंदर डेटाबेस छुपाना)
    meta_data = {
        "title": str(data["title"]),
        "subject": str(data.get("subject", "Uncategorized")),
        "topic": str(data.get("topic", "General"))
    }
    meta_script = f'\n    <!-- Self-Aware Database Tag (SEO Friendly) -->\n    <script type="application/json" id="quiz-meta">{json.dumps(meta_data, ensure_ascii=False)}</script>\n</head>'
    html = html.replace("</head>", meta_script)
    
    return html

def generate_subject_pages(site_data):
    subject_template_path = TEMPLATES / "subject-page.html"
    if not subject_template_path.exists():
        print("WARNING: subject-page.html not found.")
        return

    subject_template = subject_template_path.read_text(encoding="utf-8")

    for subject_name, topics in site_data.items():
        if subject_name in {"Test Series", "Subject Wise Notes"}:
            continue

        subject_folder = SUBJECT_FOLDERS.get(
            subject_name,
            re.sub(
                r"-+",
                "-",
                re.sub(r"\s+", "-", subject_name.strip().lower()),
            ).strip("-"),
        )
        subject_dir = OUTPUT / subject_folder
        subject_dir.mkdir(parents=True, exist_ok=True)

        chapters_html = []
        for topic_name, quizzes in topics.items():
            quiz_links = []
            for number, quiz in enumerate(quizzes, 1):
                quiz_links.append(
                    f'<a class="topic" href="/Quiz/{escape_html(subject_folder)}/{escape_html(quiz["link"])}">'
                    '<span class="topic-left">'
                    f'<span class="topic-num">{number:02d}</span>'
                    f'<span class="topic-name">{escape_html(quiz["title"])}'
                    '<span class="topic-note">क्विज़ शुरू करें</span>'
                    '</span></span><span class="arrow">›</span></a>'
                )

            if quiz_links:
                chapters_html.append(
                    '<section class="chapter-card">'
                    '<div class="chapter-head"><div>'
                    f'<div class="chapter-title">{escape_html(hindi_label(topic_name, TOPIC_LABELS_HI))}</div>'
                    '</div></div><div class="topic-list">'
                    + "\n".join(quiz_links)
                    + "</div></section>"
                )

        subject_hi = hindi_label(subject_name, SUBJECT_LABELS_HI)
        values = {
            "SUBJECT_TITLE_EN": subject_name,
            "SUBJECT_TITLE_HI": subject_hi,
            "SUBJECT_NAME": subject_name,
            "SUBJECT_DESCRIPTION": f"{subject_hi} के अध्याय और अभ्यास क्विज़।",
            "SUBJECT_ICON": "📚",
            "CHAPTER_SECTION_TITLE": f"{subject_hi} के अध्याय",
            "CHAPTERS_HTML": "\n".join(chapters_html) or (
                '<div class="no-results" style="display:block">'
                "अभी कोई अध्याय उपलब्ध नहीं है।</div>"
            ),
            "INFO_TITLE": f"{subject_hi} क्विज़ कैसे उपयोग करें?",
            "INFO_DESCRIPTION": f"{subject_hi} के अध्याय चुनकर संबंधित क्विज़ का अभ्यास करें।",
            "HOME_URL": "/Quiz/index.html",
            "NOTES_HOME_URL": "/Quiz/subject-wise-notes/index.html",
            "TEST_SERIES_URL": "/Quiz/test-series/index.html",
            "ABOUT_URL": "/Quiz/about/index.html",
            "PRIVACY_URL": "/Quiz/privacy-policy/index.html",
            "DISCLAIMER_URL": "/Quiz/disclaimer/index.html",
            "CONTACT_URL": "/Quiz/contact/index.html",
            "TERMS_URL": "/Quiz/terms-and-conditions/index.html",
        }

        final_html = subject_template
        for token, value in values.items():
            final_html = final_html.replace("{{" + token + "}}", str(value))

        output_file = subject_dir / "index.html"
        output_file.write_text(final_html, encoding="utf-8")

def build_homepage(all_quizzes):
    template = TEMPLATES / "index.html"
    destination = OUTPUT / "index.html"
    if template.exists():
        html = template.read_text(encoding="utf-8")
        
        latest_html = ""
        for q in reversed(all_quizzes[-5:]):
            link = q["link"]
            subject = q["subject"]
            title = q["title"]
            
            latest_html += f"""
            <a href="{link}" style="display: block; background-color: #ffffff; padding: 1rem; border-radius: 0.75rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); border: 1px solid #e5e7eb; margin-bottom: 0.75rem; text-decoration: none;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 0.70rem; font-weight: bold; color: #1d4ed8; background-color: #eff6ff; border: 1px solid #bfdbfe; padding: 0.25rem 0.5rem; border-radius: 0.375rem; margin-bottom: 0.5rem; display: inline-block; text-transform: uppercase; letter-spacing: 0.05em;">{subject}</span>
                        <h3 style="font-weight: bold; color: #1f2937; font-size: 1rem; margin: 0;">{title}</h3>
                    </div>
                    <span style="color: #9ca3af; font-weight: bold;">❯</span>
                </div>
            </a>
            """
        
        if not latest_html:
            latest_html = "<p style='color: #6b7280; font-size: 0.875rem; padding: 1rem; background-color: #f9fafb; border-radius: 0.5rem; border: 1px dashed #d1d5db; text-align: center;'>अभी कोई क्विज़ उपलब्ध नहीं है।</p>"
            
        html = html.replace("{{ latest_quizzes }}", latest_html)
        destination.write_text(html, encoding="utf-8")

def build():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    quiz_template_path = TEMPLATES / "quiz.html"
    master_template_text = quiz_template_path.read_text(encoding="utf-8")
    
    # 1. JSON से HTML बनाना (अगर JSON मौजूद हैं)
    if CONTENT.exists():
        for path in sorted(CONTENT.rglob("*.json")):
            relative = path.relative_to(CONTENT)

            # Dedicated builders handle these JSON files.
            # Generic Quiz builder must never validate/process them.
            if "test-series" in relative.parts:
                continue

            if "notes" in relative.parts:
                continue

            if path.name.endswith(".explanations.json"):
                continue

            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                validate_quiz(data, path)
                explanations = load_explanations(path)
            except Exception as e:
                print(f"Skipping {path}: {e}")
                continue

            quiz_dir = OUTPUT / relative.parent / path.stem
            quiz_dir.mkdir(parents=True, exist_ok=True)
            depth = len(relative.parts)

            final_html = generate_quiz_html(data, explanations, master_template_text, depth)
            output_file = quiz_dir / "index.html"
            output_file.write_text(final_html, encoding="utf-8")

    # 2. HTML से वापस डेटाबेस पढ़ना (अब JSON पर कोई निर्भरता नहीं)
    site_data = defaultdict(lambda: defaultdict(list))
    all_quizzes = []
    quizzes_found = 0
    
    # docs/ फोल्डर के अंदर के सभी HTML पेजों को स्कैन करना
    for html_path in sorted(OUTPUT.rglob("index.html")):
        if html_path.parent == OUTPUT: continue # होमपेज छोड़ें
        if html_path.parent.parent == OUTPUT: continue # सब्जेक्ट पेज छोड़ें
        
        try:
            content_text = html_path.read_text(encoding="utf-8")
            # छिपा हुआ Meta-Tag खोजना
            match = re.search(r'<script type="application/json" id="quiz-meta">(.*?)</script>', content_text, re.DOTALL)
            if match:
                meta = json.loads(match.group(1))
                relative_path = html_path.relative_to(OUTPUT)
                
                subject_page_link = "/".join(relative_path.parts[1:])
                homepage_link = relative_path.as_posix()
                
                site_data[meta["subject"]][meta["topic"]].append({"title": meta["title"], "link": subject_page_link})
                all_quizzes.append({"title": meta["title"], "link": homepage_link, "subject": meta["subject"]})
                quizzes_found += 1
        except Exception as e:
            print(f"Error reading meta from {html_path}: {e}")

    # 3. वेबसाइट की लिस्ट अपडेट करना (केवल HTML के दम पर)
    for subject_name in SUBJECT_PAGE_NAMES:
        site_data.setdefault(subject_name, defaultdict(list))

    generate_subject_pages(site_data)
    build_homepage(all_quizzes)

    # Test Series का dedicated builder
    try:
        build_test_series()
    except Exception as e:
        print(f"WARNING: Test Series build failed: {e}")

    # Subject Wise Notes का dedicated builder
    # Notes अपने standalone static HTML pages बनाता है।
    try:
        build_notes()
    except Exception as e:
        print(f"WARNING: Notes build failed: {e}")

    print(f"\nBUILD SUCCESSFUL! Processed {quizzes_found} quizzes perfectly.")

if __name__ == "__main__":
    build()
