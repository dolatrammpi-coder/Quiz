import json
from pathlib import Path

def generate_quiz_pages():
    content_dir = Path("content/quiz")
    template_home = Path("templates/quiz-subject-home.html")
    template_chapter = Path("templates/quiz-chapter.html")
    template_quiz = Path("templates/quiz.html")
    output_base = Path("docs")
    
    if not content_dir.exists():
        print("❌ content/quiz folder nahi hai")
        return
    
    home_tpl = template_home.read_text(encoding="utf-8")
    chapter_tpl = template_chapter.read_text(encoding="utf-8")
    quiz_tpl = template_quiz.read_text(encoding="utf-8")
    
    # Process each subject folder
    for subject_dir in sorted(content_dir.iterdir()):
        if not subject_dir.is_dir():
            continue
        
        # Check if subject has index.json (subject metadata)
        subject_json = subject_dir / "subject.json"
        if not subject_json.exists():
            continue
        
        with open(subject_json, encoding="utf-8") as f:
            subject_data = json.load(f)
        
        subject = subject_data.get("subject", subject_dir.name)
        subject_slug = subject_dir.name
        subject_desc = subject_data.get("description", "")
        
        print(f"\n📄 Processing: {subject} ({subject_slug})")
        
        # Collect chapters
        chapters = []
        for chapter_dir in sorted(subject_dir.iterdir()):
            if chapter_dir.is_dir() and (chapter_dir / "chapter.json").exists():
                with open(chapter_dir / "chapter.json", encoding="utf-8") as f:
                    chapter_data = json.load(f)
                chapters.append((chapter_dir, chapter_data))
        
        # Generate Subject Home
        chapters_html = ""
        for i, (ch_dir, ch_data) in enumerate(chapters, 1):
            ch_title = ch_data.get("chapter_title", ch_dir.name)
            ch_slug = ch_dir.name
            ch_desc = ch_data.get("description", "")
            ch_icon = ch_data.get("icon", "📝")
            chapters_html += f'<a class="card" href="{subject_slug}/{ch_slug}/index.html"><span class="icon">{ch_icon}</span><span><span class="name">{ch_title}</span><span class="desc">{ch_desc}</span></span><span class="arrow">›</span></a>'
        
        home_page = home_tpl.replace("{{SUBJECT_NAME}}", subject)
        home_page = home_page.replace("{{SUBJECT_DESCRIPTION}}", subject_desc)
        home_page = home_page.replace("{{CHAPTERS_HTML}}", chapters_html)
        
        subject_out = output_base / subject_slug
        subject_out.mkdir(parents=True, exist_ok=True)
        (subject_out / "index.html").write_text(home_page, encoding="utf-8")
        print(f"✅ {subject_slug}/index.html")
        
        # Generate Chapter pages
        for ch_dir, ch_data in chapters:
            ch_title = ch_data.get("chapter_title", "")
            ch_slug = ch_dir.name
            ch_desc = ch_data.get("description", "")
            
            # Collect quizzes
            quizzes = []
            for quiz_dir in sorted(ch_dir.iterdir()):
                if quiz_dir.is_dir() and (quiz_dir / "quiz.json").exists():
                    with open(quiz_dir / "quiz.json", encoding="utf-8") as f:
                        quiz_data = json.load(f)
                    quizzes.append((quiz_dir, quiz_data))
            
            quizzes_html = ""
            for i, (qz_dir, qz_data) in enumerate(quizzes, 1):
                qz_title = qz_data.get("quiz_title", qz_dir.name)
                qz_slug = qz_dir.name
                qz_count = qz_data.get("question_count", 0)
                quizzes_html += f'<a class="quiz-card" href="{ch_slug}/{qz_slug}/index.html"><span class="qnum">{i:02d}</span><span class="qinfo"><h3>{qz_title}</h3><p>{qz_count} प्रश्न</p></span><span class="arrow">›</span></a>'
            
            chapter_page = chapter_tpl.replace("{{SUBJECT_NAME}}", subject)
            chapter_page = chapter_page.replace("{{SUBJECT_URL}}", f"/Quiz/{subject_slug}/index.html")
            chapter_page = chapter_page.replace("{{CHAPTER_NAME}}", ch_title)
            chapter_page = chapter_page.replace("{{CHAPTER_DESCRIPTION}}", ch_desc)
            chapter_page = chapter_page.replace("{{QUIZZES_HTML}}", quizzes_html)
            
            chapter_out = subject_out / ch_slug
            chapter_out.mkdir(parents=True, exist_ok=True)
            (chapter_out / "index.html").write_text(chapter_page, encoding="utf-8")
            print(f"✅ {subject_slug}/{ch_slug}/index.html")
            
            # Generate Quiz pages
            for qz_dir, qz_data in quizzes:
                qz_title = qz_data.get("quiz_title", "")
                qz_slug = qz_dir.name
                
                # Read questions.json
                questions_file = qz_dir / "questions.json"
                if not questions_file.exists():
                    print(f"❌ {qz_slug}: questions.json missing")
                    continue
                
                with open(questions_file, encoding="utf-8") as f:
                    questions = json.load(f)
                
                # Read explanations.json (optional)
                explanations = {}
                expl_file = qz_dir / "explanations.json"
                if expl_file.exists():
                    with open(expl_file, encoding="utf-8") as f:
                        explanations = json.load(f)
                
                # Merge explanations into questions
                for q in questions:
                    qid = str(q.get("id", ""))
                    if qid in explanations:
                        q["explanation"] = explanations[qid]
                    elif "explanation" not in q:
                        q["explanation"] = ""
                
                # Read overview.txt (optional)
                overview_html = ""
                overview_file = qz_dir / "overview.txt"
                if overview_file.exists():
                    overview_text = overview_file.read_text(encoding="utf-8")
                    # Convert simple text to HTML paragraphs
                    paragraphs = overview_text.strip().split("\n\n")
                    overview_html = "".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())
                else:
                    overview_html = f"<p>{qz_data.get('description', qz_title)}</p>"
                
                # Generate quiz page
                quiz_data_json = json.dumps(questions, ensure_ascii=False)
                
                quiz_page = quiz_tpl.replace("{{ base_url }}", "/Quiz/")
                quiz_page = quiz_page.replace("{{ title }}", qz_title)
                quiz_page = quiz_page.replace("{{ description }}", qz_data.get("description", qz_title))
                quiz_page = quiz_page.replace("{{ subject }}", subject)
                quiz_page = quiz_page.replace("{{ subject_folder }}", subject_slug)
                quiz_page = quiz_page.replace("{{ questions_json }}", quiz_data_json)
                quiz_page = quiz_page.replace("{{ seo_content }}", overview_html)
                
                quiz_out = chapter_out / qz_slug
                quiz_out.mkdir(parents=True, exist_ok=True)
                (quiz_out / "index.html").write_text(quiz_page, encoding="utf-8")
                print(f"✅ {subject_slug}/{ch_slug}/{qz_slug}/index.html ({len(questions)} questions)")
    
    print("\n🎯 Quiz generation complete!")

if __name__ == "__main__":
    generate_quiz_pages()
