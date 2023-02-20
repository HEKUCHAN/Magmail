from pathlib import Path
from mailbox import mboxMessage
from email.message import Message
from typing import Callable, List, Optional, Union

from .header import _Header
from magmail.static import DEFAULT_AUTO_CLEAN


class Mail:
    total_instantiated = 0

    def __init__(
        self,
        message: Union[Message, mboxMessage],
        auto_clean: bool = DEFAULT_AUTO_CLEAN,
        path: Optional[Union[str, Path]] = None,
        custom_clean_function: Optional[Callable[[str], str]] = None,
    ):
        self.path = path
        self.index = Mail.total_instantiated
        Mail.total_instantiated += 1
        self.message: Union[Message, mboxMessage] = message
        self.auto_clean = auto_clean

        self.is_multipart = False

        self.custom_clean_function = custom_clean_function
        self.headers: List[_Header] = []
        self._get_headers()

    def _get_headers(self) -> None:
        for header in self.message.items():
            self.headers.append(
                _Header(
                    header=header,
                    auto_clean=self.auto_clean,
                    custom_clean_function=self.custom_clean_function,
                )
            )
