# takes user's task, generates code, validates it, saves it

import os

from generator import ( 
    generate_code, 
    generate_filename, 
    fix_code, 
    generate_project_edits)
from utils import clean_code, create_filename, validate_python_code
from executor import execute_code

from project_reader import read_project
from context_builder import build_context
from editor import apply_edits

def project_mode():
    print("\n" + "=" * 60)
    print("        WEEK 3 - MULTI-FILE CODE AGENT")
    print("=" * 60)

    project_path = input(
        "\nEnter project path (default: sample_project): "
    ).strip()

    if not project_path:
        project_path = "sample_project"

    task = input("\nEnter your coding task: ").strip()

    if not task:
        print("Please enter a task.")
        return

    try:
        # Step 1: Read project
        print("\nReading project files...")

        files = read_project(project_path)

        if not files:
            print("No Python files found.")
            return

        print(f"Found {len(files)} Python files.")

        # Step 2: Build project context
        print("\nBuilding project context...")

        context = build_context(files)

        for item in context:
            print(f"\nFile: {item['file']}")
            print(f"Functions: {item['functions']}")

        # Step 3: Ask LLM for multi-file edits
        print("\nSending project context to LLM...")

        response = generate_project_edits(
            task,
            context
        )

        print("\nLLM generated the following changes:")
        print("-" * 60)
        print(response)
        print("-" * 60)

        # Step 4: Apply edits with backups
        print("\nApplying multi-file edits...")

        success = apply_edits(
            ".",
            response
        )

        if not success:
            print("\nFailed to apply edits.")
            return

        print("\nMulti-file edits applied successfully!")

        # Step 5: Run project test
        test_file = os.path.join(
            project_path,
            "test_calculator.py"
        )

        if os.path.exists(test_file):

            print("\nRunning project tests...")

            with open(test_file, "r", encoding="utf-8") as file:
                test_code = file.read()

            output, error, success = execute_code(
                test_code,
                cwd=project_path
            )

            if success:
                print("\nTests passed!")
                print(output)
            else:
                print("\nTests failed!")
                print(error)

        else:
            print("\nNo test_calculator.py found.")

    except Exception as e:
        print(f"\nError: {e}")


def main():
    print("=" * 60)
    print("     NATURAL LANGUAGE TO CODE GENERATOR")
    print("=" * 60)

    task = input("\nEnter your coding task: ").strip()

    if not task:
        print("Please enter a task.")
        return

    print("\nGenerating code...\n")

    try:
        raw_filename = generate_filename(task)
        filename = create_filename(raw_filename)

        generated_code = generate_code(task)
        # temporary self correction test below............
        # generated_code = (
        #         'def reverse_string(s):\n'
        #         '    return s\n'
        #         '\n'
        #         'assert reverse_string("hello") == "olleh"\n'
        #     )
        generated_code = clean_code(generated_code)

        print("-" * 60)
        print(generated_code)
        print("-" * 60)

        is_valid, message = validate_python_code(generated_code)

        print(f"\n{message}")

        if not is_valid:
            print("Code was not saved because it contains a syntax error.")
            return
        
        # Execute and self-correct up to 3 attempts
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):

            print("\n" + "-" * 60)
            print(f"ATTEMPT {attempt}")
            print("-" * 60)

            output, error, success = execute_code(generated_code)

            if success:
                print("Execution successful!")
                print("\nOutput:")
                print(output)
                break

            print("Execution failed!")
            print("\nError:")
            print(error)

            # If this was the final attempt, stop
            if attempt == max_attempts:
                print("\nMaximum attempts reached.")
                return

            print("\nSending error to LLM for correction...")

            generated_code = fix_code(
                generated_code,
                error
            )

            generated_code = clean_code(generated_code)

            # Validate corrected code before executing it again
            is_valid, message = validate_python_code(generated_code)

            print(f"\n{message}")

            if not is_valid:
                print("Corrected code contains a syntax error.")
                print("The syntax error will be sent to the LLM for another correction.")

                # Replace the error with the new syntax error
                error = message

                generated_code = fix_code(
                    generated_code,
                    error
                )

                generated_code = clean_code(generated_code)


        os.makedirs("generated", exist_ok=True)

        filepath = os.path.join("generated", filename)

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(generated_code)

        print(f"\nCode saved to: {filepath}")

    except Exception as e:
        print(f"\nError: {e}")


# if __name__ == "__main__":
#     main()
if __name__ == "__main__":

    print("\n1. Single-file coding agent") # WEEK 1 & 2
    print("2. Multi-file project agent") # WEEK 3

    choice = input("\nChoose mode: ").strip()

    if choice == "2":
        project_mode()
    else:
        main()