from typing import List, Optional

from magmail.static import CUSTOM_FUNCTIONS_DICT_TYPE, CHANGE_HEADER_TYPE_FUNCTIONS
from magmail.utils import to_attribute_name


from .mail import _Header

class _Headers:
    def __init__(
        self,
        headers: List[_Header]=[],
        custom_functions: Optional[CUSTOM_FUNCTIONS_DICT_TYPE] = None,
    ):
        self.__headers: List[_Header] = headers.copy()
        self.__custom_functions: Optional[CUSTOM_FUNCTIONS_DICT_TYPE] = custom_functions

    def add_header(self, header: _Header):
        self.__custom_headers(header)

        key = to_attribute_name(header.field)
        setattr(self, key, header.body)

        return self.__headers.append(header)

    def search_header(self, key):
        for field, body in self.__headers:
            if field == key:
                return body
        return None

    def get_header(self, key):
        for i, header in enumerate(self.__headers):
            if header.field == key:
                return self.__headers[i]
        return None
    
    def has_header(self, key):
        return self.search_header(key) is not None

    def set_header(self, key, value):
        for i, header in enumerate(self.__headers):
            if header.field == key:
                self.__headers[i] = value
        raise AttributeError(key)

    def __custom_headers(self, header):
        def change_type(function_dict, header):
            if header.field in function_dict:
                func = function_dict[header.field]
                header.body = func(header.body)
    
        change_type(CHANGE_HEADER_TYPE_FUNCTIONS, header)
        change_type(self.__custom_functions, header)

    def __getitem__(self, key):
        if isinstance(key, str):
            if self.has_header(key):
                return self.search_header(key)
            else:
                raise AttributeError(key)
        else:
            return self.__headers[key]

    def __setitem__(self, key, value):
        for i, header in enumerate(self.__headers):
            if header.field == key:
               self.__headers[i] = value

    def __dict__(self):
        return {field:body for field, body in self.__headers}
    
    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i < len(self.__headers):
            value = self.__headers[self.i]
            self.i += 1
            return (value.field, value.body)

        delattr(self, "i")
        raise StopIteration
