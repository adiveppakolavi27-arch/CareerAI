from backend.utils.resume_quality import analyze_resume_quality


# Sample resume text
resume_text = """
ADIVEPPA
Python Developer

Email: adiveppa@gmail.com
Phone: 9876543210

EDUCATION
Bachelor of Engineering in Computer Science.

SKILLS
Python, Flask, SQL, HTML, CSS, JavaScript.

PROJECTS
- Developed an AI Resume Analyzer using Python.
- Created a website using Flask and HTML.
- Implemented resume analysis functionality.

EXPERIENCE
Completed an internship in Python development.

CERTIFICATIONS
Python Programming Certificate.

Developed applications and created useful projects.
Implemented features and improved application performance.
"""

# Analyze resume
result = analyze_resume_quality(resume_text)


# Display results
print("\n========== RESUME QUALITY REPORT ==========")

print("\nQuality Score:", result["quality_score"], "%")
print("Category:", result["category"])

print("\nWord Count:", result["word_count"])
print("Bullet Points:", result["bullet_count"])

print("\nDetected Sections:")
for section in result["detected_sections"]:
    print("-", section)

print("\nMissing Sections:")
for section in result["missing_sections"]:
    print("-", section)

print("\nDetected Action Verbs:")
for verb in result["detected_action_verbs"]:
    print("-", verb)

print("\nStrengths:")
for strength in result["strengths"]:
    print("-", strength)

print("\nImprovement Suggestions:")
for suggestion in result["suggestions"]:
    print("-", suggestion)

print("\nRepeated Words:")
print(result["repeated_words"])

print("\n===========================================")