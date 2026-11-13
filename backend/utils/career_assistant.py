import os
import re
import logging

from datetime import datetime
from zoneinfo import ZoneInfo

from google import genai
from google.genai import types
from dotenv import load_dotenv


# =========================================
# 1. INITIALIZATION
# =========================================

load_dotenv()

logger = logging.getLogger(__name__)


# =========================================
# 2. CONFIGURATION
# =========================================

DEFAULT_MODEL = "gemini-3.6-flash"

TIMEZONE = "Asia/Kolkata"

MAX_QUESTION_LENGTH = 3000
MAX_RESUME_CONTEXT_LENGTH = 4000

MAX_HISTORY_MESSAGES = 8
MAX_HISTORY_MESSAGE_LENGTH = 1500

MAX_OUTPUT_TOKENS = 1024
REQUEST_TIMEOUT_MS = 45000


# =========================================
# 3. CURRENT DATE AND TIME
# =========================================

def get_current_datetime():

    now = datetime.now(ZoneInfo(TIMEZONE))

    return {
        "date": now.strftime("%A, %d %B %Y"),
        "time": now.strftime("%I:%M %p"),
        "day": now.strftime("%A"),
        "timezone": TIMEZONE
    }


# =========================================
# 4. DIRECT DATE AND TIME ANSWERS
# =========================================

def get_direct_datetime_answer(question):

    question = question.lower().strip()

    question = re.sub(r"[?!.,]+$", "", question)

    question = question.replace("what's", "what is")
    question = question.replace("today's", "todays")

    current = get_current_datetime()

    date_patterns = [
        r"what is the date today",
        r"what is todays date",
        r"todays date",
        r"what date is it today",
        r"what date is today",
        r"what is the date",
        r"tell me todays date",
        r"tell me the date today",
        r"can you tell me todays date",
        r"give me todays date"
    ]

    for pattern in date_patterns:

        if re.fullmatch(pattern, question):

            return f"Today's date is {current['date']}."

    day_patterns = [
        r"what day is today",
        r"what day is it today",
        r"which day is today",
        r"what is today",
        r"tell me todays day"
    ]

    for pattern in day_patterns:

        if re.fullmatch(pattern, question):

            return f"Today is {current['day']}."

    time_patterns = [
        r"what time is it",
        r"what time is it now",
        r"what is the current time",
        r"current time",
        r"tell me the time",
        r"what is the time",
        r"what time is now"
    ]

    for pattern in time_patterns:

        if re.fullmatch(pattern, question):

            return (
                f"The current time is {current['time']} "
                f"({current['timezone']})."
            )

    return None


# =========================================
# 5. SYSTEM INSTRUCTIONS
# =========================================

SYSTEM_INSTRUCTIONS = """
You are CareerAI, an intelligent general-purpose AI assistant.

You help users with:

GENERAL KNOWLEDGE:
Science, mathematics, technology, history, geography,
education, business and everyday questions.

PROGRAMMING:
Python, Java, C, C++, JavaScript, HTML, CSS, SQL,
Flask, Django, React, APIs and databases.

ARTIFICIAL INTELLIGENCE:
AI, Machine Learning, Deep Learning, Data Science
and Generative AI.

EDUCATION:
Explain concepts step by step using simple examples.
Do not assume the user has advanced knowledge.

WRITING:
Help with emails, reports, essays, grammar,
summaries, translations and professional communication.

CAREER:
Help with career opportunities, learning roadmaps,
interviews, job preparation and professional skills.

RESUME:
When resume information is provided, analyze skills,
suggest improvements and explain ATS scores.
Never invent qualifications or experience.

IDENTITY:
- Your name is CareerAI.
- Never claim to be ChatGPT.
- Be transparent about your capabilities.

CONVERSATION:
- Understand follow-up questions.
- Understand spelling mistakes and imperfect English.
- Use previous conversation when relevant.
- Avoid repeating information unnecessarily.
- Follow the user's current topic.

CURRENT DATE:
Use the date and time provided with the request.
Timezone: Asia/Kolkata.

LIVE INFORMATION:
You do not automatically have internet access.
Never pretend to browse websites.
Never invent current prices, news, statistics or results.

RESPONSE STYLE:
- Answer the actual question first.
- Keep simple answers short.
- Explain difficult topics clearly.
- Use Markdown for longer answers.
- Use code blocks for programming.
- Give complete code when requested.
- Avoid unnecessary introductions.

You are a general-purpose AI assistant
and a dedicated career expert.
"""


# =========================================
# 6. CLEAN CONVERSATION HISTORY
# =========================================

def clean_history(conversation_history):

    if not isinstance(conversation_history, list):
        return []

    cleaned = []

    for message in conversation_history[-MAX_HISTORY_MESSAGES:]:

        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = message.get("content")

        if role not in ("user", "model"):
            continue

        if not isinstance(content, str):
            continue

        content = content.strip()

        if not content:
            continue

        content = content[:MAX_HISTORY_MESSAGE_LENGTH]

        cleaned.append({
            "role": role,
            "parts": [{"text": content}]
        })

    return cleaned


# =========================================
# 7. MAIN CAREERAI ASSISTANT
# =========================================

def ask_career_assistant(
    question,
    resume_text="",
    conversation_history=None
):

    # Validate question

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
            "error": "Your question exceeds the character limit."
        }

    # Direct date/time answers

    direct_answer = get_direct_datetime_answer(question)

    if direct_answer:

        return {
            "success": True,
            "answer": direct_answer
        }

    # Check API key

    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:

        logger.error("Gemini API key is missing.")

        return {
            "success": False,
            "error": "Gemini API key is not configured."
        }

    # Resume context

    if not isinstance(resume_text, str):
        resume_text = ""

    resume_text = resume_text[:MAX_RESUME_CONTEXT_LENGTH]

    if not resume_text.strip():

        resume_text = "No resume information is available."

    # Date and time

    current = get_current_datetime()

    date_context = f"""
Current date: {current['date']}
Current time: {current['time']}
Timezone: {current['timezone']}
"""

    # Model

    model_name = os.getenv(
        "GEMINI_MODEL",
        DEFAULT_MODEL
    ).strip()

    if not model_name:
        model_name = DEFAULT_MODEL

    # Conversation history

    history = clean_history(conversation_history)

    # Current message

    current_message = f"""
{date_context}

USER RESUME INFORMATION:

{resume_text}

CURRENT QUESTION:

{question}

Answer the current question directly.

Use previous conversation only when relevant.

Do not unnecessarily discuss the resume.

Keep simple answers concise.
"""

    contents = history + [
        {
            "role": "user",
            "parts": [
                {"text": current_message}
            ]
        }
    ]

    # Initialize Gemini with a timeout

    try:

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=REQUEST_TIMEOUT_MS,
                retry_options=types.HttpRetryOptions(
                    attempts=1
                )
            )
        )

    except Exception:

        logger.exception("Gemini initialization failed.")

        return {
            "success": False,
            "error": "Unable to initialize the AI service."
        }

    # Generate response

    try:

        logger.info("CareerAI request started.")

        response = client.models.generate_content(

            model=model_name,

            contents=contents,

            config=types.GenerateContentConfig(

                system_instruction=SYSTEM_INSTRUCTIONS,

                temperature=0.5,

                max_output_tokens=MAX_OUTPUT_TOKENS,

                automatic_continuation=False

            )
        )

        answer = getattr(response, "text", None)

        if not isinstance(answer, str) or not answer.strip():

            logger.error("Gemini returned an empty response.")

            return {
                "success": False,
                "error": "Gemini returned an empty response. Please try again."
            }

        logger.info("CareerAI response generated successfully.")

        return {
            "success": True,
            "answer": answer.strip()
        }

    except Exception as error:

        logger.exception(
            "CareerAI Gemini request failed: %s",
            type(error).__name__
        )

        return {
            "success": False,
            "error": (
                "CareerAI could not generate an answer. "
                "Please try again."
            )
        }