from pathlib import Path
from typing import Union


def to_Path(string: Union[str, Path]) -> Path:
    if isinstance(string, str):
        return Path(string)
    return string
