#!/usr/bin/env python3

from pathlib import Path
import json
import html
import re


ROOT = Path(__file__).resolve().parent.parent

SOURCE = ROOT / "content" / "notes"
OUTPUT = ROOT / "docs" / "subject-wise-notes"
TEMPLATES = ROOT / "templates"

SUBJECT_TEMPLATE = TEMPLATES / "subject-page.html"
CHAPTER_NOTES_TEMPLATE = TEMPLATES / "topic-notes.html"


# ============================================================
# BASIC HELPERS
# ============================================================

def slugify(value):
    value = str(value or "").strip().lower()
    value = re.sub(
        r"[^\w\s-]",
        "",
        value,
        flags=re.UNICODE
    )
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value)
    value = value.strip("-")

    return value or "untitled"


def esc(value):
    return html.escape(
        str(value or ""),
        quote=True
    )


def load_json(path):
    with path.open(
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def write_text(path, text):
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_text(
        text,
        encoding="utf-8"
    )


def embed_json(script_id, data):
    payload = json.dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":")
    )

    payload = payload.replace(
        "</",
        "<\\/"
    )

    return (
        f'<script type="application/json" '
        f'id="{script_id}">{payload}</script>'
    )


def replace_tokens(template, values):
    for key, value in values.items():
        template = template.replace(
            "{{" + key + "}}",
            str(value)
        )

    return template


# ============================================================
# DATA STRUCTURE
# ============================================================

def direct_chapters(data):
    """
    Chapters directly belonging to the subject.

    Example:

    {
        "subject": "Polity",
        "chapters": [
            {...},
            {...}
        ]
    }
    """

    chapters = data.get("chapters") or []

    if not isinstance(chapters, list):
        return []

    return [
        chapter
        for chapter in chapters
        if isinstance(chapter, dict)
    ]


def groups(data):
    """
    Optional groups.

    Example:

    {
        "subject": "History",
        "groups": [
            {
                "title": "Modern History",
                "chapters": [
                    {...},
                    {...}
                ]
            }
        ]
    }

    IMPORTANT:

    Group is ONLY a visual heading.

    It is NOT clickable.
    It does NOT create a URL.
    It does NOT create a separate page.

    Only its chapters create pages.
    """

    result = []

    raw_groups = data.get("groups") or []

    if not isinstance(raw_groups, list):
        return result

    for group in raw_groups:

        if not isinstance(group, dict):
            continue

        raw_chapters = group.get("chapters") or []

        if not isinstance(raw_chapters, list):
            raw_chapters = []

        chapters = [
            chapter
            for chapter in raw_chapters
            if isinstance(chapter, dict)
        ]

        result.append(
            (
                group,
                chapters
            )
        )

    return result


def all_chapters(data):
    """
    Return every real Chapter.

    Direct chapters +
    grouped chapters.

    Groups themselves are NOT chapters.
    """

    result = []

    result.extend(
        direct_chapters(data)
    )

    for _, chapter_list in groups(data):

        result.extend(
            chapter_list
        )

    return result


# ============================================================
# CHAPTER CARD
# ============================================================

def chapter_link_card(
    chapter,
    number=1
):
    """
    Creates one clickable Chapter card.

    This is the visual list item:

    01   1857 का विद्रोह                  >

         One Liner Revision Notes
    """

    title = (
        chapter.get("title")
        or chapter.get("name")
        or "Chapter"
    )

    slug = (
        chapter.get("slug")
        or slugify(title)
    )

    description = (
        chapter.get("description")
        or chapter.get("subtitle")
        or "One Liner Revision Notes"
    )

    return (
        '<a class="topic" '
        f'href="{esc(slug)}/index.html">'

        '<span class="topic-left">'

        f'<span class="topic-num">'
        f'{number:02d}'
        f'</span>'

        '<span class="topic-name">'

        f'{esc(title)}'

        '<span class="topic-note">'
        f'{esc(description)}'
        '</span>'

        '</span>'

        '</span>'

        '<span class="arrow">›</span>'

        '</a>'
    )


# ============================================================
# SUBJECT PAGE
# ============================================================

def render_subject(data):

    if not SUBJECT_TEMPLATE.exists():
        raise FileNotFoundError(
            f"Missing template: {SUBJECT_TEMPLATE}"
        )

    subject = data["subject"]

    description = (
        data.get("description")
        or
        f"{subject} के विषयवार One Liner Revision Notes।"
    )

    blocks = []

    # --------------------------------------------------------
    # GROUPED SUBJECTS
    # --------------------------------------------------------
    #
    # Example:
    #
    # History
    #
    # इतिहास के अध्याय
    #
    # 🇮🇳 Modern History
    #
    # 01  1857 का विद्रोह
    # 02  भारतीय राष्ट्रीय कांग्रेस
    # 03  गांधी युग
    #
    # Modern History is NOT clickable.
    #
    # --------------------------------------------------------

    grouped = groups(data)

    for group, chapters in grouped:

        group_title = (
            group.get("title")
            or group.get("name")
            or "Group"
        )

        group_description = (
            group.get("description")
            or ""
        )

        # Group heading.
        #
        # IMPORTANT:
        # This is NOT an <a>.
        # Therefore the group itself is not clickable.

        group_description_html = ""

        if group_description:
            group_description_html = (
                '<div class="chapter-desc">'
                f'{esc(group_description)}'
                '</div>'
            )

        chapter_items = []

        for index, chapter in enumerate(
            chapters,
            start=1
        ):
            chapter_items.append(
                chapter_link_card(
                    chapter,
                    index
                )
            )

        topics_html = "\n".join(
            chapter_items
        )

        if topics_html:

            blocks.append(
                '<section class="chapter-card">'

                '<div class="chapter-head">'
                '<div>'

                f'<div class="chapter-title">'
                f'{esc(group.get("icon") or "🇮🇳")} '
                f'{esc(group_title)}'
                f'</div>'

                f'{group_description_html}'

                '</div>'
                '</div>'

                '<div class="topic-list">'
                f'{topics_html}'
                '</div>'

                '</section>'
            )

        else:

            blocks.append(
                '<section class="chapter-card">'

                '<div class="chapter-head">'
                '<div>'

                f'<div class="chapter-title">'
                f'{esc(group.get("icon") or "📚")} '
                f'{esc(group_title)}'
                f'</div>'

                f'{group_description_html}'

                '</div>'
                '</div>'

                '<div class="topic-list">'

                '<div class="no-results" '
                'style="display:block">'
                'इस Group में अभी कोई Chapter '
                'उपलब्ध नहीं है।'
                '</div>'

                '</div>'

                '</section>'
            )


    # --------------------------------------------------------
    # DIRECT / UNGROUPED CHAPTERS
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # subject-page.html already contains:
    #
    # {{CHAPTER_SECTION_TITLE}}
    #
    # इसलिए यहाँ दोबारा
    # "Polity के Chapters"
    # या
    # "History के Chapters"
    # generate नहीं करेंगे।
    #
    # इससे duplicate heading नहीं आएगी.
    #
    # --------------------------------------------------------

    direct = direct_chapters(data)

    if direct:

        direct_items = []

        for index, chapter in enumerate(
            direct,
            start=1
        ):
            direct_items.append(
                chapter_link_card(
                    chapter,
                    index
                )
            )

        if grouped:

            # Grouped + direct chapters:
            # direct chapters get their own small section.
            #
            # Main section heading is still controlled
            # by subject-page.html.

            blocks.append(
                '<section class="chapter-card">'

                '<div class="chapter-head">'
                '<div>'

                '<div class="chapter-title">'
                '📚 Chapters'
                '</div>'

                '</div>'
                '</div>'

                '<div class="topic-list">'
                +
                "\n".join(direct_items)
                +
                '</div>'

                '</section>'
            )

        else:

            # Completely ungrouped subject.
            #
            # Do NOT add another heading.
            # Just show numbered Chapter cards.

            blocks.extend(
                direct_items
            )


    chapters_html = "\n".join(
        blocks
    )

    if not chapters_html:

        chapters_html = (
            '<div class="no-results" '
            'style="display:block">'
            'अभी कोई Chapter उपलब्ध नहीं है।'
            '</div>'
        )


    # --------------------------------------------------------
    # SUBJECT TEMPLATE TOKENS
    # --------------------------------------------------------

    values = {

        "SUBJECT_TITLE_EN":
            subject,

        "SUBJECT_TITLE_HI":
            subject,

        "SUBJECT_NAME":
            subject,

        "SUBJECT_DESCRIPTION":
            description,

        "SUBJECT_ICON":
            data.get("icon")
            or "📚",

        # IMPORTANT:
        #
        # This heading is generated ONLY by
        # subject-page.html.
        #
        # Builder does NOT generate it again.

        "CHAPTER_SECTION_TITLE":
            data.get("chapter_section_title")
            or (
                "इतिहास के अध्याय"
                if subject == "History"
                else f"{subject} के Chapters"
            ),

        "CHAPTERS_HTML":
            chapters_html,

        "INFO_TITLE":
            data.get("info_title")
            or f"{subject} Notes कैसे उपयोग करें?",

        "INFO_DESCRIPTION":
            data.get("info_description")
            or
            (
                f"{subject} के उपलब्ध Chapters "
                "चुनकर उनके Chapter Notes पढ़ें।"
            ),

        "HOME_URL":
            "../../index.html",

        "NOTES_HOME_URL":
            "../index.html",

        "TEST_SERIES_URL":
            "../../test-series/index.html",

        "ABOUT_URL":
            "../../about/index.html",

        "PRIVACY_URL":
            "../../privacy-policy/index.html",

        "DISCLAIMER_URL":
            "../../disclaimer/index.html",

        "CONTACT_URL":
            "../../contact/index.html",

        "TERMS_URL":
            "../../terms-and-conditions/index.html",
    }


    template = SUBJECT_TEMPLATE.read_text(
        encoding="utf-8"
    )

    result = replace_tokens(
        template,
        values
    )

    return result.replace(
        "</head>",
        embed_json(
            "notes-meta",
            data
        )
        +
        "\n</head>",
        1
    )


# ============================================================
# QUESTIONS
# ============================================================

def question_rows(topic):

    questions = (
        topic.get("questions")
        or []
    )

    if not isinstance(
        questions,
        list
    ):
        return "", 0

    rows = []

    for item in questions:

        if not isinstance(
            item,
            dict
        ):
            continue

        question = (
            item.get("question")
            or item.get("q")
            or ""
        )

        answer = (
            item.get("answer")
            or item.get("answer_text")
            or item.get("a")
            or ""
        )

        rows.append(

            '<div class="qa-row">'

            f'<div class="qa-cell qa-q">'
            f'{esc(question)}'
            f'</div>'

            '<div class="qa-cell qa-a answer">'

            f'<span class="answer-text">'
            f'{esc(answer)}'
            f'</span>'

            '<span class="cover">'
            'उत्तर देखें'
            '</span>'

            '</div>'

            '</div>'
        )


    return (
        "\n".join(rows),
        len(rows)
    )


# ============================================================
# CHAPTER NOTES PAGE
# ============================================================

def render_chapter_notes(
    chapter,
    subject
):

    if not CHAPTER_NOTES_TEMPLATE.exists():
        raise FileNotFoundError(
            f"Missing template: "
            f"{CHAPTER_NOTES_TEMPLATE}"
        )


    title = (
        chapter.get("title")
        or chapter.get("name")
        or "Chapter"
    )

    description = (
        chapter.get("description")
        or
        f"{title} से जुड़े महत्वपूर्ण "
        "One Liner Questions और Answers।"
    )

    subtitle = (
        chapter.get("subtitle")
        or
        "One Liner Revision Notes — "
        "महत्वपूर्ण प्रश्न और उत्तर।"
    )


    questions_html, question_count = (
        question_rows(chapter)
    )


    if not questions_html:

        questions_html = (

            '<div class="qa-row">'

            '<div class="qa-cell qa-q">'
            'इस Chapter का content अभी '
            'उपलब्ध नहीं है।'
            '</div>'

            '<div class="qa-cell qa-a answer">'

            '<span class="answer-text">'
            '—'
            '</span>'

            '<span class="cover">'
            'उत्तर देखें'
            '</span>'

            '</div>'

            '</div>'
        )


    revision = (
        chapter.get("revision")
        or {}
    )

    faq = (
        chapter.get("faq")
        or {}
    )


    values = {

        "TOPIC_TITLE":
            title,

        "TOPIC_DESCRIPTION":
            description,

        "TOPIC_SUBTITLE":
            subtitle,

        "SUBJECT_NAME":
            subject,

        "CHAPTER_NAME":
            title,

        "QUESTION_COUNT":
            question_count,

        "QUESTIONS_HTML":
            questions_html,

        "REVISION_TITLE":
            (
                revision.get("title")
                or
                chapter.get("revision_title")
                or
                f"{title} — त्वरित पुनरावृत्ति"
            ),

        "REVISION_DESCRIPTION":
            (
                revision.get("content")
                or
                chapter.get(
                    "revision_description"
                )
                or
                (
                    f"इस Chapter के One Liner "
                    f"प्रश्नों से {title} के प्रमुख "
                    "तथ्य जल्दी revise किए जा सकते हैं।"
                )
            ),

        "FAQ_TITLE":
            (
                faq.get("title")
                or
                "अक्सर पूछे जाने वाले प्रश्न"
            ),

        "FAQ_QUESTION":
            (
                faq.get("question")
                or
                chapter.get("faq_question")
                or
                "क्या इन नोट्स का अभ्यास किया जा सकता है?"
            ),

        "FAQ_ANSWER":
            (
                faq.get("answer")
                or
                chapter.get("faq_answer")
                or
                (
                    "हाँ। Practice Mode चुनकर "
                    "उत्तर छिपाएँ और प्रत्येक answer "
                    "पर tap/click करके उसे reveal करें।"
                )
            ),

        # ----------------------------------------------------
        # CHAPTER NOTES URL
        #
        # /docs/subject-wise-notes/history/
        #     revolt-of-1857/
        #         index.html
        # ----------------------------------------------------

        "HOME_URL":
            "../../../index.html",

        "NOTES_HOME_URL":
            "../../index.html",

        "SUBJECT_URL":
            "../index.html",

        "CHAPTER_URL":
            "#",

        "TEST_SERIES_URL":
            "../../../test-series/index.html",

        "ABOUT_URL":
            "../../../about/index.html",

        "PRIVACY_URL":
            "../../../privacy-policy/index.html",

        "DISCLAIMER_URL":
            "../../../disclaimer/index.html",

        "CONTACT_URL":
            "../../../contact/index.html",

        "TERMS_URL":
            "../../../terms-and-conditions/index.html",
    }


    template = CHAPTER_NOTES_TEMPLATE.read_text(
        encoding="utf-8"
    )


    result = replace_tokens(
        template,
        values
    )


    return result.replace(
        "</head>",
        embed_json(
            "chapter-meta",
            chapter
        )
        +
        "\n</head>",
        1
    )


# ============================================================
# BUILD ONE SUBJECT
# ============================================================

def build_subject(source_file):

    data = load_json(
        source_file
    )


    if not isinstance(
        data,
        dict
    ):
        raise ValueError(
            "JSON root must be an object"
        )


    subject = (
        data.get("subject")
        or
        data.get("name")
    )


    if not subject:

        raise ValueError(
            f"{source_file}: "
            "subject/name is required"
        )


    data["subject"] = subject

    data["slug"] = (
        data.get("slug")
        or
        slugify(subject)
    )


    subject_dir = (
        OUTPUT
        /
        data["slug"]
    )


    # --------------------------------------------------------
    # CLEAN OLD GENERATED OUTPUT FOR THIS SUBJECT
    # --------------------------------------------------------
    #
    # Important:
    # Only this subject's generated directory is removed.
    # Other subjects remain untouched.
    #
    # This prevents stale Chapter pages from remaining after
    # a Chapter is renamed or deleted from the source JSON.
    #
    # --------------------------------------------------------

    if subject_dir.exists():

        import shutil

        shutil.rmtree(
            subject_dir
        )


    # --------------------------------------------------------
    # SUBJECT PAGE
    # --------------------------------------------------------
    #
    # Example:
    #
    # docs/subject-wise-notes/history/index.html
    #
    # docs/subject-wise-notes/polity/index.html
    #
    # --------------------------------------------------------

    write_text(
        subject_dir / "index.html",
        render_subject(data)
    )


    # --------------------------------------------------------
    # CHAPTER PAGES
    # --------------------------------------------------------
    #
    # BOTH direct and grouped chapters use:
    #
    # /subject/chapter/index.html
    #
    # IMPORTANT:
    #
    # Group itself NEVER gets a page.
    #
    # --------------------------------------------------------

    for chapter in all_chapters(data):

        chapter_title = (
            chapter.get("title")
            or
            chapter.get("name")
            or
            "Chapter"
        )


        chapter_slug = (
            chapter.get("slug")
            or
            slugify(chapter_title)
        )


        chapter["slug"] = (
            chapter_slug
        )


        chapter_dir = (
            subject_dir
            /
            chapter_slug
        )


        write_text(
            chapter_dir / "index.html",
            render_chapter_notes(
                chapter,
                subject
            )
        )


# ============================================================
# BUILD ALL
# ============================================================

def build():

    if not SOURCE.exists():

        print(
            f"Notes source directory not found: "
            f"{SOURCE}"
        )

        print(
            "Existing generated Notes HTML is untouched."
        )

        return


    files = sorted(
        SOURCE.rglob("*.json")
    )


    if not files:

        print(
            "No Notes JSON files found."
        )

        print(
            "Existing generated Notes HTML is untouched."
        )

        return


    success = 0


    for source_file in files:

        try:

            build_subject(
                source_file
            )

            success += 1

            print(
                f"OK: {source_file}"
            )

        except Exception as exc:

            print(
                f"ERROR: "
                f"{source_file}: {exc}"
            )


    print()

    print(
        f"Built {success}/{len(files)} "
        "Notes source files."
    )

    print(
        "Missing JSON never deletes generated Notes pages."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    build()
