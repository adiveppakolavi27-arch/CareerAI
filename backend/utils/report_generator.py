import os
import uuid
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)


# --------------------------------------------------
# COLOR THEME
# --------------------------------------------------

PRIMARY = colors.HexColor("#6C63FF")
SECONDARY = colors.HexColor("#3498DB")
DARK = colors.HexColor("#202344")
LIGHT = colors.HexColor("#F5F3FF")
GREEN = colors.HexColor("#2ECC71")
RED = colors.HexColor("#E74C3C")
GREY = colors.HexColor("#777777")


# --------------------------------------------------
# SAFE TEXT CONVERSION
# --------------------------------------------------

def safe_text(value):

    if value is None:
        return ""

    return escape(str(value))


def create_paragraph(text, style):

    return Paragraph(safe_text(text), style)


# --------------------------------------------------
# HEADER AND FOOTER
# --------------------------------------------------

def add_page_design(canvas, document):

    canvas.saveState()

    page_width, page_height = A4

    # Header line
    canvas.setStrokeColor(PRIMARY)
    canvas.setLineWidth(2)

    canvas.line(
        20 * mm,
        page_height - 15 * mm,
        page_width - 20 * mm,
        page_height - 15 * mm
    )

    # Header title
    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(DARK)

    canvas.drawString(
        20 * mm,
        page_height - 12 * mm,
        "AI RESUME ANALYZER"
    )

    # Footer line
    canvas.setStrokeColor(colors.lightgrey)
    canvas.setLineWidth(0.5)

    canvas.line(
        20 * mm,
        15 * mm,
        page_width - 20 * mm,
        15 * mm
    )

    # Footer text
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)

    canvas.drawString(
        20 * mm,
        10 * mm,
        "AI Resume Analysis Report"
    )

    canvas.drawRightString(
        page_width - 20 * mm,
        10 * mm,
        f"Page {document.page}"
    )

    canvas.restoreState()


# --------------------------------------------------
# TABLE GENERATOR
# --------------------------------------------------

def create_table(data, widths):

    table = Table(
        data,
        colWidths=widths,
        repeatRows=1,
        hAlign="LEFT"
    )

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("FONTSIZE", (0, 0), (-1, -1), 9),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),

        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, LIGHT]),

        ("VALIGN", (0, 0), (-1, -1), "TOP"),

        ("LEFTPADDING", (0, 0), (-1, -1), 8),

        ("RIGHTPADDING", (0, 0), (-1, -1), 8),

        ("TOPPADDING", (0, 0), (-1, -1), 8),

        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),

    ]))

    return table


# --------------------------------------------------
# MAIN REPORT GENERATOR
# --------------------------------------------------

def generate_resume_report(
    report_folder,
    user_id,
    filename,
    ats_result,
    skills,
    jd_result=None,
    gemini_result=None,
    quality_result=None
):

    os.makedirs(report_folder, exist_ok=True)

    report_name = f"user_{user_id}_{uuid.uuid4().hex}.pdf"

    report_path = os.path.join(
        report_folder,
        report_name
    )

    document = SimpleDocTemplate(
        report_path,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=23 * mm,
        bottomMargin=22 * mm
    )

    # --------------------------------------------------
    # STYLES
    # --------------------------------------------------

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        textColor=PRIMARY,
        fontSize=22,
        leading=27,
        alignment=1,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        textColor=GREY,
        fontSize=9,
        alignment=1,
        spaceAfter=15
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        textColor=PRIMARY,
        fontSize=13,
        leading=17,
        spaceBefore=14,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "ReportNormal",
        parent=styles["BodyText"],
        fontSize=9,
        leading=14,
        spaceAfter=6
    )

    small_style = ParagraphStyle(
        "SmallText",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        textColor=GREY
    )

    bullet_style = ParagraphStyle(
        "BulletStyle",
        parent=normal_style,
        leftIndent=12,
        firstLineIndent=-8
    )

    story = []

    # --------------------------------------------------
    # REPORT TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "AI RESUME ANALYSIS REPORT",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Professional Resume Evaluation and Job Compatibility",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Resume:</b> {safe_text(filename)}",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Report Date:</b> {datetime.now().strftime('%d %B %Y')}",
            normal_style
        )
    )

    story.append(Spacer(1, 10))

    # --------------------------------------------------
    # 1. ATS SCORE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "1. ATS RESUME SCORE",
            heading_style
        )
    )

    total_score = ats_result.get("total_score", 0)

    category = ats_result.get(
        "category",
        "Not available"
    )

    story.append(
        Paragraph(
            f"<b>ATS Score:</b> {total_score}/100",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Category:</b> {safe_text(category)}",
            normal_style
        )
    )

    # ATS breakdown

    score_data = [
        [
            Paragraph("<b>Category</b>", normal_style),
            Paragraph("<b>Score</b>", normal_style)
        ]
    ]

    for name, marks in ats_result.get("breakdown", {}).items():

        score_data.append([
            Paragraph(safe_text(name), normal_style),
            Paragraph(safe_text(marks), normal_style)
        ])

    if len(score_data) > 1:

        story.append(
            create_table(
                score_data,
                [115 * mm, 40 * mm]
            )
        )

    # --------------------------------------------------
    # 2. RESUME QUALITY ANALYSIS
    # --------------------------------------------------

    if quality_result:

        story.append(
            Paragraph(
                "2. RESUME QUALITY ANALYSIS",
                heading_style
            )
        )

        quality_score = quality_result.get(
            "quality_score",
            0
        )

        quality_category = quality_result.get(
            "category",
            "Not available"
        )

        story.append(
            Paragraph(
                f"<b>Quality Score:</b> {quality_score}%",
                normal_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Quality Category:</b> "
                f"{safe_text(quality_category)}",
                normal_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Word Count:</b> "
                f"{quality_result.get('word_count', 0)}",
                normal_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Bullet Points:</b> "
                f"{quality_result.get('bullet_count', 0)}",
                normal_style
            )
        )

        # Detected sections

        story.append(
            Paragraph(
                "<b>Detected Sections:</b>",
                normal_style
            )
        )

        sections = quality_result.get(
            "detected_sections",
            []
        )

        story.append(
            Paragraph(
                safe_text(", ".join(sections) if sections else "None"),
                normal_style
            )
        )

        # Missing sections

        story.append(
            Paragraph(
                "<b>Missing Sections:</b>",
                normal_style
            )
        )

        missing_sections = quality_result.get(
            "missing_sections",
            []
        )

        story.append(
            Paragraph(
                safe_text(
                    ", ".join(missing_sections)
                    if missing_sections else "None"
                ),
                normal_style
            )
        )

        # Strengths

        story.append(
            Paragraph(
                "<b>Resume Strengths:</b>",
                normal_style
            )
        )

        strengths = quality_result.get(
            "strengths",
            []
        )

        for strength in strengths:

            story.append(
                Paragraph(
                    "• " + safe_text(strength),
                    bullet_style
                )
            )

        # Suggestions

        story.append(
            Paragraph(
                "<b>Improvement Suggestions:</b>",
                normal_style
            )
        )

        suggestions = quality_result.get(
            "suggestions",
            []
        )

        for suggestion in suggestions:

            story.append(
                Paragraph(
                    "• " + safe_text(suggestion),
                    bullet_style
                )
            )

        # Repeated words

        repeated_words = quality_result.get(
            "repeated_words",
            {}
        )

        if repeated_words:

            story.append(
                Paragraph(
                    "<b>Frequently Repeated Words:</b>",
                    normal_style
                )
            )

            repeated_text = ", ".join(
                f"{word} ({count})"
                for word, count in repeated_words.items()
            )

            story.append(
                Paragraph(
                    safe_text(repeated_text),
                    normal_style
                )
            )

    # --------------------------------------------------
    # 3. DETECTED SKILLS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "3. DETECTED TECHNICAL SKILLS",
            heading_style
        )
    )

    skills_text = (
        ", ".join(str(skill) for skill in skills)
        if skills else "No skills detected."
    )

    story.append(
        Paragraph(
            safe_text(skills_text),
            normal_style
        )
    )

    # --------------------------------------------------
    # 4. JOB DESCRIPTION MATCHING
    # --------------------------------------------------

    if jd_result:

        story.append(
            Paragraph(
                "4. JOB DESCRIPTION COMPATIBILITY",
                heading_style
            )
        )

        match_percentage = jd_result.get(
            "match_percentage",
            0
        )

        compatibility = jd_result.get(
            "compatibility",
            "Not available"
        )

        story.append(
            Paragraph(
                f"<b>Job Match Percentage:</b> "
                f"{match_percentage}%",
                normal_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Compatibility:</b> "
                f"{safe_text(compatibility)}",
                normal_style
            )
        )

        # Matching skills

        matching_skills = jd_result.get(
            "matching_skills",
            []
        )

        story.append(
            Paragraph(
                "<b>Matching Skills:</b>",
                normal_style
            )
        )

        story.append(
            Paragraph(
                safe_text(
                    ", ".join(matching_skills)
                    if matching_skills else "None"
                ),
                normal_style
            )
        )

        # Missing skills

        missing_skills = jd_result.get(
            "missing_skills",
            []
        )

        story.append(
            Paragraph(
                "<b>Missing Skills:</b>",
                normal_style
            )
        )

        story.append(
            Paragraph(
                safe_text(
                    ", ".join(missing_skills)
                    if missing_skills else "None"
                ),
                normal_style
            )
        )

        # Required skills

        required_skills = jd_result.get(
            "required_skills",
            []
        )

        story.append(
            Paragraph(
                "<b>Recognized Required Skills:</b>",
                normal_style
            )
        )

        story.append(
            Paragraph(
                safe_text(
                    ", ".join(required_skills)
                    if required_skills else "None"
                ),
                normal_style
            )
        )

        # Recommendations

        story.append(
            Paragraph(
                "<b>Skill Improvement Recommendations:</b>",
                normal_style
            )
        )

        recommendations = jd_result.get(
            "recommendations",
            []
        )

        for recommendation in recommendations:

            story.append(
                Paragraph(
                    "• " + safe_text(recommendation),
                    bullet_style
                )
            )

    # --------------------------------------------------
    # 5. GEMINI AI FEEDBACK
    # --------------------------------------------------

    if gemini_result:

        story.append(
            Paragraph(
                "5. GEMINI AI RESUME FEEDBACK",
                heading_style
            )
        )

        if gemini_result.get("success"):

            ai_text = gemini_result.get(
                "analysis",
                ""
            )

            if ai_text:

                for line in ai_text.splitlines():

                    line = line.strip()

                    if line:

                        story.append(
                            Paragraph(
                                safe_text(line),
                                normal_style
                            )
                        )

            else:

                story.append(
                    Paragraph(
                        "No AI feedback was returned.",
                        normal_style
                    )
                )

        else:

            story.append(
                Paragraph(
                    safe_text(
                        gemini_result.get(
                            "error",
                            "AI feedback unavailable."
                        )
                    ),
                    normal_style
                )
            )

    # --------------------------------------------------
    # DISCLAIMER
    # --------------------------------------------------

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "IMPORTANT DISCLAIMER",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "This report provides estimated resume feedback "
            "based on the project's scoring rules and recognized "
            "skills. It is not an official ATS evaluation, "
            "hiring decision, or employment guarantee. "
            "AI-generated recommendations should be reviewed "
            "for accuracy before making changes to a resume.",
            small_style
        )
    )

    # --------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------

    document.build(
        story,
        onFirstPage=add_page_design,
        onLaterPages=add_page_design
    )

    return report_name