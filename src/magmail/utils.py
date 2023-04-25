import keyword
from pathlib import Path
from typing import Any, Optional, Union

def get_type_name(object: Any) -> Optional[str]:
    return object.__class__.__name__

def to_path(string: Union[str, Path]) -> Path:
    if isinstance(string, str):
        return Path(string)
    elif isinstance(string, Path):
        return string

    raise TypeError(
        f"unsupported type(s) `{get_type_name(string)}`, Supported Only `str` or `pathlib.Path`."
    )


def to_attribute_name(name: str) -> str:
    name = name.lower()
    name = name.replace("-", "_")

    if not name.isidentifier():
        name = name.replace(r"[^\x00-\x7F]", "")

    if name in keyword.kwlist:
        name = f"h_{name}"

    return name
