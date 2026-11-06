import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

if not api_key:
    print("ERROR: Gemini API key not found.")
    exit()

try:
    client = genai.Client(api_key=api_key)

    print("Testing Gemini model:", model)

    response = client.models.generate_content(
        model=model,
        contents="Explain Python in three simple sentences."
    )

    print("\nSUCCESS! Gemini is working.")
    print(response.text)

except Exception as e:
    print("\nGEMINI ERROR:")
    print(e)