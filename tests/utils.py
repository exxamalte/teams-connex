"""Test utils."""


def concatenate_writes(writes: list) -> str:
    """Concatenate the provided filesystem writes to a single string."""
    result: str = ""
    for entry in writes:
        result = result + entry[1][0].decode("ASCII")
    return result
