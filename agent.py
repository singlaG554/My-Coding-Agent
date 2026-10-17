# responsible for only high level orchestration

import argparse, json, os

from project_reader import read_project
from context_builder import build_context
from generator import (
            plan_project_changes, 
            generate_project_edits,
            fix_project_edits)
from editor import apply_edits
from executor import run_tests


def main():
    parser = argparse.ArgumentParser(
        description="AI Coding Agent"
    )

    parser.add_argument(
        "--project",
        required=True,
        help="Path to the target project"
    )

    parser.add_argument(
        "--task",
        required=True,
        help="Coding task for the agent"
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("             AI CODING AGENT")
    print("=" * 60)

    print(f"\nProject: {args.project}")
    print(f"Task: {args.task}")

    # Step 1: Read project files
    print("\nReading project files...")

    files = read_project(args.project)

    relative_files = {}

    for path, content in files.items():
        relative_path = os.path.relpath(path, args.project)
        relative_path = os.path.normcase(relative_path).replace("\\", "/")
        relative_files[relative_path] = content

    print("\nAvailable source files:")
    for path in relative_files:
        print(" -", path)

    if not files:
        print("No Python files found.")
        return

    print(f"Found {len(files)} Python files.")

    # Step 2: Build project context
    print("\nBuilding project context...")

    context = build_context(files)

    for item in context:
        print("\nFile:", item["file"])
        print("Functions:", item["functions"])
        print("Imports:", item["imports"])
        
    print("\nPlanning changes...")
    plan = plan_project_changes(
        args.task,
        context
        )

    print("\nLLM Plan:")
    print("-" * 60)
    print(plan)

    plan_data = json.loads(plan)

    files_to_modify = plan_data.get("files_to_modify", [])
    files_to_modify = [
            os.path.normcase(path).replace("\\", "/")
            for path in files_to_modify
        ]

    if not files_to_modify:
        print("\nNo files selected for modification.")
        return

    print("\nFiles selected for modification:")

    for file_path in files_to_modify:
        print(" -", file_path)


    print("\nGenerating code changes...")


    files_to_modify = [
        path.replace("\\", "/")
        for path in files_to_modify
    ]


    print("\nOriginal source files being provided to LLM:")

    for path in files_to_modify:
        print("\nFILE:", path)

        normalized_path = os.path.normcase(path).replace("\\", "/")

        if normalized_path in relative_files:
            print(relative_files[normalized_path][:1000])
        else:
            print("SOURCE NOT FOUND")


    response = generate_project_edits(
        args.task,
        context,
        files_to_modify,
        relative_files
    )

    print("\nGenerated changes:")
    print("-" * 60)
    print(response)
    print("-" * 60)
    print("\nApplying changes...")

    try:
        apply_edits(args.project, response)
        # print("\nRunning tests...")

        # test_result = run_tests(args.project)
        # print("\nTest Output:")
        # print("-" * 60)
        # print(test_result["stdout"])

        # if test_result["stderr"]:
        #     print(test_result["stderr"])

        # print("-" * 60)

        # if test_result["success"]:
        #     print("\nSUCCESS: All tests passed.")
        # else:
        #     print("\nFAILURE: Tests failed.")

        print("\nRunning tests...")

        MAX_ATTEMPTS = 3
        attempt = 1

        while attempt <= MAX_ATTEMPTS:

            print(f"\nTest attempt {attempt}/{MAX_ATTEMPTS}")

            test_result = run_tests(args.project)

            print("\nTest Output:")
            print("-" * 60)

            if test_result["stdout"]:
                print(test_result["stdout"])

            if test_result["stderr"]:
                print(test_result["stderr"])

            print("-" * 60)

            if test_result["success"]:
                print("\nSUCCESS: All tests passed.")
                break

            print("\nTests failed.")

            if attempt == MAX_ATTEMPTS:
                print("\nMaximum retry limit reached.")
                print("Agent could not automatically fix the project.")
                return

            print("\nSending test failure to LLM for self-correction...")

            current_files = read_project(args.project)

            correction = fix_project_edits(
                args.task,
                context,
                files_to_modify,
                {
                    os.path.relpath(path, args.project)
                        .replace("\\", "/"): content
                    for path, content in current_files.items()
                },
                test_result["stdout"] + "\n" + test_result["stderr"]
            )

            print("\nGenerated correction:")
            print("-" * 60)
            print(correction)
            print("-" * 60)

            print("\nApplying correction...")

            try:
                apply_edits(args.project, correction)
                print("Correction applied successfully.")
            except Exception as e:
                print("Failed to apply correction:")
                print(e)
                return

            attempt += 1

        print("Changes applied successfully.")
    except Exception as e:
        print("Failed to apply changes:")
        print(e)
        return


if __name__ == "__main__":
    main()