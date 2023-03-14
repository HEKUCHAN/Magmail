from pathlib import Path
from mailbox import mboxMessage
from email.message import Message
from email.utils import parsedate_to_datetime
from typing import Any, Callable, Dict, List, Optional, Union


from .body import _Body
from .header import _Header
from .headers import _Headers
from magmail.magmail.filter import _Filter
from magmail.utils import to_attribute_name
from magmail.static import (
    DEFAULT_AUTO_CLEAN,
    FILTER_CONTENTS_TYPE,
    CUSTOM_FUNCTIONS_DICT,
    CUSTOM_FUNCTIONS_DICT_TYPE,
    CUSTOM_FUNCTIONS_ROOT_DICT_TYPE,
)


class Mail:
    total_instantiated = 0
    Dict[str, Dict[str, Optional[Callable[[Any], Any]]]]
    Dict[str, Dict[str, Callable[[Any], Any]]]
    def __init__(
        self,
        message: Union[Message, mboxMessage],
        auto_clean: bool = DEFAULT_AUTO_CLEAN,
        path: Optional[Union[str, Path]] = None,
        filters: Dict[str, FILTER_CONTENTS_TYPE] = {},
        custom_functions: CUSTOM_FUNCTIONS_ROOT_DICT_TYPE  = CUSTOM_FUNCTIONS_DICT.copy(),
    ):
        self.path = path
        self.index = Mail.total_instantiated
        Mail.total_instantiated += 1
        self.message: Union[Message, mboxMessage] = message
        self.auto_clean = auto_clean

        self.has_multipart: bool = False

        self.custom_functions: CUSTOM_FUNCTIONS_ROOT_DICT_TYPE = custom_functions
        self.filters = _Filter(filters)
        self.headers: _Headers = _Headers(
            custom_functions=self.custom_functions["headers"].copy()
        )
        self.add_header: Callable[[_Header], None] = self.headers.add_header

        self._get_headers()
        self._get_body()

        self.body = self._body.body
        self.body_html = self._body.body_html
        self.body_plain = self._body.body_plain

    def __getitem__(self, key: str) -> Optional[Any]:
        key = to_attribute_name(key)
        return getattr(self, key ,None)

    def _get_headers(self) -> None:
        for header in self.message.items():
            custom_clean_function: Optional[Callable[[str], str]] = None

            if "clean_functions" in self.custom_functions:
                if "all" in self.custom_functions["clean_functions"]:
                    custom_clean_function = self.custom_functions["clean_functions"][
                        "all"
                    ]
                elif "headers" in self.custom_functions["clean_functions"]:
                    custom_clean_function = self.custom_functions["clean_functions"][
                        "headers"
                    ]

            self.add_header(
                _Header(
                    header=header,
                    auto_clean=self.auto_clean,
                    custom_clean_function=custom_clean_function,
                )
            )

    def _get_body(self) -> None:
        custom_clean_function: Optional[Callable[[str], str]] = None

        if "clean_functions" in self.custom_functions:
            if "all" in self.custom_functions["clean_functions"]:
                custom_clean_function = self.custom_functions["clean_functions"]["all"]
            elif "body" in self.custom_functions["clean_functions"]:
                custom_clean_function = self.custom_functions["clean_functions"]["body"]

        self._body: _Body = _Body(
            self.message,
            auto_clean=self.auto_clean,
            filters=self.filters.filter_dict.copy(),
            custom_clean_function=custom_clean_function,
        )
