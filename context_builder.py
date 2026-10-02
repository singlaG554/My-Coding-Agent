# helps to summarize the files in "sample project" folder

import ast

# def summarize_file(path, content):
#     try:
#         tree = ast.parse(content)
#     except SyntaxError:
#         return {
#             "file": path,
#             "functions": [],
#             "purpose": "Could not parse file."
#         }

#     functions = []

#     for node in ast.walk(tree):
#         if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
#             functions.append(node.name)

#     return {
#         "file": path,
#         "functions": functions,
#         "purpose": "Python source file containing: "
#                    + ", ".join(functions)
#                    if functions
#                    else "Python source file."
#     }

def summarize_file(path, content):
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return {
            "file": path,
            "functions": [],
            "imports": [],
            "purpose": "Could not parse file."
        }

    functions = []
    imports = []

    for node in ast.walk(tree):

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)

        elif isinstance(node, ast.Import):
            for name in node.names:
                imports.append(name.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""

            if module:
                imports.append(module)

    if functions:
        purpose = (
            "Python source file containing: "
            + ", ".join(functions)
        )
    else:
        purpose = "Python source file."

    return {
        "file": path,
        "functions": functions,
        "imports": imports,
        "purpose": purpose
    }

def build_context(files):
    context = []

    for path, content in files.items():
        context.append(
            summarize_file(path, content)
        )

    return context


if __name__ == "__main__":
    from project_reader import read_project

    files = read_project("sample_project")
    context = build_context(files)

    for item in context:
        print("\nFile:", item["file"])
        print("Functions:", item["functions"])
        print("Purpose:", item["purpose"])