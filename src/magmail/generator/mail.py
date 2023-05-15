import os
import uuid
import quopri

from pathlib import Path
from types import GeneratorType
from base64 import b64encode, b64decode
from typing import Dict, List, Tuple, Union

from email import generator
from email.header import Header
from email.utils import formatdate, formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from magmail.utils import get_type_name


class Mail:
    def __init__(
        self,
        addr_to: Union[str, Tuple[str, str]] = "",
        addr_from: Union[str, Tuple[str, str]] = "",
        addr_cc: Union[str, Tuple[str, str]] = "",
        subject: str = "",
        message: Union[str, Dict[str, str]] = "",
        headers: Dict[str, str] = {},
        encoding: str = "utf-8",
        mime_type: str = "plain",
        transfer_encoding: str = "base64",
        attach_files_path: Union[List[str], str] = [],
    ):
        self.addr_to = addr_to
        self.addr_from = addr_from
        self.addr_cc = addr_cc
        self.subject = subject
        self.message = message
        self.headers = headers
        self.encoding = encoding
        self.mime_type = mime_type.lower()
        self.attach_files_path = attach_files_path
        self.transfer_encoding = transfer_encoding
        self.__set_transfer_encoding()
        self.__body()
        self.__headers()
        self.__attach_files()

    def __set_transfer_encoding(self):
        self.transfer_encoding_func = None

        if self.transfer_encoding == "base64":
            self.transfer_encoding_func = b64encode
        elif self.transfer_encoding == "quoted-printable":
            self.transfer_encoding_func = quopri.encodestring
        elif (
            self.transfer_encoding == "7bit"
            or self.transfer_encoding == "8bit"
            or self.transfer_encoding == "binary"
        ):
            self.transfer_encoding_func = lambda msg: msg  # Do nothing

    def __headers(self):
        headers: Dict[str, Union[str, Tuple[str, str]]] = {
            "Subject": self.subject,
            "From": self.addr_from,
            "To": self.addr_to,
            "cc": self.addr_cc,
        }
        headers.update(self.headers)

        for name, header in headers.items():
            formatted_header = self.format_header(header, self.encoding)

            if len(formatted_header) > 1:
                self.mime[name] = ", ".join([value for value in formatted_header])
            else:
                self.mime[name] = formatted_header

        self.mime["Date"] = formatdate()

    def __body(self):
        if self.mime_type == "plain":
            self.mime = MIMEText(
                self.transfer_encoding_func(self.message.encode(self.encoding)),
                "plain",
                _charset=self.encoding,
            )
        elif self.mime_type == "html":
            self.mime = MIMEText(
                self.transfer_encoding_func(self.message.encode(self.encoding)),
                "html",
                _charset=self.encoding,
            )
        elif self.mime_type == "multipart":
            self.mime = MIMEMultipart()

            if not isinstance(self.message, dict):
                raise TypeError("Invalid type for 'message'. Expected dictionary.")

            if not "plain" in self.message or not "html" in self.message:
                raise ValueError(
                    "Missing required values in 'message' dictionary. Both 'plain' and 'html' keys are required."
                )

            self.mime.attach(
                MIMEText(
                    self.transfer_encoding_func(
                        self.message["plain"].encode(self.encoding)
                    ),
                    "plain",
                    _charset=self.encoding,
                )
            )
            self.mime.attach(
                MIMEText(
                    self.transfer_encoding_func(
                        self.message["html"].encode(self.encoding)
                    ),
                    "html",
                    _charset=self.encoding,
                )
            )

        # The Transfer Encoding was duplicated, so Fix that here
        # Example : `base64`, `base64`, `utf-8` -> `base64`, `utf-8`
        self.mime.set_payload(b64decode(self.mime.get_payload()).decode("utf-8"))
        self.mime.replace_header("Content-Transfer-Encoding", self.transfer_encoding)

    def __attach_files(self):
        if isinstance(self.attach_files_path, list):
            for file_path in self.attach_files_path:
                with open(file_path, "rb") as file:
                    attachment_file = MIMEApplication(file.read())
                attachment_file.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=os.path.basename(file_path),
                )
                self.mime.attach(attachment_file)
        else:
            with open(self.attach_files_path, "rb") as file:
                attachment_file = MIMEApplication(file.read())
            attachment_file.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.basename(self.attach_files_path),
            )
            self.mime.attach(attachment_file)

    def to_file(self, path="./"):
        def write(path):
            with open(path, "w") as eml:
                gen = generator.Generator(eml)
                gen.flatten(self.mime)

        file_path = Path(path)

        if file_path.suffix != ".eml":
            raise ValueError(
                f"Unsupported file extension: {file_path.suffix}. Only `.eml` extensions are supported."
            )

        if file_path.is_dir():
            file_path = file_path / f"{uuid.uuid4()}.eml"
            write(file_path)
        else:
            write(file_path)

    def encode_header(self, value: str, encoding=None) -> str:
            if value.isascii():
                return value
            else:
                return Header(value, encoding).encode()
            
    def format_header(self, values: str, encoding=None) -> str:
            if isinstance(values, tuple):
                name_and_addr = (
                    self.encode_header(value, encoding=encoding)
                    for value in values
                )
                return formataddr(name_and_addr, charset=encoding)
            elif isinstance(values, list):
                return [self.format_header(value) for value in values]
            elif isinstance(values, str):
                return self.encode_header(values, encoding=encoding)
            else:
                raise TypeError(
                    f"{get_type_name(values)} is not supported for setting header values."
                )
