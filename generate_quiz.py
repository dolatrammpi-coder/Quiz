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
    
    # Collect all quiz JSON files (not explanations, not overview)
    quiz_files = [f for f in content_dir.glob("*.json") if not f.name.endswith("-explanations.json")]
    
    if not quiz_files:
        print("❌ No quiz JSON files found")
        return
    
    for quiz_file in sorted(quiz_files):
        with open(quiz_file, encoding="utf-8") as f:
            data = json.load(f)
        
        subject = data.get("subject", "")
        chapter_title = data.get("chapter_title", "")
        quiz_title = data.get("quiz_title", "")
        slug = data.get("slug", quiz_file.stem)
        description = data.get("description", "")
        questions = data.get("questions", [])
        
        # Subject slug from full slug (first part)
        parts = slug.split("-")
        subject_slug = data.get("subject_slug", parts[0] if parts else subject.lower())
        chapter_slug = data.get("chapter_slug", parts[1] if len(parts) > 1 else "chapter")
        quiz_slug = data.get("quiz_slug", parts[2] if len(parts) > 2 else "quiz")
        
        print(f"\n📄 Processing: {quiz_title} ({slug})")
        
        # Read explanations file if exists
        explanations = {}
        expl_file = content_dir / f"{quiz_file.stem}-explanations.json"
        if expl_file.exists():
            with open(expl_file, encoding="utf-8") as f:
                explanations = json.load(f)
        
        # Merge explanations
        for q in questions:
            qid = str(q.get("id", ""))
            if qid in explanations:
                q["explanation"] = explanations[qid]
            elif "explanation" not in q:
                q["explanation"] = ""
        
        # Read overview file if exists
        overview_html = ""
        overview_file = content_dir / f"{quiz_file.stem}-overview.txt"
        if overview_file.exists():
            overview_text = overview_file.read_text(encoding="utf-8")
            paragraphs = overview_text.strip().split("\n\n")
            overview_html = "".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())
        else:
            overview_html = f"<p>{description}</p>"
        
        # Generate Subject Home (if not exists)
        subject_out = output_base / subject_slug
        subject_out.mkdir(parents=True, exist_ok=True)
        subject_home = subject_out / "index.html"
        
        chapter_card = f'<section class="chapter-card"><div class="chapter-head"><div><div class="chapter-title">{chapter_title}</div><div class="chapter-desc">{description}</div></div></div><div class="topic-list"><a class="topic" href="{subject_slug}/{chapter_slug}/index.html"><span class="topic-left"><span class="topic-name">Start Quiz<span class="topic-note">क्विज़ शुरू करें</span></span></span><span class="arrow">›</span></a></div></section>'
        if subject_home.exists():
            existing = subject_home.read_text(encoding="utf-8")
            if f'href="{subject_slug}/{chapter_slug}/index.html"' not in existing:
                if '<div class="grid">' in existing:
                    existing = existing.replace('<div class="grid">', f'<div class="grid">{chapter_card}', 1)
                else:
                    existing = existing.replace('</main>', f'{chapter_card}</main>')
                subject_home.write_text(existing, encoding="utf-8")
                print(f"✅ {subject_slug}/index.html (updated)")
            else:
                print(f"⏭️ {subject_slug}/index.html (already exists)")
        else:
            home_page = home_tpl.replace("{{SUBJECT_NAME}}", subject)
            home_page = home_page.replace("{{SUBJECT_DESCRIPTION}}", description)
            home_page = home_page.replace("{{CHAPTERS_HTML}}", chapter_card)
            subject_home.write_text(home_page, encoding="utf-8")
            print(f"✅ {subject_slug}/index.html (created)")
        
        # Generate Chapter page
        chapter_out = subject_out / chapter_slug
        chapter_out.mkdir(parents=True, exist_ok=True)
        chapter_home = chapter_out / "index.html"
        
        chapter_page = chapter_tpl.replace("{{SUBJECT_NAME}}", subject)
        chapter_page = chapter_page.replace("{{SUBJECT_URL}}", f"/Quiz/{subject_slug}/index.html")
        chapter_page = chapter_page.replace("{{CHAPTER_NAME}}", chapter_title)
        chapter_page = chapter_page.replace("{{CHAPTER_DESCRIPTION}}", description)
        chapter_page = chapter_page.replace("{{QUIZZES_HTML}}", f'<a class="quiz-card" href="{quiz_slug}/index.html"><span class="qnum">01</span><span class="qinfo"><h3>{quiz_title}</h3><p>{len(questions)} प्रश्न</p></span><span class="arrow">›</span></a>')
        chapter_home.write_text(chapter_page, encoding="utf-8")
        print(f"✅ {subject_slug}/{chapter_slug}/index.html")
        
        # Generate Quiz page
        # Normalize question format
        for q in questions:
            if 'question' in q and 'q' not in q:
                q['q'] = q.pop('question')
            if 'answer' in q and 'correct' not in q:
                ans = q.pop('answer')
                opts = q.get('options', [])
                if isinstance(ans, int):
                    q['correct'] = ans
                elif ans in opts:
                    q['correct'] = opts.index(ans)
                else:
                    q['correct'] = 0
        
        quiz_data_json = json.dumps(questions, ensure_ascii=False)
        
        quiz_page = quiz_tpl.replace("{{ base_url }}", "/Quiz/")
        quiz_page = quiz_page.replace("{{ title }}", quiz_title)
        quiz_page = quiz_page.replace("{{ description }}", description)
        quiz_page = quiz_page.replace("{{ subject }}", subject)
        quiz_page = quiz_page.replace("{{ subject_folder }}", subject_slug)
        quiz_page = quiz_page.replace("{{ questions_json }}", quiz_data_json)
        quiz_page = quiz_page.replace("{{ seo_content }}", overview_html)
        
        quiz_out = chapter_out / quiz_slug
        quiz_out.mkdir(parents=True, exist_ok=True)
        (quiz_out / "index.html").write_text(quiz_page, encoding="utf-8")
        print(f"✅ {subject_slug}/{chapter_slug}/{quiz_slug}/index.html ({len(questions)} questions)")
    
    print("\n🎯 Quiz generation complete!")

if __name__ == "__main__":
    generate_quiz_pages()
