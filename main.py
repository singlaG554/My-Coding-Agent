# takes user's task, generates code, validates it, saves it

import os

from generator import generate_code, generate_filename, fix_code
from utils import clean_code, create_filename, validate_python_code
from executor import execute_code
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


if __name__ == "__main__":
    main()