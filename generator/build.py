from pathlib import Path
import json
import shutil
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUTPUT = ROOT / "docs"
TEMPLATES = ROOT / "templates"

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
    return html

def generate_subject_pages(site_data):
    subject_template_path = TEMPLATES / "subject.html"
    if not subject_template_path.exists():
        print("WARNING: subject.html not found.")
        return

    subject_template = subject_template_path.read_text(encoding="utf-8")

    for subject_name, topics in site_data.items():
        subject_folder = subject_name.strip().lower().replace(" ", "-")
        subject_dir = OUTPUT / subject_folder
        subject_dir.mkdir(parents=True, exist_ok=True)
        
        topics_html_list = []
        for topic_name, quizzes in topics.items():
            topic_html = f"""
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div class="bg-blue-50 px-5 py-3 border-b border-blue-100">
                    <h2 class="text-lg font-bold text-blue-800">{topic_name}</h2>
                </div>
                <div class="p-2">
                    <ul class="divide-y divide-gray-100">
            """
            for quiz in quizzes:
                topic_html += f"""
                        <li>
                            <a href="{quiz['link']}" class="block px-4 py-3 hover:bg-gray-50 transition flex justify-between items-center group">
                                <span class="text-gray-700 font-medium group-hover:text-blue-600 transition">{quiz['title']}</span>
                                <i class="fas fa-chevron-right text-gray-300 group-hover:text-blue-500 transition"></i>
                            </a>
                        </li>
                """
            topic_html += "</ul></div></div>"
            topics_html_list.append(topic_html)

        base_url = "../" # Depth is 1 for output/subject/index.html
        final_html = subject_template.replace("{{ subject_name }}", subject_name)
        final_html = final_html.replace("{{ topics_html }}", "\n".join(topics_html_list))
        final_html = final_html.replace("{{ base_url }}", base_url)
        
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
            
            # Inline CSS (ब्रह्मास्त्र) - यह कभी फेल नहीं हो सकता
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
    if not CONTENT.exists():
        raise SystemExit(f"CONTENT dir not found!")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    quiz_template_path = TEMPLATES / "quiz.html"
    master_template_text = quiz_template_path.read_text(encoding="utf-8")
    
    site_data = defaultdict(lambda: defaultdict(list))
    all_quizzes = []
    quizzes = 0

    for path in sorted(CONTENT.rglob("*.json")):
        if path.name.endswith(".explanations.json"): continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            validate_quiz(data, path)
            explanations = load_explanations(path)
        except Exception as e:
            print(f"Skipping {path}: {e}")
            continue

        relative = path.relative_to(CONTENT)
        quiz_dir = OUTPUT / relative.parent / path.stem
        quiz_dir.mkdir(parents=True, exist_ok=True)
        depth = len(relative.parts)

        final_html = generate_quiz_html(data, explanations, master_template_text, depth)
        output_file = quiz_dir / "index.html"
        output_file.write_text(final_html, encoding="utf-8")

        subject_name = data.get("subject", "Uncategorized")
        topic_name = data.get("topic", "General")
                # सब्जेक्ट पेज के लिए लिंक
        subject_page_link = f"{relative.parent.name}/{path.stem}/index.html"
        site_data[subject_name][topic_name].append({"title": data["title"], "link": subject_page_link})
        
        # होमपेज के लिए पूरा लिंक (as_posix लगाकर)
        homepage_link = f"{relative.parent.as_posix()}/{path.stem}/index.html"
        all_quizzes.append({"title": data["title"], "link": homepage_link, "subject": subject_name})

    generate_subject_pages(site_data)
    build_homepage(all_quizzes)
    print(f"\nBUILD SUCCESSFUL! Generated {quizzes} quizzes.")

if __name__ == "__main__":
    build()
