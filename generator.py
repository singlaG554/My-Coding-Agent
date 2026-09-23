# communicates with Groq and generates both code and appropriate filename

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

# fixes the code if execution of generated code, 
# by agent fails to produce required output
def fix_code(code, error):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """
You are a Python code debugging assistant.

Your job is to fix Python code that failed during execution.

Rules:
1. Return ONLY valid Python code.
2. Do NOT return Markdown.
3. Do NOT use ```python or ``` code fences.
4. Do NOT provide explanations.
5. Fix the code based on the provided error.
6. Preserve the original task and intended behavior.
7. The corrected code must be directly executable as a Python file.
"""
            },
            {
                "role": "user",
                "content": f"""
The following Python code failed during execution.

CODE:
{code}

ERROR:
{error}

Fix the code and return ONLY the corrected Python code.
"""
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content
