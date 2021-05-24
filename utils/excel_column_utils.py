from string import ascii_uppercase as _uppercase

letter_hash = {x : _uppercase[x] for x in range(0,26)}

def convert_n_to_xl_col(n):    
    if n == 0:
        return ""
    
    index = ((n - 1) % 26)
    left = convert_n_to_xl_col(n // 27)
    
    return left + letter_hash[index]

def safe_n_to_col(n):
    if n < 1:
        raise Exception("Value must be at least 1")
    if n > 702:
        raise Exception("We can't guarentee safety in these high digits")
    return convert_n_to_xl_col(n)

number_hash = {_uppercase[(n - 1)] : n for n in range(1,27)}

def col_list_convert(col_list, _depth = 0):
    if col_list:
        digit = col_list.pop()
        return col_list_convert(col_list, _depth = _depth + 1) + number_hash[digit] * (26 ** _depth)
    return 0

def convert_col_to_n(col):
    col = list(col)
    return col_list_convert(col)


if __name__ == "__main__":
    print("You've called the excel column utils like a script")