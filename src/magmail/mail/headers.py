from typing import Any, Dict, List, Optional, Tuple, Union, TypeVar

from magmail.static import CUSTOM_FUNCTIONS_DICT_TYPE, CHANGE_HEADER_TYPE_FUNCTIONS
from magmail.utils import to_attribute_name


from .mail import _Header


THeaders = TypeVar("THeaders", bound="_Headers")


class _Headers:
    def __init__(
        self,
        headers: List[_Header] = [],
        custom_functions: Optional[CUSTOM_FUNCTIONS_DICT_TYPE] = None,
    ):
        self.__headers: List[_Header] = headers.copy()
        self.__custom_functions: Optional[CUSTOM_FUNCTIONS_DICT_TYPE] = custom_functions
        self.__set_attribute()

    def add_header(self, header: _Header) -> None:
        self.__custom_headers(header)

        key = to_attribute_name(header.field)
        setattr(self, key, header.body)

        return self.__headers.append(header)

    def __set_attribute(self) -> None:
        for header in self.__headers:
            setattr(self, to_attribute_name(header.field), header.body)

    def search_header(self, key: str) -> Optional[str]:
        for field, body in self.__headers:
            if field == key:
                return body
        return None

    def get_header(self, key: str) -> Optional[_Header]:
        for i, header in enumerate(self.__headers):
            if header.field == key:
                return self.__headers[i]
        return None

    def has_header(self, key: str) -> bool:
        return self.search_header(key) is not None

    def set_header(self, key: str, value: Any) -> None:
        for i, header in enumerate(self.__headers):
            if header.field == key:
                self.__headers[i] = value
                self.__set_attribute()
                return
        raise AttributeError(key)

    def __custom_headers(self, header: _Header) -> None:
        def change_type(
            function_dict: Optional[CUSTOM_FUNCTIONS_DICT_TYPE], header: _Header
        ) -> None:
            if function_dict is not None and header.field in function_dict:
                func = function_dict[header.field]
                if func is not None:
                    header.body = func(header.body)

        change_type(CHANGE_HEADER_TYPE_FUNCTIONS, header)
        change_type(self.__custom_functions, header)

    def __getitem__(self, key: str) -> Union[Optional[str], _Header]:
        if isinstance(key, str):
            if self.has_header(key):
                return self.search_header(key)
            else:
                raise AttributeError(key)
        else:
            return self.__headers[key]

    def __setitem__(self, key: str, value: Any) -> None:
        for i, header in enumerate(self.__headers):
            if header.field == key:
                self.__headers[i] = value
                self.__set_attribute()

    @property
    def __dict__(self) -> Dict[str, Any]:
        return {field: body for field, body in self.__headers}

    @__dict__.setter
    def __dict__(self, value: Dict[str, Any]) -> None:
        self.__dict__ = value
        self.__set_attribute()

    def __iter__(self: THeaders) -> THeaders:
        self.i = 0
        return self

    def __next__(self) -> Tuple[str, Union[Any, str]]:
        if self.i < len(self.__headers):
            value = self.__headers[self.i]
            self.i += 1
            return (value.field, value.body)

        delattr(self, "i")
        raise StopIteration
