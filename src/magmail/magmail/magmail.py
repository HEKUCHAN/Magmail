import csv
import math
import email
import mailbox
from pathlib import Path
from io import TextIOWrapper
from mailbox import mboxMessage
from email.message import Message
from typing import Any, Generator, Iterator, Optional, Union, List, Dict, Callable

from .filter import _Filter
from magmail.mail import Mail
from magmail.utils import to_Path
from magmail.static import (
    DEFAULT_AUTO_CLEAN,
    DEFAULT_COLUMNS,
    CUSTOM_FUNCTIONS_DICT,
    DEFAULT_FILTER_CONTENTS_DICT,
    FILTER_CONTENTS_TYPE,
)


class Magmail:
    def __init__(
        self,
        mbox_path: Union[str, Path],
        auto_clean: bool = DEFAULT_AUTO_CLEAN,
        filters: Dict[str, FILTER_CONTENTS_TYPE] = DEFAULT_FILTER_CONTENTS_DICT.copy(),
        custom_functions: Dict[
            str, Dict[str, Callable[[Any], Any]]
        ] = CUSTOM_FUNCTIONS_DICT.copy(),
        drop_duplicates: bool = True,
    ):
        self.mbox_path: Path = to_Path(mbox_path)
        self.auto_clean: bool = auto_clean
        self.filters: _Filter = _Filter(filters)
        self.custom_functions: Dict[
            str, Dict[str, Callable[[Any], Any]]
        ] = custom_functions
        self.drop_duplicates = drop_duplicates

        self.emails: List[Mail] = []
        self.add_mail: Callable[[Mail], None] = self.emails.append

        self._parse()

    def __len__(self) -> int:
        return len(self.emails)

    def __iter__(self) -> Iterator[Mail]:
        return iter(self.emails)

    def total(self) -> int:
        return self.__len__()

    def _parse(self) -> None:
        if self.mbox_path.suffix == ".mbox":
            self.add_mbox(self.mbox_path)
        elif self.mbox_path.suffix == ".eml":
            self.add_eml(self.mbox_path)
        else:
            raise TypeError("Only supported .eml or .mbox files.")

    def _create_mail(
        self,
        message: Union[Message, mboxMessage],
        path: Optional[Union[str, Path]] = None,
    ) -> Mail:

        return Mail(
            message=message,
            path=path,
            auto_clean=self.auto_clean,
            filters=self.filters.filter_dict.copy(),
            custom_functions=self.custom_functions,
        )

    def _append_mail(
        self,
        message: Union[Message, mboxMessage],
        path: Optional[Union[str, Path]] = None,
        drop_duplicates=True,
    ) -> None:
        if drop_duplicates and self.is_mail_exist(message):
            return

        self.add_mail(self._create_mail(message, path))

    def is_mail_exist(self, message: Union[Message, mboxMessage]):
        for mail in self.emails:
            if mail.message.as_string() == message.as_string():
                return True
        return False

    def add_mbox(self, mbox_path: Union[str, Path]) -> None:
        mbox_path = to_Path(mbox_path)
        filter_suffix = ".mbox"

        if not mbox_path.exists():
            raise FileExistsError(mbox_path)

        if mbox_path.is_file() and mbox_path.suffix == filter_suffix:
            mail_box = mailbox.mbox(mbox_path)

            for message in mail_box:
                self._append_mail(
                    message, self.mbox_path, drop_duplicates=self.drop_duplicates
                )
        elif self.mbox_path.is_dir():
            for file in mbox_path.iterdir():
                if mbox_path.suffix == filter_suffix:
                    mail_box = mailbox.mbox(file)
                    for message in mail_box:
                        self._append_mail(
                            message,
                            self.mbox_path,
                            drop_duplicates=self.drop_duplicates,
                        )

    def add_eml(self, eml_path: Union[str, Path]) -> None:
        eml_path = to_Path(eml_path)
        filter_suffix = ".eml"

        if not eml_path.exists():
            raise FileNotFoundError(eml_path)

        if eml_path.is_file() and eml_path.suffix == filter_suffix:
            with open(eml_path, "rb") as email_file:
                message = email.message_from_bytes(email_file.read())
                self._append_mail(
                    message, eml_path, drop_duplicates=self.drop_duplicates
                )
        elif eml_path.is_dir():
            for file in eml_path.iterdir():
                if file.suffix == filter_suffix:
                    with open(file, "rb") as email_file:
                        message = email.message_from_bytes(email_file.read())
                        self._append_mail(
                            message, eml_path, drop_duplicates=self.drop_duplicates
                        )

    def split_emails(self, n: int) -> Generator[list[Mail], None, None]:
        for idx in range(0, self.total(), n):
            yield self.emails[idx : idx + n]

    def export_csv(
        self,
        path: Union[str, Path] = "./mbox.csv",
        filename: Optional[Union[str, Path]] = None,
        encoding: str = "utf-8",
        columns: List[str] = DEFAULT_COLUMNS.copy(),
        extends_columns: List[str] = [],
        slice_files: int = 1,
    ) -> None:
        """Export all mails of this class to csv"""
        files: List[TextIOWrapper] = []
        files_path: List[Path] = []
        if extends_columns:
            columns.extend(extends_columns)

        csv_path = to_Path(path)

        if slice_files > 1:
            if csv_path.is_dir():
                if filename is None:
                    filename = Path("mbox.csv")

                csv_filename = to_Path(filename)

                for i in range(1, slice_files + 1):
                    csv_filename = csv_filename.with_suffix(".csv")
                    files_path.append(
                        csv_path / (csv_filename.stem + f"-{i}" + csv_filename.suffix)
                    )
            else:
                csv_filename = csv_path.with_suffix(".csv")
                for i in range(1, slice_files + 1):
                    files_path.append(
                        csv_path.parent
                        / (csv_filename.stem + f"-{i}" + csv_filename.suffix)
                    )
        else:
            csv_path = csv_path.with_suffix(".csv")
            files_path.append(csv_path)

        for path in files_path:
            files.append(open(path, "w", encoding=encoding, newline=""))

        file_index = 0
        for splitted_emails in self.split_emails(math.ceil(self.total() / slice_files)):
            writer = csv.writer(files[file_index], quotechar='"')
            writer.writerow(columns)
            for mail in splitted_emails:
                rows = []
                for row in columns:
                    rows.append(getattr(mail, row, None))
                writer.writerow(rows)
            file_index += 1
