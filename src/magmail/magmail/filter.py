from typing import Any, Dict


class _Filter:
    def __init__(self, filter_dict: Dict[str, Any]) -> None:
        self.filter_dict: Dict[str, Any] = {
            key: value for key, value in filter_dict.items() if value is not None
        }
        for name, value in filter_dict.items():
            setattr(self, name, value)

    def __getitem__(self, key: str) -> Any:
        if key in self.filter_dict:
            return self.filter_dict[key]
        raise IndexError

    def is_has(self, key: str) -> bool:
        return key in self.filter_dicts
