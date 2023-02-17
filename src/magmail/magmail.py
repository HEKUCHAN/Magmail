import os
import csv
import math
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
from .utils import Utils
from .static import DEFAULT_COLUMNS


class Magmail:
    """Magmail class is a class to change `.mbox` file to csv file or `pandas.dataframe`

    Magmail class is a class that can be used to gets email has in `.mbox` files.
    Mails of `.mbox` files will automatically decode and if you want, you can clean them.
    You can add mails of `.eml` or `.mbox` files in instantiated class.
    if you add new mails in instantiated class, These emails will be added in the `emails` attribute of this class.

    Attributes:
      mbox_path (:obj:`Union[str, Path]`): Path of the `.mbox` file

      auto_clean (:obj:`bool`): 
        Clean or not clean the body and header of the email in the `.mbox` file.
        If you change to True, headers and body of mails will be automatically cleaned.

        The following will be cleaned.

        Headers
         - Newlines will be removed
         - First and last space will be removed
         - Urls will be removed
         - More than a blank will be a blank

        Body
         - More than a blank will be a blank
         - Comments of html will be removed
         - HTML tags will be removed
         - URLs will be removed
         - Tabs will be removed
         - Email addresses will be removed

      filter_content_type (:obj:`Union[List[str], Optional[str]]`):
        You can filter the `Content-Type` header of emails
        if set `text/plain` only plains text will be added in `body` attribute of Mail class.

      trial_charset_list (:obj:`Optional[List[str]]`): 
        If failed to detect the charset of body or charset, The charsets of this list will be tried.

      extends_trial_charset_list (:obj:`Optional[List[str]]`): 
        You can extends list of `trial_charset_list` attribute of Mail class.

      extension_charset_list (:obj:`Optional[Dict[str, str]]`): 
        Sometimes `chardet` detect charset before extension,
        You can change to extended charset.
        Example, shift-jis and cp932

      extends_extension_charset_list (:obj:`Dict[str, str]`): 
        You can extends default dict of `extension_charset_list` attribute of Mail class.

      custom_clean_function (:obj:`Callable[[str], str]`): 
        test

      is_dir (:obj:`bool`): 
        if `mbox_path` attribute of this class is path of directory will be true

      emails (:obj:`List[Mail]`): 
        All mails decoded from `.mbox` file will added in this list

    Args:
      mbox_path (:obj:`Union[str, Path]`): 
        path to the `.mbox` file
        You can set directory path or `.mbox` file path.
        If you set directory path, are mails of `.mbox` files in the directory will be changed to `Mail` class and it will add in the `emails` attribute of this class.

      auto_clean (:obj:`bool`, Optional): 
        Default is False, if you want to clean the mails in `.mbox` files change to True.
        If you change to True, headers and body of mails will be automatically cleaned.
        The following will be cleaned.

        Headers
         - Newlines will be removed
         - First and last space will be removed
         - Urls will be removed
         - More than a blank will be a blank

        Body
         - More than a blank will be a blank
         - Comments of html will be removed
         - HTML tags will be removed
         - URLs will be removed
         - Tabs will be removed
         - Emails addresses will be removed

      filter_content_type (:obj:`Union[List[str], Optional[str]]`, Optional): 
        Default value is `None`, You can filter the `Content-Type` header of emails

      trial_charset_list (:obj:`Optional[List[str]]`, Optional): 
        Default value is `None`.
        If failed to detect the charset of body or charset, The charsets of this list will be tried.

      extends_trial_charset_list (:obj:`List[str]`, Optional): 
        Default value is `[]`, You can add new charsets in `trial_charset_list` attribute.

      extension_charset_list (:obj:`Optional[Dict[str, str]]`, Optional): 
        If you wants to change `extension_charset_list` attribute of Mail class, set the value type was documetioned.
  
      extends_extension_charset_list (:obj:`Dict[str, str]`, Optional): 
        Default value is `{}`.
        You can extends default dict of `extension_charset_list` attribute of Mail class.

      custom_clean_function (:obj:`Optional[Callable[[str], str]]`, Optional): 
        You can set custom cleanup function.
        This custom function will clean headers and body of mails.
        The function has to return str, and the first argument should to can able to set str.

    Raises: 
      FileNotFoundError: When not found mbox file will be raised.
    
    Examples:
      .. code-block:: python
          :caption: If you want to use a custom cleanup function.

          def example_clean(text):
              return text

          Magmail(
              "path/to/mbox",
              custom_clean_function=example_clean
          )
    """
    def __init__(
        self,
        mbox_path: Union[str, Path],
        auto_clean: bool = True,
        filter_content_type: Union[List[str], Optional[str]] = None,
        trial_charset_list: Optional[List[str]] = None,
        extends_trial_charset_list: List[str] = [],
        extension_charset_list: Optional[Dict[str, str]] = None,
        extends_extension_charset_list: Dict[str, str] = {},
        custom_clean_function: Optional[Callable[[str], str]] = None,
    ):
        self.mbox_path = Utils.str_to_Path(mbox_path)
        self.auto_clean = auto_clean
        self.filter_content_type = filter_content_type
        self.trial_charset_list = trial_charset_list
        self.extends_trial_charset_list = extends_trial_charset_list
        self.extension_charset_list = extension_charset_list
        self.extends_extension_charset_list = extends_extension_charset_list
        self.custom_clean_function: Optional[
            Callable[[str], str]
        ] = custom_clean_function
        self.is_dir: bool = self.mbox_path.is_dir()
        self.emails: List[Mail] = []

        self._parse()

    def __len__(self) -> int:
        return len(self.emails)

    def total(self) -> int:
        """Returns the number of decoded emails.

        Returns:
          int: The number of decoded emails.
        """
        return self.__len__()
    
    def _create_mail(self, message: Union[Message, mboxMessage]) -> Mail:
        return Mail(
            message,
            auto_clean=self.auto_clean,
            filter_content_type=self.filter_content_type,
            trial_charset_list=self.trial_charset_list,
            extends_trial_charset_list=self.extends_trial_charset_list,
            custom_clean_function=self.custom_clean_function,
            extension_charset_list=self.extension_charset_list,
            extends_extension_charset_list=self.extends_extension_charset_list,
        )

    def _append_mail(self, message: Union[Message, mboxMessage]) -> None:
        """Adds a mail in emails attribute.

        Change `Message` or `mboxMessage` class to `Mail` class and add instance was created in `emails` attribute

        Args:
          message (Union[Message, mboxMessage]):
            Add `Message` or `mboxMessage` class to change to `Mail` class and add this instance in `emails` attribute
        """
        self.emails.append(
            self._create_mail(message)
        )

    def _parse(self) -> None:
        """Change `.mbox`'s mail to `Mail` class

        The mails of `.mbox` file will be changed to `Mail` class and it will be added in `emails` attribute of this class.
        If path of `.mbox` is directory,  are mails of `.mbox` files in the directory will be changed to `Mail` class and it will add in the `emails` attribute of this class.
        Also, if any extensions other than `.mbox` exist in the directory, they are ignored.

        """
        
        self.add_mbox(self.mbox_path)

        print("Total of successfully parsed files: %d" % len(self))
        print("Total of failed to decode body or header: %d" % Mail.failed_decode_count)

    def add_mail(self, eml_path: Union[str, Path]) -> None:
        """保留
        """
        eml_path = Utils.str_to_Path(eml_path)
        filter_suffix = ".eml"

        if not eml_path.exists():
            raise FileNotFoundError()

        if eml_path.is_file() and eml_path.suffix == filter_suffix:
            with open(eml_path, "rb") as email_file:
                message = email.message_from_bytes(email_file.read())
                self._append_mail(message)
        elif eml_path.is_dir():
            for file in eml_path.iterdir():
                if file.suffix == filter_suffix:
                    with open(file, "rb") as email_file:
                        message = email.message_from_bytes(email_file.read())
                        self._append_mail(message)

    def add_mbox(self, mbox_path: Union[str, Path]) -> None:
        mbox_path = Utils.str_to_Path(mbox_path)
        filter_suffix = ".mbox"

        if not mbox_path.exists():
            raise FileNotFoundError()

        if mbox_path.is_file() and mbox_path.suffix == filter_suffix:
            mail_box = mailbox.mbox(mbox_path)
            for message in mail_box:
                self._append_mail(message)
        elif self.mbox_path.is_dir():
            for file in mbox_path.iterdir():
                if file.suffix == filter_suffix:
                    mail_box = mailbox.mbox(file)
                    for message in mail_box:
                        self._append_mail(message)

    def split_emails(self, n: int):
        for idx in range(0, self.total(), n):
            yield self.emails[idx:idx + n]

    def export_csv(
        self,
        path: Union[str, Path] = "./mbox.csv",
        filename: Optional[Union[str, Path]] = None,
        encoding: str = "utf-8",
        columns: List[str] = DEFAULT_COLUMNS.copy(),
        extends_columns: List[str] = [],
        slice_files: int = 1,
    ) -> None:
        """Export all mails of this class to csv

        """
        files: List[TextIOWrapper] = []
        files_path: List[Path] = []
        if extends_columns:
            columns.extend(extends_columns)

        csv_path = Utils.str_to_Path(path)

        if slice_files > 1:
            if csv_path.is_dir():
                if filename is None:
                    filename = Path("mbox.csv")

                csv_filename = Utils.str_to_Path(filename)

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

    def dataframe(
        self,
        columns: List[str] = DEFAULT_COLUMNS.copy(),
        extends_columns: List[str] = [],
    ) -> pd.DataFrame:
        if extends_columns:
            print(extends_columns)
            columns.extend(extends_columns)
        dataframe: pd.DataFrame = pd.DataFrame(columns=columns)

        for mail in self.emails:
            rows = []
            for row in columns:
                rows.append(getattr(mail, row, None))

            series = pd.Series(rows)
            dataframe = pd.DataFrame(
                np.vstack([dataframe.values, series.values]), columns=dataframe.columns
            )

        return dataframe
