# communicates with Groq and generates both code and appropriate filename
# Edits multiple files if code in them is not fine

import os, json

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


def generate_project_edits(task, context):
    response = client.chat.completions.create (
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """
                You are a Python coding agent that edits existing projects.

                You will receive:
                1. A coding task.
                2. A summary of the files in the project.

                Your job is to identify which files need to be changed.

                Rules:
                1. Return ONLY valid JSON.
                2. Do NOT use Markdown or code fences.
                3. Return only files that actually need modification.
                4. Each file must contain its COMPLETE updated content.
                5. Preserve all existing functionality unless the task requires a change.
                6. Do not introduce new external libraries or dependencies.
                7. Preserve the existing testing framework and coding style.
                8. Preserve existing import statements exactly unless changing an import is necessary.
                9. Do NOT convert local imports into package imports.
                10. If two Python files are in the same directory and one imports the other,
                    preserve the existing direct import style.
                11. Do NOT add a package name such as "sample_project." to an existing local import.
                12. Do NOT change the project structure.
                13. Only make changes required by the user's task.
                14. Use the project's existing imports and testing approach as the source of truth.
                15. Do not introduce a testing framework that is not present in the project context.
                16. If the project uses plain assert statements and has no pytest import, use plain assert statements.

                IMPORTANT:
                If the existing test file contains:

                from calculator import add, subtract, divide

                you MUST preserve that exact import.

                Do not change it to:

                from sample_project.calculator import add, subtract, divide

                unless the user's task explicitly asks for that import change.

                Use this exact format:

                {
                    "files": [
                        {
                            "path": "relative/path/to/file.py",
                            "content": "complete updated file content"
                        }
                    ]
                }
                """
            },
            {
                "role": "user",
                "content": f"""
                PROJECT CONTEXT:
                {json.dumps(context, indent=2)}

                TASK:
                {task}

                Identify the required files and return their complete updated contents.
                """
            }
                ],
        temperature=0
        )

    return response.choices[0].message.content