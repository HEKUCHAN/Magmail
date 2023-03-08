from typing import List


from magmail.mail import _Header

class _Headers:
    def __init__(self, headers: List[_Header]=[]):
        self.__headers: List[_Header] = headers.copy()

    def __getitem__(self, key):
        pass

    def add_header(self, header: _Header):
        self.__headers.append(header)
