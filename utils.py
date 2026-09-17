import re
import ast 

def clean_code(code):
    code = code.strip()

    # Remove ```python ... ``` or ``` ... ```
    code = re.sub(r"^```python\s*", "", code, flags=re.IGNORECASE)
    code = re.sub(r"^```\s*", "", code)
    code = re.sub(r"\s*```$", "", code)

    return code.strip()


def create_filename(filename):
    filename = filename.lower().strip()

    # Remove .py if the model accidentally included it
    if filename.endswith(".py"):
        filename = filename[:-3]

    # Replace anything that isn't a letter, number or underscore
    filename = re.sub(r"[^a-z0-9_]+", "_", filename)

    # Remove repeated underscores
    filename = re.sub(r"_+", "_", filename)

    # Remove underscores from beginning/end
    filename = filename.strip("_")

    # Fallback
    if not filename:
        filename = "generated_code"

    return filename + ".py"


def validate_python_code(code):
    try:
        ast.parse(code) #checks whether text is valid python syntax
        return True, "Syntax validation passed"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"