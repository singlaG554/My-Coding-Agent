def bubble_sort(arr):
    """
    Sorts a list in ascending order using the bubble sort algorithm.
    The sorting is done in-place and the same list is returned.
    """
    n = len(arr)
    for i in range(n):
        # Track if any swap happens; if not, the list is already sorted
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

# Example usage
if __name__ == "__main__":
    sample = [64, 34, 25, 12, 22, 11, 90]
    print("Original list:", sample)
    sorted_list = bubble_sort(sample)
    print("Sorted list:", sorted_list)