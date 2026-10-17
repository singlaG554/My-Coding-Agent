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

def plan_project_changes(task, context):
    import json

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """
                            You are a software engineering planning assistant.

                            You will receive:
                            1. A coding task.
                            2. A summary of an existing Python project.

                            Determine which files actually need to be modified.

                            Rules:
                            1. Return ONLY valid JSON.
                            2. Do not use Markdown or code fences.
                            3. Do not generate code.
                            4. Only select files that are relevant to the task.
                            5. Do not invent files.
                            6. Preserve the existing project structure.
                            7. If the task asks for tests, include the relevant existing test file.
                            8. Use project-relative file paths only.
                            9. Do not return absolute paths.
                            10. If a task requires both implementation and tests,
                                identify both the implementation file and test file.

                            Use exactly this format:

                            {
                                "files_to_modify": [
                                    "Calculator.py",
                                    "tests/test_calculator.py"
                                ],
                                "reason": "short explanation"
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

                            Identify ALL files that need to be modified to fully complete the task.

                            The task is:
                            {task}

                            If the task asks for automated tests, you MUST include the
                            appropriate existing test file.

                            Return project-relative paths only.
                            """
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


def generate_project_edits(task, context, files_to_modify, files):
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
                17. Make the smallest possible change required by the task.
                18. Do NOT rewrite an entire file when a localized change is sufficient.
                19. Preserve all existing classes, functions, imports, UI code, and behavior.
                20. Do NOT rename existing classes or functions.
                21. Do NOT remove existing functionality.
                22. Extend the existing implementation instead of replacing it.
                23. Do NOT recreate the project from scratch.
                24. The existing project structure is the source of truth.
                25. Preserve all existing test cases and add only the tests required by the task.
                26. Do NOT modify files that are not selected by the planner.
                27. Make the smallest possible edit to each selected file.
                28. If adding one function, mapping entry, import, or test is sufficient,
                    modify only that section.
                29. NEVER rewrite an entire file when a localized edit is sufficient.
                30. The returned content must preserve the exact existing source code
                    except for the changes required by the task.
                31. Do not reformat, reorganize, rename, or modernize unrelated code.
                32. Do not replace an existing class with another class.
                33. Do not replace the existing implementation with a newly invented
                    implementation.
                34. For this task, abs() should be added to the existing self.funcs
                    dictionary using "abs": abs.
                35. For tests, preserve all existing tests and add only the required
                    abs() test.

                For example, if the existing code contains:

                self.funcs = {
                    "sin": ...,
                    "cos": ...,
                    "sqrt": math.sqrt,
                    "log": math.log,
                }

                and the task asks to add abs(), the correct modification is:

                self.funcs = {
                    "sin": ...,
                    "cos": ...,
                    "sqrt": math.sqrt,
                    "log": math.log,
                    "abs": abs,
                }

                Do NOT rewrite SafeEvaluator.
                Do NOT rewrite the GUI.
                Do NOT rename classes.
                Do NOT recreate the file.

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

                FILES SELECTED BY PLANNER:
                {json.dumps(files_to_modify, indent=2)}

                ORIGINAL SOURCE CODE:
                {json.dumps(
                    {
                        path: files[path]
                        for path in files_to_modify
                        if path in files
                    },
                    indent=2
                )}

                TASK:
                {task}

                Generate the complete updated contents ONLY for the files selected
                by the planner.

                Use the ORIGINAL SOURCE CODE as the source of truth.

                Make the smallest possible changes required by the task.

                Do not rewrite or recreate the files from scratch.
                Preserve all existing classes, functions, imports, UI code,
                tests, and functionality unless the task specifically requires
                a change.
                """
            }
                ],
        temperature=0
        )

    return response.choices[0].message.content


def fix_project_edits(task, context, files_to_modify, files, test_error):
    import json

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """
                    You are a software debugging assistant.

                    A coding agent modified an existing Python project, but its tests failed.

                    Your job is to correct the generated changes.

                    Rules:
                    1. Return ONLY valid JSON.
                    2. Do not use Markdown or code fences.
                    3. Return complete updated contents only for the selected files.
                    4. Preserve the existing project structure.
                    5. Make the smallest possible correction.
                    6. Do not rewrite unrelated code.
                    7. Preserve all existing functionality.
                    8. Preserve all existing tests.
                    9. Do not remove working functionality.
                    10. Do not introduce new external libraries.
                    11. Use the existing imports and project structure.
                    12. Only modify files listed in files_to_modify.
                    13. Fix the actual test failure rather than hiding or bypassing it.
                    14. Do not modify tests merely to make an incorrect implementation pass.

                    Return exactly:

                    {
                        "files": [
                            {
                                "path": "relative/path.py",
                                "content": "complete file content"
                            }
                        ]
                    }
                    """
            },
            
            {
                "role": "user",
                "content": f"""
                    TASK:
                    {task}

                    FILES TO MODIFY:
                    {json.dumps(files_to_modify, indent=2)}

                    ORIGINAL/CURRENT SOURCE CODE:
                    {json.dumps(
                        {
                            path: files[path]
                            for path in files_to_modify
                            if path in files
                        },
                        indent=2
                        )
                    }

                    TEST FAILURE:
                    {test_error}

                    Fix the implementation so that the tests pass.

                    Return only valid JSON.
                    """
            }
            ],
            temperature=0
    )

    return response.choices[0].message.content