def factorial(n):
    """Calculate the factorial of a non-negative integer n."""
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a non-negative integer")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

# Example usage:
if __name__ == "__main__":
    print(factorial(5))  # Output: 120