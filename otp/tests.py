def unique_and_output(string: str):
    count = 0
    freq = {}
    unique_dict = {}
    for s in string:
        freq[s] = freq.get(s, 0) + 1
        if freq[s] == 1:
            count += 1
            unique_dict[f"value {count}"] = s

    return unique_dict









