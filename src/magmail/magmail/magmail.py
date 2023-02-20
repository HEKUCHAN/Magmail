import csv
import email
import mailbox
from pathlib import Path
from mailbox import mboxMessage
from email.message import Message
from typing import Any, Optional, Union, List, Dict, Callable

from magmail.mail import Mail
from magmail.utils import to_Path
from magmail.static import DEFAULT_AUTO_CLEAN, DEFAULT_CUSTOM_FUNCTIONS_DICT


class Magmail:
    def __init__(
        self,
        mbox_path: Union[str, Path],
        auto_clean: bool = DEFAULT_AUTO_CLEAN,
        filter_contents: Dict[str, str] = {},
        custom_functions: Dict[
            str, Callable[[Any], Any]
        ] = DEFAULT_CUSTOM_FUNCTIONS_DICT,
    ):
        self.mbox_path: Path = to_Path(mbox_path)
        self.auto_clean: bool = auto_clean
        self.filter_contents: Dict[str, str] = filter_contents

        self.emails: List[Mail] = []
        self.add_mail: Callable[[Mail], None] = self.emails.append
        self.custom_functions: Dict[str, Callable[[Any], Any]] = custom_functions

        self._parse()

    def __len__(self) -> int:
        return len(self.emails)

    def total(self) -> int:
        return self.__len__()

    def _parse(self) -> None:
        self.add_mbox(self.mbox_path)

    def _create_mail(
        self,
        message: Union[Message, mboxMessage],
        path: Optional[Union[str, Path]] = None,
    ) -> Mail:
        custom_function: Optional[Callable[[str], str]] = None

        if self.custom_functions["all"] is not None:
            custom_function = self.custom_functions["clean"]
        elif self.custom_functions["headers"] is not None:
            custom_function = self.custom_functions["headers"]

        return Mail(
            message=message,
            path=path,
            auto_clean=self.auto_clean,
            custom_clean_function=custom_function,
        )

    def _append_mail(
        self,
        message: Union[Message, mboxMessage],
        path: Optional[Union[str, Path]] = None,
    ) -> None:
        self.add_mail(self._create_mail(message, path))

    def add_mbox(self, mbox_path: Union[str, Path]) -> None:
        mbox_path = to_Path(mbox_path)
        filter_suffix = ".mbox"

        if not mbox_path.exists():
            raise FileExistsError(mbox_path)

        if mbox_path.is_file() and mbox_path.suffix == filter_suffix:
            mail_box = mailbox.mbox(mbox_path)

            for message in mail_box:
                self._append_mail(message, self.mbox_path)
        elif self.mbox_path.is_dir():
            for file in mbox_path.iterdir():
                if mbox_path.suffix == filter_suffix:
                    mail_box = mailbox.mbox(file)
                    for message in mail_box:
                        self._append_mail(message, self.mbox_path)

    def add_eml(self, eml_path: Union[str, Path]) -> None:
        eml_path = to_Path(eml_path)
        filter_suffix = ".eml"

        if not eml_path.exists():
            raise FileNotFoundError(eml_path)

        if eml_path.is_file() and eml_path.suffix == filter_suffix:
            with open(eml_path, "rb") as email_file:
                message = email.message_from_bytes(email_file.read())
                self._append_mail(message, eml_path)
        elif eml_path.is_dir():
            for file in eml_path.iterdir():
                if file.suffix == filter_suffix:
                    with open(file, "rb") as email_file:
                        message = email.message_from_bytes(email_file.read())
                        self._append_mail(message, eml_path)
