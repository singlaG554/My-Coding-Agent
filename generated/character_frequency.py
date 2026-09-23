def char_frequency(s: str) -> dict:
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    return freq

assert char_frequency("aab") == {"a": 2, "b": 1}