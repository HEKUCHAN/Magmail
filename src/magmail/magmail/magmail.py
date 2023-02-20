import csv
import email
import mailbox
from pathlib import Path
from mailbox import mboxMessage
from email.message import Message
from typing import Any, Union, List, Dict, Callable

from magmail.mail import Mail
from magmail.utils import to_Path
from magmail.static import DEFAULT_AUTO_CLEAN


class Magmail:
    def __init__(
        self,
        mbox_path: Union[str, Path],
        auto_clean: bool = DEFAULT_AUTO_CLEAN,
        filter_contents: Dict[str, str] = {},
        custom_functions: Dict[str, Callable[[Any], Any]] = {},
    ):
        self.mbox_path: Path = to_Path(mbox_path)
        self.auto_clean: bool = auto_clean
        self.filter_contents: Dict[str, str] = filter_contents

        self.emails: List[Mail] = []
        self.add_mail: Callable[[Mail], None] = self.emails.append
        self.custom_functions: Dict[str, Callable[[Any], Any]] = custom_functions

    def __len__(self) -> int:
        return len(self.emails)

    def total(self) -> int:
        return self.__len__()
