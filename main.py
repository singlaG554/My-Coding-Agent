import os

from generator import generate_code, generate_filename
from utils import clean_code, create_filename, validate_python_code
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

        generated_code = clean_code(generated_code)

        print("-" * 60)
        print(generated_code)
        print("-" * 60)

        is_valid, message = validate_python_code(generated_code)

        print(f"\n{message}")

        if not is_valid:
            print("Code was not saved because it contains a syntax error.")
            return

        os.makedirs("generated", exist_ok=True)

        filepath = os.path.join("generated", filename)

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(generated_code)

        print(f"\nCode saved to: {filepath}")

    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()