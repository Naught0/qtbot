def truncate(s: str, length: int) -> str:
    if len(s) > length:
        return f"{s[:length - 1]}…"
    else:
        return s
