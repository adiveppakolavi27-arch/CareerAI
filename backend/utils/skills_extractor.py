import re


# ==========================================
# 1. SKILL DATABASE
# ==========================================

SKILL_CATEGORIES = {

    "Programming Languages": [
        "Python", "Java", "C", "C++", "C#", "JavaScript",
        "TypeScript", "PHP", "R", "Ruby", "Go", "Kotlin",
        "Swift", "Dart"
    ],

    "Web Development": [
        "HTML", "CSS", "React", "Angular", "Vue.js",
        "Node.js", "Express.js", "Flask", "Django",
        "FastAPI", "Bootstrap", "Tailwind CSS",
        "Next.js", "REST API", "GraphQL"
    ],

    "Databases": [
        "SQL", "MySQL", "MongoDB", "SQLite",
        "PostgreSQL", "Oracle", "Redis", "Firebase"
    ],

    "AI and Machine Learning": [
        "Artificial Intelligence", "Machine Learning",
        "Deep Learning", "Natural Language Processing",
        "Computer Vision", "Generative AI",
        "Large Language Models", "Neural Networks",
        "Prompt Engineering", "Reinforcement Learning"
    ],

    "Data Science": [
        "Data Science", "Data Analysis", "Data Visualization",
        "Pandas", "NumPy", "Matplotlib", "Seaborn",
        "Scikit-learn", "TensorFlow", "PyTorch",
        "Statistics", "Excel", "Microsoft Excel",
        "Power BI", "Tableau"
    ],

    "Cloud and DevOps": [
        "AWS", "Microsoft Azure", "Google Cloud",
        "Docker", "Kubernetes", "Jenkins",
        "CI/CD", "Linux", "Git", "GitHub", "GitLab"
    ],

    "Software Development": [
        "Object-Oriented Programming",
        "Data Structures", "Algorithms",
        "Software Testing", "Unit Testing",
        "Agile", "Scrum", "Debugging",
        "Version Control"
    ],

    "Soft Skills": [
        "Communication", "Leadership", "Teamwork",
        "Problem Solving", "Time Management",
        "Critical Thinking", "Adaptability",
        "Creativity", "Decision Making",
        "Project Management"
    ]
}


# ==========================================
# 2. SKILL ALIASES
# ==========================================

SKILL_ALIASES = {

    "JS": "JavaScript",
    "Javascript": "JavaScript",

    "TS": "TypeScript",

    "NodeJS": "Node.js",
    "Node JS": "Node.js",

    "ReactJS": "React",
    "React.js": "React",

    "Vue": "Vue.js",

    "Express": "Express.js",

    "Sklearn": "Scikit-learn",
    "Scikit learn": "Scikit-learn",

    "PyTorch": "PyTorch",

    "ML": "Machine Learning",
    "DL": "Deep Learning",
    "AI": "Artificial Intelligence",
    "NLP": "Natural Language Processing",
    "CV": "Computer Vision",
    "GenAI": "Generative AI",
    "LLM": "Large Language Models",

    "PowerBI": "Power BI",

    "Postgres": "PostgreSQL",

    "MSSQL": "Microsoft SQL Server",

    "OOP": "Object-Oriented Programming",

    "DSA": "Data Structures"
}


# ==========================================
# 3. CREATE MASTER SKILL LIST
# ==========================================

SKILLS_LIST = []

for category_skills in SKILL_CATEGORIES.values():

    SKILLS_LIST.extend(category_skills)


# Add Microsoft SQL Server if needed.

SKILLS_LIST.append("Microsoft SQL Server")


# ==========================================
# 4. NORMALIZE SKILL NAMES
# ==========================================

def normalize_skill(skill):

    cleaned_skill = skill.strip().lower()

    for alias, canonical_name in SKILL_ALIASES.items():

        if cleaned_skill == alias.lower():

            return canonical_name

    for known_skill in SKILLS_LIST:

        if cleaned_skill == known_skill.lower():

            return known_skill

    return skill.strip()


# ==========================================
# 5. EXTRACT SKILLS FROM TEXT
# ==========================================

def extract_skills(text):

    if not text:

        return []

    text = text.lower()

    found_skills = set()

    # Search for standard skill names.

    for skill in SKILLS_LIST:

        pattern = (
            r"(?<![a-zA-Z0-9])"
            + re.escape(skill.lower())
            + r"(?![a-zA-Z0-9])"
        )

        if re.search(pattern, text):

            found_skills.add(skill)

    # Search for alternative skill names.

    for alias, canonical_name in SKILL_ALIASES.items():

        pattern = (
            r"(?<![a-zA-Z0-9])"
            + re.escape(alias.lower())
            + r"(?![a-zA-Z0-9])"
        )

        if re.search(pattern, text):

            found_skills.add(canonical_name)

    # Return skills in a consistent order.

    ordered_skills = [
        skill
        for skill in SKILLS_LIST
        if skill in found_skills
    ]

    return ordered_skills


# ==========================================
# 6. COMPARE RESUME WITH JOB DESCRIPTION
# ==========================================

def compare_skills(resume_skills, job_description):

    # Normalize resume skills.

    normalized_resume_skills = {
        normalize_skill(skill)
        for skill in resume_skills
    }

    # Extract required skills from job description.

    required_skills = extract_skills(job_description)

    # Find matching skills.

    matching_skills = [
        skill
        for skill in required_skills
        if skill in normalized_resume_skills
    ]

    # Find missing skills.

    missing_skills = [
        skill
        for skill in required_skills
        if skill not in normalized_resume_skills
    ]

    # Calculate matching percentage.

    if required_skills:

        match_percentage = round(
            len(matching_skills) / len(required_skills) * 100
        )

    else:

        match_percentage = 0

    return {

        "required_skills": required_skills,

        "matching_skills": matching_skills,

        "missing_skills": missing_skills,

        "match_percentage": match_percentage

    }