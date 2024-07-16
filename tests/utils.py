"""Test utils."""


def concatenate_writes(writes: list) -> str:
    """Concatenate the provided filesystem writes to a single string."""
    result: str = ""
    for entry in writes:
        line = entry[1][0]
        if isinstance(line, bytes):
            line = line.decode("ASCII")
        result = result + line
    return result
