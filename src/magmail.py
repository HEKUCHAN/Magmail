import os
import csv
import mailbox
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Optional

from .mail import Mail


class Magmail:
    def __init__(
        self,
        mbox_path: str,
        auto_clean: bool = True,
        filter_content_type: Optional[str] = None,
        trial_charset_list: Optional[List[str]] = None,
        extends_trial_charset_list: List[str] = [],
    ):
        self.mbox_path: Path = Path(mbox_path)
        self.auto_clean = auto_clean
        self.filter_content_type = filter_content_type
        self.trial_charset_list = trial_charset_list
        self.extends_trial_charset_list = extends_trial_charset_list
        if not os.path.exists(self.mbox_path):
            raise FileNotFoundError()

        self.is_dir: bool = os.path.isdir(self.mbox_path)
        self.emails: List[Mail] = []

        self._parse()

    def __len__(self) -> int:
        return len(self.emails)

    def _parse(self) -> None:
        if not self.is_dir:
            mail_box = mailbox.mbox(self.mbox_path)
            for message in mail_box:
                self.emails.append(
                    Mail(
                        message,
                        auto_clean=self.auto_clean,
                        filter_content_type=self.filter_content_type,
                        trial_charset_list=self.trial_charset_list,
                        extends_trial_charset_list=self.extends_trial_charset_list
                    )
                )
        else:
            for file in os.listdir(self.mbox_path):
                mail_box = mailbox.mbox(self.mbox_path / file)
                for message in mail_box:
                    self.emails.append(
                        Mail(
                            message,
                            auto_clean=self.auto_clean,
                            filter_content_type=self.filter_content_type,
                            trial_charset_list=self.trial_charset_list,
                            extends_trial_charset_list=self.extends_trial_charset_list
                        )
                    )

    def total(self) -> int:
        return self.__len__()

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
                        mail.to_address,
                        mail.cc_address,
                        mail.from_address,
                        mail.body,
                        mail.has_file(),
                        mail.attach_file_list,
                        mail.has_image(),
                        mail.images,
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
        ]
        dataframe: pd.DataFrame = pd.DataFrame(columns=col_names)

        for mail in self.emails:
            series = pd.Series(
                [
                    mail.subject,
                    mail.date,
                    mail.to_address,
                    mail.cc_address,
                    mail.from_address,
                    mail.body,
                    mail.has_file(),
                    mail.attach_file_list,
                    mail.has_image(),
                    mail.images,
                    mail.is_multipart,
                ]
            )
            dataframe = pd.DataFrame(
                np.vstack([dataframe.values, series.values]), columns=dataframe.columns
            )

        return dataframe
