from typing import Any


def rindex(sequence: list[Any], value: Any) -> int:
    return len(sequence) - sequence[::-1].index(value) - 1
