from pathlib import Path
from typing import Union


class Utils:
    @classmethod
    def str_to_Path(cls, string: Union[Path, str]) -> Path:
        if not isinstance(string, Path):
            return Path(string)
        return string
