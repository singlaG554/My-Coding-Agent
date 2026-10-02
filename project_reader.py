# reads the files in "sample project" folder

import os

def read_project(project_path):
    files = {}

    for root, dirs, filenames in os.walk(project_path):

        # Ignore Python cache folders
        dirs[:] = [d for d in dirs if d != "__pycache__"]

        for filename in filenames:

            if filename.endswith(".py"):
                file_path = os.path.join(root, filename)

                with open(file_path, "r", encoding="utf-8") as file:
                    files[file_path] = file.read()

    return files

# if __name__ == "__main__":
#     files = read_project("sample_project")

#     for path, content in files.items():
#         print("\n" + "=" * 60)
#         print(path)
#         print("=" * 60)
#         print(content)