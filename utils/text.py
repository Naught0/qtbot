def truncate(s: str, length: int) -> str:
    """Truncates & ellipsizes a string at the given character count
    String length will never exceed the length arg
        len(return) <= length

    Args:
        s (str)
        length (int): Desired output length in chars minus the elipsis character

    Returns:
        str
    """
    if len(s) > length:
        return f"{s[:length - 1]}…"
    else:
        return s


def truncate_word(s: str, length: int) -> str:
    """Truncates & ellipsizes a string based on word count

    Args:
        s (str)
        length (int): Number of words to allow in the string

    Returns:
        str
    """
    words = s.split(" ")
    if len(words) <= length:
        return s
    else:
        return f'{" ".join(words[:length])} …'
