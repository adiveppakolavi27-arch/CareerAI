from backend.utils.ats_scorer import score_resume

resume = """
Name: Student

Email: student@gmail.com
Phone: +919876543210

Education:
Bachelor of Engineering in Computer Science.

Experience:
Python Developer Internship.

Projects:
Developed an AI Resume Analyzer.

Skills:
Python, Java, SQL, Machine Learning,
HTML, CSS, Flask, Communication.
"""

skills = [
    "Python",
    "Java",
    "SQL",
    "Machine Learning",
    "HTML",
    "CSS",
    "Flask",
    "Communication"
]

result = score_resume(resume, skills)

print("ATS RESUME ANALYSIS")
print("-------------------")

print("Total Score:", result["total_score"], "/100")

print("Category:", result["category"])

print("\nScore Breakdown:")

for category, marks in result["breakdown"].items():
    print(category, ":", marks)