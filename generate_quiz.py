import json
from pathlib import Path

def generate_quiz_pages():
    content_dir = Path("content/quiz")
    template_home = Path("templates/quiz-subject-home.html")
    template_chapter = Path("templates/quiz-chapter.html")
    template_quiz = Path("templates/quiz-page.html")
    output_base = Path("docs")
    
    if not content_dir.exists():
        print("❌ content/quiz folder nahi hai")
        return
    
    json_files = list(content_dir.glob("*.json"))
    if not json_files:
        print("❌ content/quiz me koi JSON nahi")
        return
    
    home_tpl = template_home.read_text(encoding="utf-8")
    chapter_tpl = template_chapter.read_text(encoding="utf-8")
    quiz_tpl = template_quiz.read_text(encoding="utf-8")
    
    for json_file in json_files:
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
        
        subject = data.get("subject", "")
        subject_slug = data.get("slug", "")
        subject_desc = data.get("description", "")
        chapters = data.get("chapters", [])
        
        print(f"\n📄 Processing: {subject} ({subject_slug})")
        
        # Generate Subject Home
        chapters_html = ""
        for i, ch in enumerate(chapters, 1):
            ch_title = ch.get("chapter_title", "")
            ch_slug = ch.get("chapter_slug", "")
            ch_desc = ch.get("description", "")
            ch_icon = ch.get("icon", "📝")
            chapters_html += f'<a class="card" href="{subject_slug}/{ch_slug}/index.html"><span class="icon">{ch_icon}</span><span><span class="name">{ch_title}</span><span class="desc">{ch_desc}</span></span><span class="arrow">›</span></a>'
        
        home_page = home_tpl.replace("{{SUBJECT_NAME}}", subject)
        home_page = home_page.replace("{{SUBJECT_DESCRIPTION}}", subject_desc)
        home_page = home_page.replace("{{CHAPTERS_HTML}}", chapters_html)
        
        subject_dir = output_base / subject_slug
        subject_dir.mkdir(parents=True, exist_ok=True)
        (subject_dir / "index.html").write_text(home_page, encoding="utf-8")
        print(f"✅ {subject_slug}/index.html")
        
        # Generate Chapter pages
        for ch in chapters:
            ch_title = ch.get("chapter_title", "")
            ch_slug = ch.get("chapter_slug", "")
            ch_desc = ch.get("description", "")
            quizzes = ch.get("quizzes", [])
            
            quizzes_html = ""
            for i, qz in enumerate(quizzes, 1):
                qz_title = qz.get("quiz_title", "")
                qz_slug = qz.get("quiz_slug", "")
                qz_count = len(qz.get("questions", []))
                quizzes_html += f'<a class="quiz-card" href="{ch_slug}/{qz_slug}/index.html"><span class="qnum">{i:02d}</span><span class="qinfo"><h3>{qz_title}</h3><p>{qz_count} प्रश्न</p></span><span class="arrow">›</span></a>'
            
            chapter_page = chapter_tpl.replace("{{SUBJECT_NAME}}", subject)
            chapter_page = chapter_page.replace("{{SUBJECT_URL}}", f"/Quiz/{subject_slug}/index.html")
            chapter_page = chapter_page.replace("{{CHAPTER_NAME}}", ch_title)
            chapter_page = chapter_page.replace("{{CHAPTER_DESCRIPTION}}", ch_desc)
            chapter_page = chapter_page.replace("{{QUIZZES_HTML}}", quizzes_html)
            
            chapter_dir = subject_dir / ch_slug
            chapter_dir.mkdir(parents=True, exist_ok=True)
            (chapter_dir / "index.html").write_text(chapter_page, encoding="utf-8")
            print(f"✅ {subject_slug}/{ch_slug}/index.html")
            
            # Generate Quiz pages
            for qz in quizzes:
                qz_title = qz.get("quiz_title", "")
                qz_slug = qz.get("quiz_slug", "")
                questions = qz.get("questions", [])
                
                quiz_data_json = json.dumps(questions, ensure_ascii=False)
                
                quiz_page = quiz_tpl.replace("{{QUIZ_TITLE}}", qz_title)
                quiz_page = quiz_page.replace("{{QUIZ_DESCRIPTION}}", qz.get("description", qz_title))
                quiz_page = quiz_page.replace("{{SUBJECT_NAME}}", subject)
                quiz_page = quiz_page.replace("{{SUBJECT_URL}}", f"/Quiz/{subject_slug}/index.html")
                quiz_page = quiz_page.replace("{{CHAPTER_NAME}}", ch_title)
                quiz_page = quiz_page.replace("{{CHAPTER_URL}}", f"/Quiz/{subject_slug}/{ch_slug}/index.html")
                quiz_page = quiz_page.replace("{{TOTAL_QUESTIONS}}", str(len(questions)))
                quiz_page = quiz_page.replace("{{QUIZ_DATA_JSON}}", quiz_data_json)
                
                quiz_dir = chapter_dir / qz_slug
                quiz_dir.mkdir(parents=True, exist_ok=True)
                (quiz_dir / "index.html").write_text(quiz_page, encoding="utf-8")
                print(f"✅ {subject_slug}/{ch_slug}/{qz_slug}/index.html ({len(questions)} questions)")
    
    print("\n🎯 Quiz generation complete!")

if __name__ == "__main__":
    generate_quiz_pages()
