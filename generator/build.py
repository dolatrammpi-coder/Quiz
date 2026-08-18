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
        # लिस्ट को उल्टा करें और टॉप 5 चुनें
        for q in reversed(all_quizzes[-5:]):
            latest_html += f"""
            <a href="{q['link']}" class="block bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md hover:border-blue-300 transition group">
                <div class="flex justify-between items-center">
                    <div>
                        <span class="text-[10px] font-bold text-blue-600 bg-blue-50 border border-blue-100 px-2 py-1 rounded mb-1.5 inline-block uppercase tracking-wider">{q['subject']}</span>
                        <h3 class="font-bold text-gray-800 group-hover:text-blue-700 transition">{q['title']}</h3>
                    </div>
                    <i class="fas fa-chevron-right text-gray-300 group-hover:text-blue-500 transition"></i>
                </div>
            </a>
            """
        
        if not latest_html:
            latest_html = "<p class='text-gray-500 text-sm p-4 bg-gray-50 rounded-lg border border-dashed border-gray-300 text-center'>अभी कोई क्विज़ उपलब्ध नहीं है।</p>"
            
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
        quiz_link = f"{relative.parent.name}/{path.stem}/index.html"
        site_data[subject_name][topic_name].append({"title": data["title"], "link": quiz_link})
        all_quizzes.append({"title": data["title"], "link": quiz_link, "subject": subject_name})
        quizzes += 1

    generate_subject_pages(site_data)
    build_homepage(all_quizzes)
    print(f"\nBUILD SUCCESSFUL! Generated {quizzes} quizzes.")

if __name__ == "__main__":
    build()
