import sys

def is_palindrome(s: str) -> bool:
    return s == s[::-1]

def main():
    if len(sys.argv) > 1:
        input_str = sys.argv[1]
    else:
        input_str = sys.stdin.read().strip()
    result = "Palindrome" if is_palindrome(input_str) else "Not a palindrome"
    print(result)

if __name__ == "__main__":
    main()