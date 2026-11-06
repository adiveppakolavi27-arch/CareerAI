from backend.utils.skills_extractor import extract_skills

sample_resume = """
I know Python, Java, SQL, Machine Learning,
HTML, CSS, Flask, and Data Science.
I also have communication and leadership skills.
"""

skills = extract_skills(sample_resume)

print("Extracted Skills:")

for skill in skills:
    print("-", skill)