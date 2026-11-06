import re


def score_resume(resume_text, skills):

    text = resume_text.lower()

    scores = {}

    # 1. Skills Score (30 marks)
    skill_count = len(skills)

    scores["Skills"] = min(
        skill_count * 3,
        30
    )

    # 2. Education Score (15 marks)
    education_keywords = [
        "education",
        "bachelor",
        "degree",
        "b.tech",
        "b.e",
        "master",
        "university",
        "college",
        "diploma"
    ]

    education_found = any(
        word in text for word in education_keywords
    )

    scores["Education"] = 15 if education_found else 0

    # 3. Experience Score (15 marks)
    experience_keywords = [
        "experience",
        "internship",
        "worked",
        "developer",
        "engineer",
        "employment"
    ]

    experience_found = any(
        word in text for word in experience_keywords
    )

    scores["Experience"] = 15 if experience_found else 0

    # 4. Projects Score (15 marks)
    project_keywords = [
        "projects",
        "project",
        "developed",
        "implemented",
        "built"
    ]

    project_found = any(
        word in text for word in project_keywords
    )

    scores["Projects"] = 15 if project_found else 0

    # 5. Contact Information Score (15 marks)

    # Email detection
    email_found = bool(
        re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            resume_text
        )
    )

    # Indian mobile number detection
    phone_found = bool(
        re.search(
            r"\b(?:\+91[- ]?)?[6-9]\d{9}\b",
            resume_text
        )
    )

    contact_score = 0

    if email_found:
        contact_score += 8

    if phone_found:
        contact_score += 7

    scores["Contact Information"] = contact_score

    # 6. Resume Content Score (10 marks)
    word_count = len(text.split())

    if word_count >= 300:
        scores["Resume Content"] = 10

    elif word_count >= 150:
        scores["Resume Content"] = 7

    elif word_count >= 50:
        scores["Resume Content"] = 4

    else:
        scores["Resume Content"] = 0

    # Calculate total score
    total_score = sum(scores.values())

    # Score category
    if total_score >= 80:
        category = "Excellent"

    elif total_score >= 60:
        category = "Good"

    elif total_score >= 40:
        category = "Average"

    else:
        category = "Needs Improvement"

    return {
        "total_score": total_score,
        "category": category,
        "breakdown": scores
    }