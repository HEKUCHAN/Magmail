import os
import csv
import email
import mailbox
import numpy as np
import pandas as pd
from pathlib import Path
from mailbox import mboxMessage
from email.message import Message
from typing import List, Optional, Union, Callable, Dict

from .mail import Mail


class Magmail:
    def __init__(
        self,
        mbox_path: str,
        auto_clean: bool = True,
        filter_content_type: Optional[str] = None,
        trial_charset_list: Optional[List[str]] = None,
        extends_trial_charset_list: List[str] = [],
        custom_clean_function: Optional[Callable[[str], str]] = None,
        extension_charset_list: Optional[Dict[str, str]] = None,
        extends_extension_charset_list: Optional[Dict[str, str]] = None,
    ):
        self.mbox_path: Path = Path(mbox_path)
        self.auto_clean = auto_clean
        self.filter_content_type = filter_content_type
        self.trial_charset_list = trial_charset_list
        self.extends_trial_charset_list = extends_trial_charset_list
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

    def add_mail(self, eml_path: str) -> None:
        with open(eml_path, "rb") as email_file:
            message = email.message_from_bytes(email_file.read())
            self._add_message(message)

    def export_csv(
        self,
        path: str = "./mbox.csv",
        encoding: str = "utf-8",
        header: List[str] = [
            "subject",
            "date",
            "to_address",
            "cc_address",
            "from_address",
            "body",
            "has_file",
            "attach_file_list",
            "has_image",
            "images",
            "is_multipart",
            "has_delivered_to",
        ],
    ) -> None:
        with open(path, "w", encoding=encoding) as f:
            writer = csv.writer(f, quotechar='"')
            writer.writerow(header)
            for mail in self.emails:
                writer.writerow(
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

    def dataframe(self) -> pd.DataFrame:
        col_names = [
            "subject",
            "date",
            "to_address",
            "cc_address",
            "from_address",
            "body",
            "has_file",
            "attach_file_list",
            "has_image",
            "images",
            "is_multipart",
            "has_delivered_to",
        ]
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
