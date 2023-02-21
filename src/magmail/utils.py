from pathlib import Path
from typing import Union


def to_Path(string: Union[str, Path]) -> Path:
    if isinstance(string, str):
        return Path(string)
    return string


def to_attribute_name(name: str) -> str:
    name = name.lower()
    name = name.replace("-", "_")

    if name.isidentifier():
        return str
    else:
        name = name.replace(r"[^\x00-\x7F]", "")
        return name
