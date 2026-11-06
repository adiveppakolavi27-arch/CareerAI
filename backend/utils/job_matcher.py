from backend.utils.skills_extractor import (
    compare_skills,
    SKILL_CATEGORIES
)


def analyze_job_match(resume_skills, job_description):

    # Compare resume skills with job requirements
    result = compare_skills(
        resume_skills,
        job_description
    )

    required_skills = result["required_skills"]
    matching_skills = result["matching_skills"]
    missing_skills = result["missing_skills"]

    # Group required skills by category
    categorized_skills = {}

    for category, category_skills in SKILL_CATEGORIES.items():

        category_required = [
            skill for skill in required_skills
            if skill in category_skills
        ]

        if category_required:

            category_matching = [
                skill for skill in category_required
                if skill in matching_skills
            ]

            category_missing = [
                skill for skill in category_required
                if skill in missing_skills
            ]

            categorized_skills[category] = {
                "required": category_required,
                "matching": category_matching,
                "missing": category_missing
            }

    # Generate learning recommendations
    recommendations = []

    for skill in missing_skills:

        recommendations.append(
            f"Learn and practice {skill}."
        )

    # Overall result
    match_percentage = result["match_percentage"]

    if match_percentage >= 80:
        compatibility = "Excellent Match"

    elif match_percentage >= 60:
        compatibility = "Good Match"

    elif match_percentage >= 40:
        compatibility = "Moderate Match"

    else:
        compatibility = "Needs Improvement"

    return {
        "required_skills": required_skills,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "match_percentage": match_percentage,
        "compatibility": compatibility,
        "categorized_skills": categorized_skills,
        "recommendations": recommendations
    }