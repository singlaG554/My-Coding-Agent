def sort_dict_by_values(d, reverse=False):
    """
    Return a new dictionary sorted by its values.

    Parameters:
        d (dict): The dictionary to sort.
        reverse (bool): If True, sort in descending order.

    Returns:
        dict: A dictionary with items sorted by value.
    """
    return dict(sorted(d.items(), key=lambda item: item[1], reverse=reverse))