def find_max(numbers):
    if not numbers:
        raise ValueError("The list is empty")
    max_val = numbers[0]
    for num in numbers[1:]:
        if num > max_val:
            max_val = num
    return max_val

assert find_max([3, 7, 2, 9, 5]) == 9