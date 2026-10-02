def add(a, b):
    """Return the sum of a and b."""
    return a + b


def subtract(a, b):
    """Return the difference of a and b."""
    return a - b


def divide(a, b):
    """Return the division of a by b.

    Raises:
        ValueError: If b (the divisor) is zero.
    """
    if b == 0:
        raise ValueError("Divisor cannot be zero")
    return a / b
