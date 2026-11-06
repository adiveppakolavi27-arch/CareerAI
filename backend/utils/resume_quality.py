import re


def analyze_resume_quality(resume_text):

    text = resume_text.strip()
    text_lower = text.lower()

    suggestions = []
    strengths = []

    # 1. Word Count
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)

    if word_count >= 300:
        strengths.append("Resume contains sufficient content.")
    else:
        suggestions.append(
            "Add more relevant details about your education, "
            "projects and experience."
        )

    # 2. Email Detection
    email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    email = re.search(email_pattern, text)

    if email:
        strengths.append("Email address detected.")
    else:
        suggestions.append("Add a valid email address.")

    # 3. Phone Number Detection
    phone_pattern = r"(\+?\d[\d\s()-]{8,}\d)"
    phone = re.search(phone_pattern, text)

    if phone:
        strengths.append("Phone number detected.")
    else:
        suggestions.append("Add your contact number.")

    # 4. Section Detection
    sections = {
        "Education": [
            "education", "academic qualification"
        ],
        "Experience": [
            "experience", "work experience", "internship"
        ],
        "Skills": [
            "skills", "technical skills"
        ],
        "Projects": [
            "projects", "academic projects"
        ],
        "Certifications": [
            "certifications", "certificates"
        ]
    }

    detected_sections = []
    missing_sections = []

    for section, keywords in sections.items():

        if any(keyword in text_lower for keyword in keywords):
            detected_sections.append(section)
        else:
            missing_sections.append(section)

    for section in missing_sections:
        suggestions.append(
            f"Consider adding a {section} section if relevant."
        )

    # 5. Bullet Point Detection
    bullet_count = len(
        re.findall(r"(?m)^\s*[-•*]\s+", text)
    )

    if bullet_count > 0:
        strengths.append("Bullet points detected.")
    else:
        suggestions.append(
            "Use bullet points to make information easier to scan."
        )

    # 6. Action Verb Detection
    action_verbs = [
        "developed", "created", "designed",
        "implemented", "managed", "built",
        "improved", "analyzed", "organized",
        "automated", "maintained", "led"
    ]

    detected_action_verbs = [
        verb for verb in action_verbs
        if re.search(r"\b" + re.escape(verb) + r"\b", text_lower)
    ]

    if detected_action_verbs:
        strengths.append("Action verbs detected.")
    else:
        suggestions.append(
            "Use action verbs such as Developed, Created, "
            "Implemented and Designed."
        )

    # 7. Repeated Word Detection
    word_frequency = {}

    for word in words:

        word = word.lower()

        if len(word) > 3:
            word_frequency[word] = word_frequency.get(word, 0) + 1

    repeated_words = {
        word: count
        for word, count in word_frequency.items()
        if count >= 5
    }

    if repeated_words:
        suggestions.append(
            "Review frequently repeated words: "
            + ", ".join(repeated_words.keys())
        )

    # 8. Quality Score
    checks = [
        word_count >= 300,
        bool(email),
        bool(phone),
        len(detected_sections) >= 3,
        bullet_count > 0,
        bool(detected_action_verbs)
    ]

    quality_score = round(
        sum(checks) / len(checks) * 100
    )

    if quality_score >= 80:
        category = "Excellent"
    elif quality_score >= 60:
        category = "Good"
    elif quality_score >= 40:
        category = "Average"
    else:
        category = "Needs Improvement"

    return {
        "quality_score": quality_score,
        "category": category,
        "word_count": word_count,
        "detected_sections": detected_sections,
        "missing_sections": missing_sections,
        "detected_action_verbs": detected_action_verbs,
        "repeated_words": repeated_words,
        "bullet_count": bullet_count,
        "strengths": strengths,
        "suggestions": suggestions
    }