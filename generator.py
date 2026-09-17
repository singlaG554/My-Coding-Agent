import os

from dotenv import load_dotenv
from groq import Groq

from prompt import SYSTEM_PROMPT

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")


client = Groq(api_key=api_key)
MODEL = "openai/gpt-oss-120b"

def generate_code(task):
    response = client.chat.completions.create(
        model = MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": task
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


def generate_filename(task):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """
                            You generate filenames for Python programs.

                            Given a programming task, return ONLY a short, descriptive filename.

                            Rules:
                            1. Return only the filename without .py.
                            2. Use lowercase letters.
                            3. Use underscores between words.
                            4. Do not use spaces.
                            5. Do not use special characters.
                            6. Keep it concise, preferably 2 to 5 words.
                            7. The filename should describe the main purpose of the program.
                            8. Do not include words like "program", "solution", "code", or "python"
                            unless they are genuinely part of the task.
                            """
            },
            {
                "role": "user",
                "content": task
            }
        ],
        temperature=0
    )

    filename = response.choices[0].message.content.strip()

    return filename