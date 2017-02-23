def clear_str(d_string):
    dangerous_symbols = ["\\", "(", ")", "-", "=", "#", "%", "0", '"']
    for sym in dangerous_symbols:
        if sym in d_string:
            return 0
    return 1

def addslashes(d_string):
    if "'" in d_string:
        d_string = d_string.replace("'", "''")
    if len(d_string) > 10:
        d_string = d_string[:10]
    return d_string

