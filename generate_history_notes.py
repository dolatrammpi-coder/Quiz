import json
from pathlib import Path

def generate_pages():
    notes_dir = Path("content/notes")
    template_path = Path("templates/topic-notes.html")
    output_base = Path("docs/subject-wise-notes/history")
    
    # Read all JSON files in content/notes/ (except backup files)
    json_files = [f for f in notes_dir.glob("*.json") if not f.name.endswith(".backup")]
    
    if not json_files:
        print("❌ No JSON files found in content/notes/")
        return
    
    with open(template_path, encoding="utf-8") as f:
        template = f.read()
    
    total_pages = 0
    
    for json_file in json_files:
        print(f"\n📄 Processing: {json_file.name}")
        
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
        
        # Handle different JSON formats
        if "chapters" in data or "groups" in data:
            # Full history.json format (multiple chapters)
            groups = data.get("groups", [])
            for group in groups:
                for chapter in group.get("chapters", []):
                    slug = chapter.get("slug", "")
                    title = chapter.get("title", "")
                    description = chapter.get("description", "")
                    questions = chapter.get("questions", [])
                    
                    if not slug:
                        continue
                    
                    if len(questions) > 0:
                        generate_page(slug, title, description, questions, template, output_base)
                        total_pages += 1
                    else:
                        print(f"⏭️ {slug} (0 questions) - Skipped")
        else:
            # Standalone chapter format (single chapter)
            slug = data.get("chapter_slug", data.get("slug", ""))
            title = data.get("chapter_title", data.get("title", ""))
            description = data.get("description", "")
            questions = data.get("questions", [])
            
            if slug and len(questions) > 0:
                generate_page(slug, title, description, questions, template, output_base)
                total_pages += 1
            elif slug:
                print(f"⏭️ {slug} (0 questions) - Skipped")
    
    # Regenerate History index page with all chapters
    if Path("content/notes/history.json").exists():
        with open("content/notes/history.json", encoding="utf-8") as f:
            history_data = json.load(f)
        
        chapters_html = ""
        for group in history_data.get("groups", []):
            group_title = group.get("title", "")
            group_desc = group.get("description", "")
            ch_html = ""
            for i, chapter in enumerate(group.get("chapters", []), 1):
                slug = chapter.get("slug", "")
                title = chapter.get("title", "")
                desc = chapter.get("description", "")
                ch_html += f'<a class="topic" href="subject-wise-notes/history/{slug}/index.html"><span class="topic-left"><span class="topic-num">{i:02d}</span><span class="topic-name">{title}<span class="topic-note">{desc}</span></span></span><span class="arrow">›</span></a>'
            chapters_html += f'<section class="chapter-card"><div class="chapter-head"><div><div class="chapter-title">{group_title}</div><div class="chapter-desc">{group_desc}</div></div></div><div class="topic-list">{ch_html}</div></section>\n'
        
        index_path = Path("docs/subject-wise-notes/history/index.html")
        if index_path.exists():
            import re
            index_content = index_path.read_text(encoding="utf-8")
            old_sections = re.findall(r'<section class="chapter-card">.*?</section>', index_content, flags=re.DOTALL)
            for section in old_sections:
                index_content = index_content.replace(section, "")
            index_content = index_content.replace('<div class="ad-slot" aria-label="Advertisement">Advertisement</div>', chapters_html + '<div class="ad-slot" aria-label="Advertisement">Advertisement</div>', 1)
            index_path.write_text(index_content, encoding="utf-8")
            print("\n📄 History index regenerated")
    
    print(f"\n🎯 Total pages generated: {total_pages}")

def generate_page(slug, title, description, questions, template, output_base):
    # Generate Q&A HTML
    qa_html = ""
    for q in questions:
        question = q.get("question", "")
        answer = q.get("answer", "")
        qa_html += f'<div class="qa-row"><div class="qa-cell qa-q">{question}</div><div class="qa-cell qa-a"><div class="answer"><div class="cover">उत्तर देखें</div><div class="answer-text">{answer}</div></div></div></div>\n'
    
    # Replace placeholders
    page = template.replace('{{QUESTIONS_HTML}}', qa_html)
    page = page.replace('{{TOPIC_TITLE}}', title)
    page = page.replace('{{TOPIC_DESCRIPTION}}', description)
    page = page.replace('{{TOPIC_SUBTITLE}}', description)
    page = page.replace('{{SUBJECT_NAME}}', 'History')
    page = page.replace('{{CHAPTER_NAME}}', 'प्राचीन भारत')
    page = page.replace('{{SUBJECT_URL}}', '/Quiz/subject-wise-notes/history/index.html')
    page = page.replace('{{CHAPTER_URL}}', '/Quiz/subject-wise-notes/history/index.html')
    page = page.replace('{{HOME_URL}}', '/Quiz/index.html')
    page = page.replace('{{NOTES_HOME_URL}}', '/Quiz/subject-wise-notes/index.html')
    page = page.replace('{{TEST_SERIES_URL}}', '/Quiz/test-series/index.html')
    page = page.replace('{{ABOUT_URL}}', '/Quiz/about/index.html')
    page = page.replace('{{PRIVACY_URL}}', '/Quiz/privacy-policy/index.html')
    page = page.replace('{{DISCLAIMER_URL}}', '/Quiz/disclaimer/index.html')
    page = page.replace('{{CONTACT_URL}}', '/Quiz/contact/index.html')
    page = page.replace('{{TERMS_URL}}', '/Quiz/terms-and-conditions/index.html')
    page = page.replace('{{QUESTION_COUNT}}', str(len(questions)))
    page = page.replace('{{REVISION_TITLE}}', 'Revision Notes')
    page = page.replace('{{REVISION_DESCRIPTION}}', f'{title} से जुड़े महत्वपूर्ण तथ्यों का Revision करें।')
    page = page.replace('{{FAQ_TITLE}}', 'FAQ')
    page = page.replace('{{FAQ_QUESTION}}', f'{title} क्यों महत्वपूर्ण है?')
    page = page.replace('{{FAQ_ANSWER}}', f'{title} प्रतियोगी परीक्षाओं के लिए महत्वपूर्ण विषय है।')
    
    # Save page
    chapter_dir = output_base / slug
    chapter_dir.mkdir(parents=True, exist_ok=True)
    page_file = chapter_dir / "index.html"
    page_file.write_text(page, encoding="utf-8")
    
    print(f"✅ {slug} ({len(questions)} questions)")

if __name__ == "__main__":
    generate_pages()
