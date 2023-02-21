from pathlib import Path
from mailbox import mboxMessage
from email.message import Message
from typing import Any, Callable, Dict, List, Optional, Union

from magmail.utils import to_attribute_name

from .body import _Body
from .header import _Header
from .custom import _CustomsFunctions
from magmail.magmail.filter import _Filter
from magmail.static import (
    DEFAULT_AUTO_CLEAN,
    DEFAULT_CUSTOM_CLEAN_FUNCTIONS_DICT,
    FILTER_CONTENTS_TYPE,
)


class Mail:
    total_instantiated = 0

    def __init__(
        self,
        message: Union[Message, mboxMessage],
        auto_clean: bool = DEFAULT_AUTO_CLEAN,
        path: Optional[Union[str, Path]] = None,
        filters: Dict[str, FILTER_CONTENTS_TYPE] = {},
        custom_clean_functions: Dict[
            str, Optional[Callable[[Any], Any]]
        ] = DEFAULT_CUSTOM_CLEAN_FUNCTIONS_DICT.copy(),
    ):
        self.path = path
        self.index = Mail.total_instantiated
        Mail.total_instantiated += 1
        self.message: Union[Message, mboxMessage] = message
        self.auto_clean = auto_clean

        self.has_multipart: bool = False

        self.custom_clean_function: _CustomsFunctions = _CustomsFunctions(
            custom_clean_functions
        )
        self.filters = _Filter(filters)
        self.headers: List[_Header] = []
        self.add_header: Callable[[_Header], None] = self.headers.append
        self._get_headers()
        self._get_body()

    def __getitem__(self, key: str) -> Optional[str]:
        key = to_attribute_name(key)
        if hasattr(self, key):
            return getattr(self, key)
        else:
            return None

    def _get_headers(self) -> None:
        for header in self.message.items():
            custom_clean_function: Optional[Callable[[str], str]] = None

            if self.custom_clean_function.is_has("all"):
                custom_clean_function = self.custom_clean_function["all"]
            elif self.custom_clean_function.is_has("headers"):
                custom_clean_function = self.custom_clean_function["headers"]

            self.add_header(
                _Header(
                    header=header,
                    auto_clean=self.auto_clean,
                    custom_clean_function=custom_clean_function,
                )
            )

        for field, body in self.headers:
            if not hasattr(self, to_attribute_name(field)):
                setattr(self, to_attribute_name(field), body)

    def _get_body(self) -> None:
        custom_clean_function: Optional[Callable[[str], str]] = None

        if self.custom_clean_function.is_has("all"):
            custom_clean_function = self.custom_clean_function["all"]
        elif self.custom_clean_function.is_has("body"):
            custom_clean_function = self.custom_clean_function["body"]

        self._body: _Body = _Body(
            self.message,
            auto_clean=self.auto_clean,
            filters=self.filters.filter_dict.copy(),
            custom_clean_function=custom_clean_function,
        )
