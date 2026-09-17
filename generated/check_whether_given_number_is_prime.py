import sys
import math

def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    w = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += w
        w = 6 - w
    return True

if __name__ == "__main__":
    data = sys.stdin.read().strip().split()
    if not data:
        sys.exit()
    try:
        number = int(data[0])
    except ValueError:
        print("Invalid input")
        sys.exit()
    print("Prime" if is_prime(number) else "Not prime")