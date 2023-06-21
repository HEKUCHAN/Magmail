import re
import keyword
from pathlib import Path
from typing import Any, List, Union


def get_type_name(object: Any) -> Any:
    return object.__class__.__name__


def to_path(string: Union[str, Path]) -> Path:
    if isinstance(string, str):
        return Path(string)
    elif isinstance(string, Path):
        return string

    raise TypeError(
        f"Unsupported type: '{get_type_name(string)}'. Only 'str' or 'pathlib.Path' are supported."
    )


def to_attribute_name(name: str) -> str:
    name = name.lower()
    name = name.replace("-", "_")

    if not name.isidentifier():
        name = name.replace(r"[^\x00-\x7F]", "")

    if name in keyword.kwlist:
        name = f"h_{name}"

    return name


def atoi(text: str) -> Union[int, str]:
    return int(text) if text.isdigit() else text


def natural_keys(text: str) -> List[Union[int, str]]:
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
    """
    return [atoi(c) for c in re.split(r"(\d+)", text)]
