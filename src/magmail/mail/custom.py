from typing import Any, Callable, Dict, Optional


from magmail.utils import to_attribute_name


class _CustomsFunctions:
    def __init__(self, functions_dict: Dict[str, Optional[Callable[[Any], Any]]]):
        self.functions_dict = {
            key: value for key, value in functions_dict.items() if value is not None
        }
        for name, func in functions_dict.items():
            setattr(self, name, func)

            if not hasattr(self, to_attribute_name(name)):
                setattr(self, to_attribute_name(name), func)

    def __getitem__(self, key: str) -> Callable[[Any], Any]:
        if key in self.functions_dict:
            return self.functions_dict[key]
        raise IndexError

    def is_has(self, key: str) -> bool:
        return key in self.functions_dict
