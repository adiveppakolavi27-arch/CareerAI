import os
import time

from google import genai
from dotenv import load_dotenv

load_dotenv()


def analyze_resume_with_gemini(resume_text, job_description=""):

    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "your_api_key_here":
        return {
            "success": False,
            "error": "Gemini API key is not configured."
        }

    # Validate resume
    if not resume_text or not resume_text.strip():
        return {
            "success": False,
            "error": "Resume text is empty."
        }

    try:
        # Initialize Gemini
        client = genai.Client(api_key=api_key)

        # Create prompt
        prompt = f"""
You are an expert resume reviewer and career advisor.

Analyze the following resume carefully.

RESUME:
{resume_text[:12000]}

JOB DESCRIPTION:
{job_description if job_description else "Not provided"}

Provide feedback using these headings:

1. Resume Summary
2. Candidate Strengths
3. Areas to Improve
4. Missing or Recommended Skills
5. Resume Improvement Suggestions
6. Relevant Project Suggestions
7. Overall Feedback

Instructions:
- Give practical and specific suggestions.
- Do not invent qualifications, skills or experience.
- Distinguish existing skills from recommended skills.
- Use simple professional language.
"""

        # Retry Gemini request up to 3 times
        for attempt in range(3):

            try:
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt
                )

                if not response or not response.text:
                    return {
                        "success": False,
                        "error": "Gemini returned an empty response."
                    }

                return {
                    "success": True,
                    "analysis": response.text
                }

            except Exception as error:

                error_message = str(error).upper()

                temporary_error = (
                    "503" in error_message
                    or "429" in error_message
                    or "UNAVAILABLE" in error_message
                    or "RESOURCE_EXHAUSTED" in error_message
                )

                if temporary_error and attempt < 2:

                    wait_time = 2 ** (attempt + 1)

                    print(
                        f"Gemini temporarily unavailable. "
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                else:
                    raise

    except Exception as error:

        print("\n========== GEMINI API ERROR ==========")
        print("Error Type:", type(error).__name__)
        print("Error Details:", str(error))
        print("======================================\n")

        return {
            "success": False,
            "error": (
                "Gemini analysis failed. "
                "Please check the VS Code terminal."
            )
        }