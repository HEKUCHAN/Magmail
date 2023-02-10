import os
import csv
import email
import mailbox
import numpy as np
import pandas as pd
from pathlib import Path
from io import TextIOWrapper
from mailbox import mboxMessage
from email.message import Message
from typing import List, Optional, Union, Callable, Dict

from .mail import Mail


class Magmail:
    def __init__(
        self,
        mbox_path: Union[str, Path],
        auto_clean: bool = True,
        filter_content_type: Optional[str] = None,
        trial_charset_list: Optional[List[str]] = None,
        extends_trial_charset_list: List[str] = [],
        extension_charset_list: Optional[Dict[str, str]] = None,
        extends_extension_charset_list: Dict[str, str] = {},
        custom_clean_function: Optional[Callable[[str], str]] = None,
    ):
        if isinstance(mbox_path, str):
            self.mbox_path = Path(mbox_path)
        else:
            self.mbox_path = mbox_path

        self.auto_clean = auto_clean
        self.filter_content_type = filter_content_type
        self.trial_charset_list = trial_charset_list
        self.extends_trial_charset_list = extends_trial_charset_list
        self.extension_charset_list = extension_charset_list
        self.extends_extension_charset_list = extends_extension_charset_list
        self.custom_clean_function: Optional[
            Callable[[str], str]
        ] = custom_clean_function
        if not os.path.exists(self.mbox_path):
            raise FileNotFoundError()

        self.is_dir: bool = os.path.isdir(self.mbox_path)
        self.emails: List[Mail] = []

        self._parse()

    def __len__(self) -> int:
        return len(self.emails)

    def total(self) -> int:
        return self.__len__()

    def _add_message(self, message: Union[Message, mboxMessage]) -> None:
        self.emails.append(
            Mail(
                message,
                auto_clean=self.auto_clean,
                filter_content_type=self.filter_content_type,
                trial_charset_list=self.trial_charset_list,
                extends_trial_charset_list=self.extends_trial_charset_list,
                custom_clean_function=self.custom_clean_function,
                extension_charset_list=self.extension_charset_list,
                extends_extension_charset_list=self.extends_extension_charset_list,
            )
        )

    def _parse(self) -> None:
        if not self.is_dir:
            mail_box = mailbox.mbox(self.mbox_path)
            for message in mail_box:
                self._add_message(message)
        else:
            for file in os.listdir(self.mbox_path):
                mail_box = mailbox.mbox(self.mbox_path / file)
                for message in mail_box:
                    self._add_message(message)
        print("Total of successfully parsed files: %d" % len(self))
        print("Total of failed to decode body or header: %d" % Mail.failed_decode_count)

    def add_mail(self, eml_path: Union[str, Path]) -> None:
        if isinstance(eml_path, str):
            self.eml_path = Path(eml_path)
        else:
            self.eml_path = eml_path
        with open(eml_path, 'rb') as email_file:
            message = email.message_from_bytes(email_file.read())
            self._add_message(message)

    @classmethod
    def gets_instance_variable(self, obj: object) -> List[str]:
        variables: List[str] = []
        for variable in obj.emails[0].__dir__():
            if not variable[0] == "_":
                variables.append(variable)

        return variables

    def export_csv(
        self,
        path: Union[str, Path] = "./mbox.csv",
        filename: Optional[Union[str, Path]] = None,
        encoding: str = "utf-8",
        columns: Optional[List[str]] = None,
        extends_columns: List[str] = [],
        slice_files: int = 1
    ) -> None:
        files: List[TextIOWrapper] = []
        files_path: List[Path] = []

        if not isinstance(path, Path):
            csv_path: Path = Path(path)
        else:
            csv_path = path

        if slice_files > 1:
            if os.path.isdir(path):
                if filename is None:
                    filename: Path = Path("mbox.csv")

                if not isinstance(filename, Path):
                    csv_filename: Path = Path(filename)
                else:
                    csv_filename = filename

                for i in range(1, slice_files+1):
                    csv_filename = csv_filename.with_suffix(".csv")
                    files_path.append(
                        csv_path / (csv_filename.stem + f"-{i}" + csv_filename.suffix)
                    )
            else:
                csv_filename = csv_path.with_suffix(".csv")
                for i in range(1, slice_files+1):
                    files_path.append(
                        csv_path.parent / (csv_filename.stem + f"-{i}" + csv_filename.suffix)
                    )
        else:
            csv_path = csv_path.with_suffix(".csv")
            files_path.append(
                csv_path
            )

        for path in files_path:
            files.append(
                open(path, 'w', encoding=encoding)
            )

        for i, mail in enumerate(self.emails):
            total = self.total()
            split_amount = total // slice_files

            writer = csv.writer(files[i // split_amount - 1], quotechar='"')

            if (i / split_amount).is_integer():
                if columns is None:
                    columns: List[str] = [
                        "subject",
                        "date",
                        "to_header",
                        "cc_header",
                        "from_header",
                        "body",
                        "has_file",
                        "attach_file_list",
                        "has_image",
                        "is_multipart",
                        "has_delivered_to",
                    ]
                    columns.extend(extends_columns)
                writer.writerow(columns)

            rows = []
            for row in columns:
                rows.append(getattr(mail, row, None))
            writer.writerow(rows)

    def dataframe(
        self, columns: Optional[List[str]], extends_columns: List[str] = []
    ) -> pd.DataFrame:
        if columns is None:
            columns: List[str] = [
                "subject",
                "date",
                "to_header",
                "cc_header",
                "from_header",
                "body",
                "has_file",
                "attach_file_list",
                "has_image",
                "is_multipart",
                "has_delivered_to",
            ]
            columns.extend(extends_columns)
        dataframe: pd.DataFrame = pd.DataFrame(columns=col_names)

        for mail in self.emails:
            series = pd.Series(
                [
                    mail.subject,
                    mail.date,
                    mail.to_header,
                    mail.cc_header,
                    mail.from_header,
                    mail.body,
                    mail.has_file,
                    mail.attach_file_list,
                    mail.has_image,
                    mail.images,
                    mail.is_multipart,
                    mail.has_delivered_to,
                ]
            )
            dataframe = pd.DataFrame(
                np.vstack([dataframe.values, series.values]), columns=dataframe.columns
            )

        return dataframe
