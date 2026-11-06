import os
import time
import logging

from google import genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# =========================================
# CONFIGURATION
# =========================================

DEFAULT_MODEL = "gemini-3.6-flash"

MAX_QUESTION_LENGTH = 3000
MAX_RESUME_CONTEXT_LENGTH = 8000

MAX_RETRIES = 3


# =========================================
# CAREER ASSISTANT SYSTEM INSTRUCTIONS
# =========================================

SYSTEM_INSTRUCTIONS = """
You are CareerAI, an intelligent AI career guidance assistant.

Your purpose is to help students and job seekers build
technical skills, understand career opportunities,
prepare for placements and develop professional skills.

YOUR MAIN RESPONSIBILITIES:

1. PYTHON DEVELOPMENT
   - Python fundamentals
   - Intermediate Python
   - Advanced Python
   - Python projects
   - Libraries and frameworks

2. ARTIFICIAL INTELLIGENCE
   - AI fundamentals
   - AI applications
   - Natural Language Processing
   - Generative AI
   - AI projects

3. MACHINE LEARNING
   - Supervised learning
   - Unsupervised learning
   - Model training
   - Model evaluation
   - Machine learning projects

4. DATA SCIENCE
   - Python for data science
   - NumPy and Pandas
   - Data visualization
   - Statistics
   - SQL

5. WEB DEVELOPMENT
   - HTML
   - CSS
   - JavaScript
   - Flask
   - APIs
   - Database integration

6. PLACEMENT PREPARATION
   - Technical interview preparation
   - Python interview questions
   - SQL interview questions
   - Communication skills
   - Resume improvement

7. PROJECT GUIDANCE
   - Beginner projects
   - Intermediate projects
   - Advanced projects
   - Final-year projects
   - Project development steps

ANSWERING GUIDELINES:

1. Explain concepts in beginner-friendly language.
2. Use step-by-step explanations when appropriate.
3. Give practical examples.
4. Recommend useful skills and learning resources.
5. Suggest realistic projects.
6. Explain technical concepts clearly.
7. Do not invent qualifications or experience.
8. Never guarantee jobs, salaries or placement results.
9. Distinguish facts from recommendations.
10. If information is missing, ask for clarification.
11. Keep answers organized with headings and bullet points.
12. Do not pretend to have accessed information that
    you have not actually accessed.

Your goal is to help users learn, improve and plan
their careers through practical guidance.
"""


# =========================================
# TEMPORARY ERROR DETECTION
# =========================================

def is_temporary_error(error):

    error_message = str(error).upper()

    temporary_keywords = [

        "429",
        "500",
        "502",
        "503",
        "504",
        "UNAVAILABLE",
        "RESOURCE_EXHAUSTED",
        "INTERNAL",
        "TIMEOUT",
        "CONNECTION"

    ]

    return any(
        keyword in error_message
        for keyword in temporary_keywords
    )


# =========================================
# MAIN CAREER ASSISTANT FUNCTION
# =========================================

def ask_career_assistant(question, resume_text=""):

    # -------------------------------------
    # CHECK API KEY
    # -------------------------------------

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "your_api_key_here":

        return {

            "success": False,

            "error": "Gemini API key is not configured."

        }

    # -------------------------------------
    # VALIDATE QUESTION
    # -------------------------------------

    if not isinstance(question, str):

        return {

            "success": False,

            "error": "Invalid question format."

        }

    question = question.strip()

    if not question:

        return {

            "success": False,

            "error": "Please enter your question."

        }

    if len(question) > MAX_QUESTION_LENGTH:

        return {

            "success": False,

            "error": "Your question exceeds the 3000 character limit."

        }

    # -------------------------------------
    # VALIDATE RESUME CONTEXT
    # -------------------------------------

    if not isinstance(resume_text, str):

        resume_text = ""

    resume_text = resume_text[:MAX_RESUME_CONTEXT_LENGTH]

    if not resume_text.strip():

        resume_text = "No resume information is available."

    # -------------------------------------
    # GET MODEL CONFIGURATION
    # -------------------------------------

    model_name = os.getenv(
        "GEMINI_MODEL",
        DEFAULT_MODEL
    )

    # -------------------------------------
    # CREATE PROMPT
    # -------------------------------------

    prompt = f"""
{SYSTEM_INSTRUCTIONS}

=========================================
USER RESUME INFORMATION
=========================================

{resume_text}

=========================================
USER QUESTION
=========================================

{question}

=========================================
RESPONSE REQUIREMENTS
=========================================

Provide a useful and accurate answer.

When explaining technical topics:

- Start with a simple explanation.
- Explain important concepts.
- Give practical examples.
- Include code examples when requested.
- Explain the code step by step when useful.

When creating learning roadmaps:

- Divide learning into phases.
- Include beginner, intermediate and advanced topics.
- Suggest practical exercises.
- Recommend projects.
- Explain what to learn next.

When providing career recommendations:

- Consider the available resume information.
- Identify relevant skills.
- Suggest possible improvements.
- Avoid unsupported assumptions.

Keep the answer clear, organized and practical.
"""

    # -------------------------------------
    # INITIALIZE GEMINI CLIENT
    # -------------------------------------

    try:

        client = genai.Client(
            api_key=api_key
        )

    except Exception:

        logger.exception(
            "Gemini client initialization failed."
        )

        return {

            "success": False,

            "error": "Unable to initialize the AI service."

        }

    # -------------------------------------
    # GENERATE AI RESPONSE
    # -------------------------------------

    for attempt in range(MAX_RETRIES):

        try:

            response = client.models.generate_content(

                model=model_name,

                contents=prompt

            )

            if response is None:

                return {

                    "success": False,

                    "error": "Gemini returned no response."

                }

            answer = response.text

            if not answer or not answer.strip():

                return {

                    "success": False,

                    "error": "Gemini returned an empty response."

                }

            return {

                "success": True,

                "answer": answer.strip()

            }

        except Exception as error:

            logger.warning(
                "Gemini request failed on attempt %s: %s",
                attempt + 1,
                type(error).__name__
            )

            if (
                is_temporary_error(error)
                and attempt < MAX_RETRIES - 1
            ):

                wait_time = 2 ** (attempt + 1)

                time.sleep(wait_time)

                continue

            logger.exception(
                "Career Assistant API request failed."
            )

            return {

                "success": False,

                "error": (
                    "Career Assistant is temporarily unavailable. "
                    "Please try again later."
                )

            }

    return {

        "success": False,

        "error": "Unable to generate a response."

    }