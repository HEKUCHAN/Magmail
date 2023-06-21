import os
import uuid
import quopri

from pathlib import Path
from base64 import b64encode, b64decode
from typing import Any, Dict, List, Optional, Tuple, Union

from email import generator
from email.header import Header
from email.charset import Charset
from email.utils import formatdate, formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from magmail.utils import get_type_name, to_path
from magmail.types import ADDRESS_HEADER_TYPE, HEADER_TYPE


class Mail:
    def __init__(
        self,
        addr_to: ADDRESS_HEADER_TYPE = "",
        addr_from: ADDRESS_HEADER_TYPE = "",
        addr_cc: Union[List[ADDRESS_HEADER_TYPE], ADDRESS_HEADER_TYPE] = "",
        subject: str = "",
        message: Union[str, Dict[str, str]] = "",
        headers: Dict[str, HEADER_TYPE] = {},
        encoding: str = "utf-8",
        mime_type: str = "plain",
        transfer_encoding: str = "base64",
        attachment_file_paths: Union[List[Union[str, Path]], Union[Path, str]] = [],
    ):
        self.addr_to = addr_to
        self.addr_from = addr_from
        self.addr_cc = addr_cc
        self.subject = subject
        self.message = message
        self.headers = headers
        self.encoding = encoding
        self.mime: Union[MIMEText, MIMEMultipart]
        self.mime_type = mime_type.lower()
        self.attachment_file_paths = attachment_file_paths
        if isinstance(self.attachment_file_paths, list):
            self.attachment_file_paths = [
                to_path(path) for path in self.attachment_file_paths
            ]
        self.transfer_encoding = transfer_encoding
        self.__set_transfer_encoding()
        self.__body()
        self.__headers()
        self.__attach_files()

    def __set_transfer_encoding(self) -> None:
        self.transfer_encoding_func: Any = None

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

    def __headers(self) -> None:
        headers: Dict[str, HEADER_TYPE] = {
            "Subject": self.subject,
            "From": self.addr_from,
            "To": self.addr_to,
            "cc": self.addr_cc,
        }
        headers.update(self.headers)

        for name, header in headers.items():
            formatted_header = self.format_header(header, self.encoding)

            if isinstance(formatted_header, list):
                self.mime[name] = ", ".join([value for value in formatted_header])
            else:
                self.mime[name] = formatted_header

        self.mime["Date"] = formatdate()

    def __body(self) -> None:
        if self.mime_type == "plain":
            if isinstance(self.message, dict):
                raise TypeError(
                    "The 'message' argument cannot be a dictionary when mime_type is 'plain'."
                )

            self.mime = MIMEText(
                self.transfer_encoding_func(self.message.encode(self.encoding)),
                "plain",
                _charset=self.encoding,
            )
        elif self.mime_type == "html":
            if isinstance(self.message, dict):
                raise TypeError(
                    "The 'message' argument cannot be a dictionary when mime_type is 'html'."
                )

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

        if self.encoding == "shift_jis" or self.encoding == "euc_jp":
            self.mime.output_encoding = self.encoding
            self.mime.replace_header("Content-Type", f'text/plain; charset="{self.encoding}"')
        self.mime.set_payload(b64decode(self.mime.get_payload(decode=False)))
        self.mime.replace_header("Content-Transfer-Encoding", self.transfer_encoding)

    def __attach_files(self) -> None:
        if isinstance(self.attachment_file_paths, list):
            for file_path in self.attachment_file_paths:
                with open(file_path, "rb") as file:
                    attachment_file = MIMEApplication(file.read())
                attachment_file.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=os.path.basename(file_path),
                )
                self.mime.attach(attachment_file)
        else:
            with open(self.attachment_file_paths, "rb") as file:
                attachment_file = MIMEApplication(file.read())
            attachment_file.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.basename(self.attachment_file_paths),
            )
            self.mime.attach(attachment_file)

    def to_file(self, path: Union[str, Path] = "./", encoding: str='utf-8') -> None:
        def write(path: Union[str, Path]) -> None:
            with open(path, "w", encoding=encoding) as eml:
                gen = generator.Generator(eml)
                gen.flatten(self.mime)

        file_path = to_path(path)

        if file_path.suffix != ".eml":
            raise ValueError(
                f"Unsupported file extension: {file_path.suffix}. Only '.eml' extensions are supported."
            )

        if file_path.is_dir():
            file_path = file_path / f"{uuid.uuid4()}.eml"
            write(file_path)
        else:
            write(file_path)

    def encode_header(
        self, value: str, encoding: Optional[Union[Charset, str]] = None
    ) -> str:
        if value.isascii():
            return value
        else:
            return Header(value, encoding).encode()

    def encode_address(
        self, address: ADDRESS_HEADER_TYPE, encoding: Union[Charset, str] = "utf-8"
    ) -> str:
        if isinstance(address, str):
            return self.encode_header(address, encoding=encoding)
        elif isinstance(address, tuple):
            name_and_addr: Tuple[Optional[str], str] = (
                self.encode_header(address[0], encoding=encoding),
                self.encode_header(address[1], encoding=encoding),
            )

            return formataddr(name_and_addr, charset=encoding)

    def format_header(
        self,
        values: HEADER_TYPE,
        encoding: Union[Charset, str] = "utf-8",
    ) -> Union[str, List[str]]:
        if isinstance(values, tuple):
            return self.encode_address(values, encoding=encoding)
        elif isinstance(values, list):
            test = [self.encode_address(value) for value in values]
            return test
        elif isinstance(values, str):
            return self.encode_header(values, encoding=encoding)
        else:
            raise TypeError(
                f"{get_type_name(values)} is not supported for setting header values."
            )
