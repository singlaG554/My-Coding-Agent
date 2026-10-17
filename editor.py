# backs up the files before making changes into it
# modify + backup files

import os
import json
import shutil


def backup_file(file_path):
    backup_path = file_path + ".bak"

    shutil.copy2(file_path, backup_path)

    return backup_path


def apply_edits(project_path, response):
    try:
        data = json.loads(response)
    except json.JSONDecodeError as e:
        print("Invalid JSON returned by LLM.")
        print(e)
        return False

    files = data.get("files", [])

    if not files:
        print("No files were provided for editing.")
        return False

    for file_data in files:
        relative_path = file_data["path"]
        content = file_data["content"]

        # file_path = os.path.join(project_path, relative_path)
        if relative_path.startswith(project_path):
            file_path = relative_path
        else:
            file_path = os.path.join(project_path, relative_path)


        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False

        backup_path = backup_file(file_path)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

        print(f"Updated: {file_path}")
        print(f"Backup:  {backup_path}")

    return True