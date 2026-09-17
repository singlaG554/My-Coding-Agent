def find_maximum(lst):
    if not lst:
        raise ValueError("List is empty")
    max_val = lst[0]
    for item in lst[1:]:
        if item > max_val:
            max_val = item
    return max_val

if __name__ == "__main__":
    try:
        input_str = input("Enter numbers separated by spaces: ").strip()
        numbers = [float(x) if '.' in x else int(x) for x in input_str.split()] if input_str else []
        print("Maximum:", find_maximum(numbers))
    except Exception as e:
        print("Error:", e)