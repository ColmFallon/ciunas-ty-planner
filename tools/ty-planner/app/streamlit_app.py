#!/usr/bin/env python3
"""Streamlit UI for the deployed TY planning tool."""

from __future__ import annotations

import csv
from datetime import datetime
from io import BytesIO
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
GENERATED_PLANS_DIR = ROOT / "outputs" / "generated_plans"
LEADS_DIR = ROOT / "outputs" / "leads"
SHOW_DOCX_DIAGNOSTIC = False
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from answer_query import answer_question, normalise_template_context, parse_template_context, requested_output_language  # noqa: E402


def split_layer_prefix(text: str) -> tuple[str | None, str]:
    match = re.match(r"^\[(official_guidance|ciunas_framework)\]\s+(.*)$", text.strip())
    if not match:
        return None, text.strip()
    return match.group(1), match.group(2).strip()


def render_source_layer_caption() -> None:
    st.caption(
        "Official guidance informs policy and planning context. "
        "Ciunas framework sources can shape programme and module ideas, but they are not official policy."
    )


def plan_sections_map(full_plan_text: str) -> tuple[str, str, dict[str, list[str]]]:
    title, subtitle, sections = parse_plan_blocks(full_plan_text)
    section_map: dict[str, list[str]] = {}
    for heading, paragraphs in sections:
        if heading.strip():
            section_map[heading.strip().lower()] = paragraphs
    return title, subtitle, section_map


def render_plan_sections(title: str, subtitle: str, sections: list[tuple[str, list[str]]]) -> None:
    if not title and not sections:
        st.write("No TY plan text was returned.")
        return

    if title:
        st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)

    for heading, paragraphs in sections:
        if heading:
            st.markdown(f"#### {heading}")
        for paragraph in paragraphs:
            if paragraph:
                st.write(paragraph)


def render_generated_plan(answer: str) -> None:
    title, subtitle, sections = parse_plan_blocks(answer)
    render_plan_sections(title, subtitle, sections)


def render_plan_preview(answer: str) -> None:
    title, subtitle, section_map = plan_sections_map(answer)
    preview_sections: list[tuple[str, list[str]]] = []
    for heading in ("programme overview", "rationale", "aims"):
        paragraphs = section_map.get(heading)
        if paragraphs:
            preview_sections.append((heading.title() if heading != "aims" else "Aims", paragraphs))
    render_plan_sections(title, subtitle, preview_sections)


def build_download_prompt(user_input: str) -> str:
    if not user_input:
        return "Create a TY plan"

    lowered = user_input.lower()
    if any(term in lowered for term in ("create", "generate", "plan", "ty plan", "annual plan")):
        return user_input
    if any(term in lowered for term in ("irish", "gaeilge", "as gaeilge", "i ngaeilge", "cruthaigh", "idirbhliana")):
        return f"Create a TY plan in Irish focused on {user_input}"
    return f"Create a TY plan focused on {user_input}"


def build_tailored_plan_prompt(
    school_name: str,
    cohort_size: str,
    school_type: str,
    school_ethos: str,
    priorities: str,
    existing_modules: str,
    work_experience: str,
    additional_context: str,
    language: str,
) -> str:
    return (
        "Create a Transition Year annual plan.\n\n"
        "Use the following context:\n"
        f"School name: {school_name or 'Not specified'}\n"
        f"Cohort size: {cohort_size or 'Not specified'}\n"
        f"School type: {school_type or 'Not specified'}\n"
        f"School ethos: {school_ethos or 'Not specified'}\n"
        f"Main priorities: {priorities or 'Not specified'}\n"
        f"Existing modules: {existing_modules or 'Not specified'}\n"
        f"Work experience timing: {work_experience or 'Not specified'}\n"
        f"Additional context: {additional_context or 'Not specified'}\n"
        f"Language: {language or 'English'}\n\n"
        "The plan should:\n"
        "- reflect the school context\n"
        "- use the school name and cohort context naturally where relevant\n"
        "- prioritise the stated focus areas\n"
        "- incorporate existing modules where relevant\n"
        "- structure work experience appropriately\n"
        "- sound realistic for current TY practice in Irish schools\n"
        "- remain practical and usable for a TY coordinator\n\n"
        "Generate a full structured TY annual plan."
    )


def infer_output_language(answer_mode: str, prompt: str) -> str:
    context = parse_template_context(prompt)
    explicit_language = requested_output_language(context.get("language", ""))
    if explicit_language:
        return explicit_language
    lowered_prompt = prompt.lower()
    if answer_mode.endswith("_ga") or any(
        term in lowered_prompt for term in ("irish", "gaeilge", "as gaeilge", "i ngaeilge")
    ):
        return "ga"
    return "en"


def save_generated_plan(answer: str, language: str) -> tuple[Path, Path]:
    GENERATED_PLANS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"ty_annual_plan_{language}_{timestamp}"
    markdown_path = GENERATED_PLANS_DIR / f"{stem}.md"
    text_path = GENERATED_PLANS_DIR / f"{stem}.txt"
    markdown_path.write_text(answer + "\n", encoding="utf-8")
    text_path.write_text(answer + "\n", encoding="utf-8")
    return markdown_path, text_path


def save_export_file(data: bytes, language: str, format_marker: str, suffix: str) -> Path:
    GENERATED_PLANS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = GENERATED_PLANS_DIR / f"ty_annual_plan_{language}_{format_marker}_{timestamp}.{suffix}"
    export_path.write_bytes(data)
    return export_path


def looks_like_email(value: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value.strip()))


def save_lead_row(row: dict[str, str]) -> Path:
    LEADS_DIR.mkdir(parents=True, exist_ok=True)
    leads_path = LEADS_DIR / "ty_planner_leads.csv"
    fieldnames = [
        "timestamp",
        "email",
        "name",
        "mode",
        "language",
        "school_name",
        "school_type",
        "priorities",
    ]
    write_header = not leads_path.exists()
    with leads_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow({field: row.get(field, "") for field in fieldnames})
    return leads_path


def is_generator_result(answer_mode: str) -> bool:
    return answer_mode.startswith("template_generation")


def latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def split_export_paragraph(paragraph: str) -> list[str]:
    cleaned = " ".join(paragraph.split())
    if len(cleaned) < 520:
        return [cleaned]

    sentence_parts = re.split(r"(?<=[.!?])\s+", cleaned)
    sentence_parts = [part.strip() for part in sentence_parts if part.strip()]
    if len(sentence_parts) < 3:
        return [cleaned]

    midpoint = max(1, len(sentence_parts) // 2)
    left = " ".join(sentence_parts[:midpoint]).strip()
    right = " ".join(sentence_parts[midpoint:]).strip()
    if not left or not right:
        return [cleaned]
    return [left, right]


def infer_plan_language(title: str, subtitle: str) -> str:
    combined = f"{title} {subtitle}".lower()
    ga_markers = (
        "idirbhliana",
        "meán fómhair",
        "bealtaine",
        "plean bliantúil",
    )
    return "ga" if any(marker in combined for marker in ga_markers) else "en"


def standardised_export_subtitle(language: str) -> str:
    if language == "ga":
        return "Meán Fómhair 2026 – Bealtaine 2027"
    return "September 2026 – May 2027"


def build_cover_page_text(language: str) -> tuple[str, str, str, str]:
    if language == "ga":
        return (
            "PLEAN BLIANTÚIL",
            "NA hIDIRBHLIANA",
            "Comhordaitheoir TY:",
            "Doiciméad pleanála struchtúrtha do dhearadh, cur i bhfeidhm, agus athbhreithniú chlár na hIdirbhliana.",
        )
    return (
        "TRANSITION YEAR",
        "ANNUAL PLAN",
        "TY Coordinator:",
        "A structured planning document for the design, delivery, and review of the Transition Year programme.",
    )


def build_title_block_values(language: str, context: dict[str, str] | None = None) -> tuple[str, str, bool]:
    _, _, coordinator_label, _ = build_cover_page_text(language)
    context = normalise_template_context(context or {}, language)
    school_name = str(context.get("school_name", "")).strip()
    ty_coordinator = str(context.get("ty_coordinator", "")).strip()

    school_value = school_name if school_name else "______________________"
    coordinator_value = (
        f"{coordinator_label} {ty_coordinator}"
        if ty_coordinator
        else f"{coordinator_label} ______________________"
    )
    return school_value, coordinator_value, bool(school_name)


def needs_fill_lines(heading: str, language: str) -> bool:
    normalised = heading.strip().lower()
    if language == "ga":
        return normalised in {"croí-mhodúil", "féilire achomair", "punann"}
    return normalised in {"core modules", "summary calendar", "portfolio"}


def export_fill_lines() -> list[str]:
    return [
        "____________________________",
        "____________________________",
    ]


def parse_plan_blocks(full_plan_text: str) -> tuple[str, str, list[tuple[str, list[str]]]]:
    lines = [line.rstrip() for line in full_plan_text.splitlines()]
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    if not non_empty_lines:
        return "", "", []

    title = non_empty_lines[0]
    subtitle = non_empty_lines[1] if len(non_empty_lines) > 1 else ""
    remaining_text = full_plan_text
    title_block = f"{title}\n{subtitle}".strip()
    if title_block and remaining_text.startswith(title_block):
        remaining_text = remaining_text[len(title_block) :].lstrip()

    blocks = [block.strip() for block in remaining_text.split("\n\n") if block.strip()]
    sections: list[tuple[str, list[str]]] = []

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) >= 2:
            heading = lines[0]
            body: list[str] = []
            for line in lines[1:]:
                body.extend(split_export_paragraph(line))
        else:
            heading = ""
            body = split_export_paragraph(block)
        sections.append((heading, body))

    return title, subtitle, sections


def build_plan_latex(full_plan_text: str, context: dict[str, str] | None = None) -> str:
    title, subtitle, sections = parse_plan_blocks(full_plan_text)
    language = infer_plan_language(title, subtitle)
    subtitle = standardised_export_subtitle(language)
    title_line_one, title_line_two, _coordinator_label, cover_note = build_cover_page_text(language)
    school_field, coordinator_field, has_school_name = build_title_block_values(language, context)
    section_parts: list[str] = []
    for heading, paragraphs in sections:
        if heading:
            section_parts.append(f"\\section*{{{latex_escape(heading)}}}")
        for paragraph in paragraphs:
            if paragraph:
                section_parts.append(latex_escape(paragraph))
                section_parts.append("")
        if heading and needs_fill_lines(heading, language):
            for fill_line in export_fill_lines():
                section_parts.append(latex_escape(fill_line))
            section_parts.append("")

    body = "\n".join(section_parts).strip()
    escaped_title_line_one = latex_escape(title_line_one)
    escaped_title_line_two = latex_escape(title_line_two)
    escaped_subtitle = latex_escape(subtitle)
    escaped_cover_note = latex_escape(cover_note)
    escaped_school_field = latex_escape(school_field)
    escaped_coordinator_field = latex_escape(coordinator_field)
    school_line = (
        f"{{\\fontsize{{17pt}}{{21pt}}\\selectfont\\bfseries\\sffamily {escaped_school_field}\\par}}\n"
        if has_school_name
        else f"{{\\fontsize{{15pt}}{{19pt}}\\selectfont\\sffamily {escaped_school_field}\\par}}\n"
    )

    return (
        "\\documentclass[11pt]{article}\n"
        "\\usepackage[a4paper,margin=24mm,top=26mm,bottom=26mm]{geometry}\n"
        "\\usepackage{fontspec}\n"
        "\\usepackage{microtype}\n"
        "\\usepackage{titlesec}\n"
        "\\usepackage{setspace}\n"
        "\\usepackage{parskip}\n"
        "\\usepackage{ragged2e}\n"
        "\\usepackage{xcolor}\n"
        "\\usepackage[hidelinks]{hyperref}\n"
        "\\IfFontExistsTF{TeX Gyre Pagella}{\\setmainfont{TeX Gyre Pagella}}{\\IfFontExistsTF{Times New Roman}{\\setmainfont{Times New Roman}}{\\setmainfont{Latin Modern Roman}}}\n"
        "\\IfFontExistsTF{TeX Gyre Heros}{\\setsansfont{TeX Gyre Heros}}{\\IfFontExistsTF{Helvetica Neue}{\\setsansfont{Helvetica Neue}}{\\setsansfont{Latin Modern Sans}}}\n"
        "\\setstretch{1.16}\n"
        "\\setlength{\\parskip}{0.85em}\n"
        "\\setlength{\\parindent}{0pt}\n"
        "\\definecolor{TYHeading}{HTML}{203247}\n"
        "\\titleformat{\\section}{\\Large\\bfseries\\sffamily\\color{TYHeading}}{}{0pt}{}\n"
        "\\titlespacing*{\\section}{0pt}{1.8em}{0.55em}\n"
        "\\raggedbottom\n"
        "\\pagestyle{plain}\n"
        "\\begin{document}\n"
        "\\thispagestyle{empty}\n"
        "\\begin{center}\n"
        "\\vspace*{1.9cm}\n"
        f"{{\\fontsize{{22pt}}{{28pt}}\\selectfont\\bfseries\\sffamily {escaped_title_line_one}\\par}}\n"
        "\\vspace{0.35em}\n"
        f"{{\\fontsize{{22pt}}{{28pt}}\\selectfont\\bfseries\\sffamily {escaped_title_line_two}\\par}}\n"
        "\\vspace{1.15em}\n"
        f"{{\\large\\itshape {escaped_subtitle}\\par}}\n"
        "\\vspace{1.7em}\n"
        f"{school_line}"
        "\\vspace{0.9em}\n"
        f"{{\\normalsize\\sffamily {escaped_coordinator_field}\\par}}\n"
        "\\vspace{1.4em}\n"
        f"{{\\normalsize\\itshape {escaped_cover_note}\\par}}\n"
        "\\vfill\n"
        "\\rule{0.82\\textwidth}{0.6pt}\\par\n"
        "\\end{center}\n"
        "\\newpage\n"
        "\\RaggedRight\n"
        f"{body}\n"
        "\\end{document}\n"
    )


def build_pdf_fallback_bytes(full_plan_text: str, title: str) -> bytes:
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer
        import reportlab
    except Exception:
        # Final fallback if reportlab is unavailable.
        return (full_plan_text + "\n").encode("utf-8")

    from pathlib import Path as _Path

    title_text, subtitle, sections = parse_plan_blocks(full_plan_text)
    language = infer_plan_language(title_text, subtitle)
    subtitle = standardised_export_subtitle(language)
    title_line_one, title_line_two, _coordinator_label, cover_note = build_cover_page_text(language)

    fonts_dir = _Path(reportlab.__file__).resolve().parent / "fonts"
    regular_font_path = fonts_dir / "Vera.ttf"
    bold_font_path = fonts_dir / "VeraBd.ttf"
    italic_font_path = fonts_dir / "VeraIt.ttf"
    regular_font = "Helvetica"
    bold_font = "Helvetica-Bold"
    italic_font = "Helvetica-Oblique"
    if regular_font_path.exists() and bold_font_path.exists() and italic_font_path.exists():
        pdfmetrics.registerFont(TTFont("TYVera", str(regular_font_path)))
        pdfmetrics.registerFont(TTFont("TYVeraBold", str(bold_font_path)))
        pdfmetrics.registerFont(TTFont("TYVeraItalic", str(italic_font_path)))
        regular_font = "TYVera"
        bold_font = "TYVeraBold"
        italic_font = "TYVeraItalic"

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=24 * mm,
        rightMargin=24 * mm,
        topMargin=24 * mm,
        bottomMargin=24 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TYTitle",
        parent=styles["Title"],
        fontName=bold_font,
        fontSize=22,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#203247"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "TYSubtitle",
        parent=styles["Normal"],
        fontName=italic_font,
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=18,
    )
    cover_note_style = ParagraphStyle(
        "TYCoverNote",
        parent=styles["Normal"],
        fontName=italic_font,
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#4A5560"),
        spaceAfter=10,
    )
    heading_style = ParagraphStyle(
        "TYHeading",
        parent=styles["Heading1"],
        fontName=bold_font,
        fontSize=15,
        leading=20,
        textColor=colors.HexColor("#203247"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "TYBody",
        parent=styles["BodyText"],
        fontName=regular_font,
        fontSize=11,
        leading=15,
        spaceAfter=8,
    )
    placeholder_style = ParagraphStyle(
        "TYPlaceholder",
        parent=body_style,
        fontName=italic_font,
        textColor=colors.HexColor("#68707A"),
    )

    story = [
        Spacer(1, 38),
        Paragraph(title_line_one, title_style),
        Paragraph(title_line_two, title_style),
        Spacer(1, 10),
        Paragraph(subtitle, subtitle_style),
        Spacer(1, 10),
        Paragraph(cover_note, cover_note_style),
        PageBreak(),
    ]

    for heading, paragraphs in sections:
        if heading:
            story.append(Paragraph(heading, heading_style))
        for paragraph in paragraphs:
            if paragraph:
                style = placeholder_style if set(paragraph) <= {"_"} else body_style
                story.append(Paragraph(paragraph.replace("\n", "<br/>"), style))
        if heading and needs_fill_lines(heading, language):
            for fill_line in export_fill_lines():
                story.append(Paragraph(fill_line, placeholder_style))

    doc.build(story)
    return buffer.getvalue()


def build_docx_bytes(full_plan_text: str, context: dict[str, str] | None = None) -> bytes:
    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Inches
        from docx.shared import Pt
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("python-docx is not available") from exc

    title, subtitle, sections = parse_plan_blocks(full_plan_text)
    language = infer_plan_language(title, subtitle)
    subtitle = standardised_export_subtitle(language)
    title_line_one, title_line_two, _coordinator_label, cover_note = build_cover_page_text(language)
    document = Document()

    normal_style = document.styles["Normal"]
    normal_style.font.name = "Aptos"
    normal_style._element.rPr.rFonts.set(qn("w:eastAsia"), "Aptos")
    normal_style.font.size = Pt(11)
    normal_style.paragraph_format.space_after = Pt(9)
    normal_style.paragraph_format.line_spacing = 1.16

    title_style = document.styles["Title"]
    title_style.font.name = "Aptos Display"
    title_style._element.rPr.rFonts.set(qn("w:eastAsia"), "Aptos Display")
    title_style.font.size = Pt(20)
    title_style.font.bold = True
    title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_style.paragraph_format.space_after = Pt(5)

    heading_style = document.styles["Heading 1"]
    heading_style.font.name = "Aptos Display"
    heading_style._element.rPr.rFonts.set(qn("w:eastAsia"), "Aptos Display")
    heading_style.font.size = Pt(14)
    heading_style.font.bold = True
    heading_style.paragraph_format.space_before = Pt(18)
    heading_style.paragraph_format.space_after = Pt(6)

    for section in document.sections:
        section.top_margin = Inches(0.92)
        section.bottom_margin = Inches(0.92)
        section.left_margin = Inches(0.95)
        section.right_margin = Inches(0.95)

    for cover_title_line in (title_line_one, title_line_two):
        title_paragraph = document.add_paragraph(cover_title_line, style="Title")
        title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if subtitle:
        subtitle_paragraph = document.add_paragraph(subtitle, style="Normal")
        subtitle_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subtitle_run = subtitle_paragraph.runs[0]
        subtitle_run.italic = True
        subtitle_run.font.size = Pt(12)
        subtitle_run.font.name = "Aptos"
        subtitle_paragraph.paragraph_format.space_after = Pt(20)

    school_line, coordinator_line, has_school_name = build_title_block_values(language, context)
    school_paragraph = document.add_paragraph(school_line, style="Title" if has_school_name else "Normal")
    school_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    school_run = school_paragraph.runs[0]
    school_run.font.name = "Aptos Display" if has_school_name else "Aptos"
    school_run.font.size = Pt(17 if has_school_name else 13)
    school_paragraph.paragraph_format.space_after = Pt(14)

    coordinator_paragraph = document.add_paragraph(style="Normal")
    coordinator_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    label, value = coordinator_line.split(":", 1)
    label_run = coordinator_paragraph.add_run(f"{label}:")
    label_run.bold = True
    value_run = coordinator_paragraph.add_run(value)
    value_run.font.name = "Aptos"
    coordinator_paragraph.paragraph_format.space_after = Pt(18)

    cover_note_paragraph = document.add_paragraph(cover_note, style="Normal")
    cover_note_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover_note_run = cover_note_paragraph.runs[0]
    cover_note_run.italic = True
    cover_note_paragraph.paragraph_format.space_after = Pt(24)

    rule_paragraph = document.add_paragraph()
    rule_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "8")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "AAB2BD")
    p_borders.append(bottom)
    rule_paragraph._p.get_or_add_pPr().append(p_borders)
    rule_paragraph.paragraph_format.space_after = Pt(0)

    document.add_page_break()

    for heading, paragraphs in sections:
        if heading:
            heading_paragraph = document.add_heading(heading, level=1)
            heading_paragraph.paragraph_format.space_before = Pt(18)
            heading_paragraph.paragraph_format.space_after = Pt(6)
        for paragraph in paragraphs:
            if paragraph:
                body_paragraph = document.add_paragraph(paragraph, style="Normal")
                body_paragraph.paragraph_format.space_after = Pt(9)
                body_paragraph.paragraph_format.line_spacing = 1.16
        if heading and needs_fill_lines(heading, language):
            for fill_line in export_fill_lines():
                clean_fill_line = fill_line.replace("• ", "", 1)
                fill_paragraph = document.add_paragraph(clean_fill_line, style="List Bullet")
                fill_paragraph.paragraph_format.space_after = Pt(5)

    output = BytesIO()
    document.save(output)
    return output.getvalue()


def build_pdf_bytes(full_plan_text: str, title: str, context: dict[str, str] | None = None) -> bytes:
    lualatex_path = shutil.which("lualatex")
    if not lualatex_path:
        return build_pdf_fallback_bytes(full_plan_text, title)

    latex_source = build_plan_latex(full_plan_text, context=context)
    with tempfile.TemporaryDirectory(prefix="ty_plan_pdf_", dir=GENERATED_PLANS_DIR) as temp_dir:
        temp_path = Path(temp_dir)
        tex_path = temp_path / "ty_plan_export.tex"
        pdf_path = temp_path / "ty_plan_export.pdf"
        tex_path.write_text(latex_source, encoding="utf-8")
        try:
            subprocess.run(
                [lualatex_path, "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
                cwd=temp_path,
                check=True,
                capture_output=True,
                text=True,
            )
            return pdf_path.read_bytes()
        except Exception as exc:  # pragma: no cover
            print(f"[ty-plan-pdf] latex_fallback=true reason={exc.__class__.__name__}", flush=True)
            return build_pdf_fallback_bytes(full_plan_text, title)


def main() -> None:
    st.set_page_config(page_title="Ciunas TY Planning Tool", page_icon="📘", layout="centered")

    st.title("Transition Year Planning Tool")
    st.write("Generate a structured TY annual plan in minutes - in English or Irish.")
    st.markdown(
        "- Create a full TY annual plan\n"
        "- Adapt it to your school\n"
        "- Download and edit immediately\n"
        "- Works in English and Irish"
    )
    st.info(
        "You can use this tool in English or Irish.\n\n"
        "Examples: `Create a TY plan`, `Create a TY plan in Irish`, `Cruthaigh plean Idirbhliana`."
    )
    render_source_layer_caption()

    mode = st.radio(
        "Choose a mode",
        ("Ask a TY Planning Question", "Generate a TY Annual Plan"),
        horizontal=True,
    )

    st.session_state.setdefault("generated_plan_result", None)
    st.session_state.setdefault("generated_plan_prompt", "Create a TY plan")
    st.session_state.setdefault("show_tailor_form", False)
    st.session_state.setdefault("download_format", "PDF")
    st.session_state.setdefault("download_unlocked", False)
    st.session_state.setdefault("lead_name", "")
    st.session_state.setdefault("lead_email", "")

    if mode == "Ask a TY Planning Question":
        input_label = "Ask a TY planning question in English or Irish"
        input_placeholder = "For example: How should a school structure a Transition Year programme? / Conas ba chóir clár Idirbhliana a struchtúrú?"
        submit_label = "Ask"
        loading_message = "Finding grounded TY guidance..."
        empty_message = "Please enter a TY planning question before continuing."
        idle_message = "Enter a TY planning question in English or Irish to get grounded guidance."
    else:
        input_label = "Optional: add a focus or context"
        input_placeholder = "e.g. wellbeing focus, small rural school, student leadership, as Gaeilge"
        submit_label = "Generate TY Plan"
        loading_message = "Generating TY plan..."
        empty_message = ""
        idle_message = (
            "Generate a full TY Annual Plan in English or Irish, with optional context to shape the draft."
        )

    with st.form("ty_question_form", clear_on_submit=False):
        user_input = st.text_area(
            input_label,
            placeholder=input_placeholder,
            height=120,
            help=(
                "You can enter your own context or just generate a plan. You can ask in English or Irish. "
                "Examples: Create a TY plan, Create a TY plan focused on wellbeing, Cruthaigh plean Idirbhliana."
                if mode == "Generate a TY Annual Plan"
                else "You can ask in English or Irish."
            ),
        )
        submitted = st.form_submit_button(submit_label)

    if not submitted:
        if mode == "Ask a TY Planning Question" or not st.session_state.get("generated_plan_result"):
            st.info(idle_message)
            return
        result = st.session_state["generated_plan_result"]
        question = str(st.session_state.get("generated_plan_prompt", "Create a TY plan"))
    else:
        user_input = user_input.strip()
        if mode == "Ask a TY Planning Question":
            question = user_input
            if not question:
                st.warning(empty_message)
                return
        else:
            question = build_download_prompt(user_input)

        try:
            with st.spinner(loading_message):
                result = answer_question(question)
        except Exception as exc:  # pragma: no cover
            if mode == "Generate a TY Annual Plan":
                st.error("TY plan generation failed. Please try again.")
            else:
                st.error("The guidance engine hit a runtime error. Please try again.")
            return

        if mode == "Generate a TY Annual Plan":
            st.session_state["generated_plan_result"] = result
            st.session_state["generated_plan_prompt"] = question
            st.session_state["show_tailor_form"] = False

    answer = str(result.get("answer", "")).strip()
    key_points = result.get("key_points") or []
    sources = result.get("sources") or []
    evidence_note = str(result.get("evidence_note", "")).strip()
    answer_mode = str(result.get("answer_mode", "")).strip()
    generation_source = str(result.get("generation_source", "")).strip()
    model_used = str(result.get("model_used", "")).strip()
    full_plan_text = answer if mode == "Generate a TY Annual Plan" and is_generator_result(answer_mode) else ""

    if not answer and not key_points and not sources:
        if mode == "Generate a TY Annual Plan":
            st.warning("No TY plan could be generated from the current template mode.")
        else:
            st.warning("No grounded answer could be assembled for this question from the current source set.")
        return

    if mode == "Generate a TY Annual Plan":
        if not full_plan_text:
            st.error("Generator mode did not return a full TY plan, so export has been disabled for this response.")
            return
        unlocked = st.session_state.get("download_unlocked", False)
        st.subheader("TY Annual Plan")
        if unlocked:
            render_generated_plan(full_plan_text)
            st.caption("You can download this plan or improve it further for your school.")
        else:
            render_plan_preview(full_plan_text)
            st.info("Continue to full plan by unlocking below.")
        output_language = infer_output_language(answer_mode, question)
        markdown_path, _text_path = save_generated_plan(full_plan_text, output_language)
        plan_title = full_plan_text.splitlines()[0].strip() if full_plan_text.splitlines() else "TY Annual Plan"
        prompt_context = parse_template_context(question)
        pdf_bytes = build_pdf_bytes(full_plan_text, plan_title, context=prompt_context)
        docx_bytes: bytes | None = None
        docx_error = ""
        try:
            docx_bytes = build_docx_bytes(full_plan_text, context=prompt_context)
        except Exception as exc:  # pragma: no cover
            docx_error = str(exc)
        export_char_count = len(full_plan_text)
        print(
            f"[ty-plan-export] mode={answer_mode} language={output_language} chars={export_char_count}",
            flush=True,
        )
        st.markdown("### Download your formatted TY plan")
        st.caption("The downloadable version is formatted and ready to edit and share.")
        st.caption("Includes a clean layout suitable for school use.")
        st.caption(f"Export source length: {export_char_count} characters.")
        if SHOW_DOCX_DIAGNOSTIC:
            docx_runtime_available = bool(docx_bytes)
            st.caption(
                f"Temporary diagnostic: DOCX runtime support is {'available' if docx_runtime_available else 'unavailable'}."
            )
            if not docx_runtime_available:
                st.caption(
                    "Temporary diagnostic: DOCX unavailable reason: "
                    f"{docx_error or 'build_docx_bytes returned no content.'}"
                )
        if not unlocked:
            with st.form("download_unlock_form", clear_on_submit=False):
                lead_email = st.text_input(
                    "Email address",
                    value=st.session_state.get("lead_email", ""),
                    placeholder="e.g. teacher@school.ie",
                )
                lead_name = st.text_input(
                    "Name (optional)",
                    value=st.session_state.get("lead_name", ""),
                    placeholder="e.g. Mary",
                )
                st.caption("Enter your email to unlock the download and receive practical TY planning supports.")
                unlock_submitted = st.form_submit_button("Unlock download")

            if unlock_submitted:
                cleaned_email = lead_email.strip()
                cleaned_name = lead_name.strip()
                if not looks_like_email(cleaned_email):
                    st.warning("Please enter a valid email address to unlock the download.")
                else:
                    leads_path = save_lead_row(
                        {
                            "timestamp": datetime.now().isoformat(timespec="seconds"),
                            "email": cleaned_email,
                            "name": cleaned_name,
                            "mode": "Generate a TY Annual Plan",
                            "language": output_language,
                            "school_name": str(prompt_context.get("school_name", "")),
                            "school_type": str(prompt_context.get("school_type", "")),
                            "priorities": str(prompt_context.get("priorities", "")),
                        }
                    )
                    st.session_state["lead_email"] = cleaned_email
                    st.session_state["lead_name"] = cleaned_name
                    st.session_state["download_unlocked"] = True
                    st.rerun()
        else:
            download_options = ["PDF", "Word (.docx)"] if docx_bytes else ["PDF", "Markdown (.md fallback)"]
            default_index = 0 if st.session_state.get("download_format") == "PDF" else min(1, len(download_options) - 1)
            download_format = st.selectbox("Choose format:", download_options, index=default_index, key="download_format")
            if download_format == "PDF":
                pdf_path = save_export_file(pdf_bytes, output_language, "pdf", "pdf")
                st.caption(
                    "PDF export is generated directly from the full plan shown on screen."
                )
                st.download_button(
                    "Download plan",
                    data=pdf_bytes,
                    file_name=pdf_path.name,
                    mime="application/pdf",
                )
            elif download_format == "Word (.docx)":
                docx_path = save_export_file(docx_bytes or b"", output_language, "docx", "docx")
                st.caption(
                    "Word export preserves the title and section hierarchy for editing."
                )
                st.download_button(
                    "Download plan",
                    data=docx_bytes,
                    file_name=docx_path.name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            else:
                markdown_bytes = markdown_path.read_bytes()
                markdown_export_path = save_export_file(markdown_bytes, output_language, "markdown", "md")
                st.caption(
                    "Word export is temporarily unavailable, so the editable fallback is Markdown."
                )
                if docx_error:
                    st.caption("Word export fallback is active for this session.")
                st.download_button(
                    "Download plan",
                    data=markdown_bytes,
                    file_name=markdown_export_path.name,
                    mime="text/markdown",
                )
        if st.button("Improve this plan for my school"):
            st.session_state["show_tailor_form"] = True

        if st.session_state.get("show_tailor_form"):
            st.markdown("### Tailor this plan for your school")
            st.write("Add a few details to improve the plan. Leave anything blank if not relevant.")
            with st.form("tailor_plan_form", clear_on_submit=False):
                school_name = st.text_input(
                    "School name (optional)",
                    placeholder="e.g. St. Mary's College",
                )
                cohort_size = st.text_input(
                    "Approximate TY cohort size (optional)",
                    placeholder="e.g. 68 students",
                )
                school_type = st.text_input(
                    "School type",
                    placeholder="e.g. small rural mixed school",
                    help=(
                        "Examples: Gaelcholáiste, English-medium school, mixed school, girls' school, "
                        "boys' school, large urban school, small rural school, DEIS school."
                    ),
                )
                school_ethos = st.text_input(
                    "School ethos or character (optional)",
                    placeholder="e.g. Catholic ethos, Gaelscoil, ETB school",
                )
                priorities = st.text_area(
                    "Main priorities for TY this year",
                    height=80,
                    placeholder="e.g. wellbeing and student leadership",
                    help=(
                        "Examples: wellbeing, student leadership, work experience, confidence, "
                        "balance, engagement"
                    ),
                )
                existing_modules = st.text_area(
                    "Existing modules or programmes",
                    height=80,
                    placeholder="e.g. mini-company and Gaisce",
                    help=(
                        "Examples: mini-company, Gaisce, outdoor education, musical, enterprise projects"
                    ),
                )
                work_experience = st.text_input(
                    "Work experience timing",
                    placeholder="e.g. two-week block in January",
                    help=(
                        "Examples: January block, spread across the year, two-week block, not yet decided"
                    ),
                )
                additional_context = st.text_area(
                    "Anything else we should include? (optional)",
                    height=100,
                    placeholder=(
                        "Examples: school ethos or mission, fixed events or trips, staffing or timetable "
                        "constraints, existing TY traditions, local community links, particular student "
                        "needs, assessment or portfolio expectations"
                    ),
                    help=(
                        "You can add any extra detail that would make the plan more realistic for your school."
                    ),
                )
                language = st.radio("Language for the final plan", ("English", "Irish"), horizontal=True)
                improve_submitted = st.form_submit_button("Generate improved plan")

            if improve_submitted:
                improved_prompt = build_tailored_plan_prompt(
                    school_name=school_name.strip(),
                    cohort_size=cohort_size.strip(),
                    school_type=school_type.strip(),
                    school_ethos=school_ethos.strip(),
                    priorities=priorities.strip(),
                    existing_modules=existing_modules.strip(),
                    work_experience=work_experience.strip(),
                    additional_context=additional_context.strip(),
                    language=language.strip(),
                )
                try:
                    with st.spinner("Generating improved TY plan..."):
                        improved_result = answer_question(improved_prompt)
                except Exception as exc:  # pragma: no cover
                    st.error("Improved TY plan generation failed. Please try again.")
                    st.code(str(exc))
                    return

                improved_answer = str(improved_result.get("answer", "")).strip()
                if not improved_answer:
                    st.warning("No improved TY plan could be generated from the provided context.")
                    return

                st.session_state["generated_plan_result"] = improved_result
                st.session_state["generated_plan_prompt"] = improved_prompt
                st.session_state["show_tailor_form"] = False
                st.rerun()
    else:
        st.subheader("Answer")
        st.write(answer or "No grounded answer text was returned.")

    if mode == "Ask a TY Planning Question" and key_points:
        st.subheader("Key Points")
        for point in key_points:
            layer, body = split_layer_prefix(str(point))
            if layer:
                st.markdown(f"- `{layer}` {body}")
            else:
                st.markdown(f"- {body}")

    if mode == "Ask a TY Planning Question" and sources:
        st.subheader("Sources")
        for source in sources:
            title = str(source.get("title", "Untitled source"))
            layer = str(source.get("source_layer", "unknown"))
            chunk_id = str(source.get("chunk_id", ""))
            source_note = str(source.get("source_note", "")).strip()
            line = f"- `{layer}` {title}"
            if chunk_id:
                line += f" ({chunk_id})"
            if source_note:
                line += f" [{source_note}]"
            st.markdown(line)

    if evidence_note and mode == "Ask a TY Planning Question":
        st.subheader("Evidence Note")
        st.write(evidence_note)

if __name__ == "__main__":
    main()
