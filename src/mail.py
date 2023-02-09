import re
import codecs
import chardet
from datetime import datetime
from mailbox import mboxMessage
from email.message import Message
from email.header import decode_header
from email.iterators import _structure
from email.utils import parsedate_to_datetime
from typing import Optional, Tuple, Union, List, overload


class Mail:
    failed_decode_count = 0

    def __init__(
        self,
        message: Union[Message, mboxMessage],
        auto_clean: bool = True,
        filter_content_type: Union[List[str], Optional[str]] = None,
        trial_charset_list: Optional[List[str]] = None,
        extends_trial_charset_list: List[str] = [],
    ):
        self.message: Union[Message, mboxMessage] = message
        self.auto_clean: bool = auto_clean
        self.is_multipart: bool = False
        self.trial_charset_list: List[str] = []
        self.filter_content_type: Union[List[str], Optional[str]] = filter_content_type

        if trial_charset_list is not None:
            self.trial_charset_list = trial_charset_list
        else:
            self.trial_charset_list = ["utf-8", "cp932", "shift-jis", "base64"]
        self.trial_charset_list.extend(extends_trial_charset_list)

        self.images: List[bytes] = []

        self.payload: bytes = b""
        self.body: Union[str, bytes, None] = ""
        self.original_body: Union[str, bytes, None] = ""
        self.content_charset: Optional[str] = ""
        self.body_charset: Optional[str] = ""
        self.header_charset: Optional[str] = ""
        self.detected_header_charset: Optional[str] = ""

        self.__subject = self._get_header("Subject")
        self.__date = self._get_header("Date")
        self.__to_header = self._get_header("To")
        self.__cc_header = self._get_header("Cc")
        self.__from_header = self._get_header("From")

        for part in self.message.walk():
            self.attach_fname = part.get_filename()
            self.content_maintype = part.get_content_maintype()
            self.content_subtype = part.get_content_subtype()
            self.attach_file_list: List[Optional[str]] = []

            if self.content_maintype == "multipart":
                self.is_multipart = True
                continue

            if self.content_maintype == "image":
                self.images.append(part.get_payload())
                continue

            if self.attach_fname is not None:
                self.attach_file_list.append(self._get_header(self.attach_fname))
                continue

            if (
                self.filter_content_type
                and part.get_content_type() not in self.filter_content_type
            ):
                continue

            self.payload = part.get_payload(decode=True)
            self.content_charset = part.get_content_charset()

            try:
                if self.payload and self.content_charset:
                    try:
                        self.body = codecs.decode(
                            self.payload, encoding=self.content_charset
                        )
                        self.body_charset = self.content_charset
                    except:
                        if not self.__is_canable_decode_body():
                            continue
                elif self.payload:
                    if not self.__is_canable_decode_body():
                        continue
                else:
                    self.body = ""
            except:
                decoded_payload, detected_charset = self.__trial_charset_decode(
                    self.payload
                )
                if isinstance(decoded_payload, bytes):
                    self.body = decoded_payload
                else:
                    self.__cannot_decode_body(self.payload, detected_charset)

        self.original_body = self.body
        if self.auto_clean:
            self.body = self._body_clean_text(self.body)

    @property
    def subject(self) -> Union[List[str], Optional[str]]:
        subject = self.__subject
        if self.auto_clean:
            subject = self._header_clean_text(subject)

        return subject

    @property
    def date(self) -> Union[datetime, Optional[str]]:
        if type(self.__date) is str:
            return parsedate_to_datetime(self.__date)
        return self.__date

    @property
    def to_header(self) -> Optional[str]:
        return self.__to_header

    def to_header_list(self) -> List[Tuple[Optional[str], Optional[str]]]:
        header_list = self._split_address_header(self.__to_header)
        return [header for header in header_list]

    @property
    def to_header_names(self) -> List[Optional[str]]:
        to_header_list = self._split_address_header(self.__to_header)

        return [name for name, _address in to_header_list]

    @property
    def to_header_address(self) -> List[Optional[str]]:
        to_header_list = self._split_address_header(self.__to_header)

        return [address for _name, address in to_header_list]

    @property
    def cc_header(self) -> Optional[str]:
        return self.__cc_header

    def cc_header_list(self) -> List[Tuple[Optional[str], Optional[str]]]:
        header_list = self._split_address_header(self.__cc_header)

        return [header for header in header_list]

    @property
    def cc_header_names(self) -> List[Optional[str]]:
        cc_header_list = self._split_address_header(self.__cc_header)

        return [name for name, _address in cc_header_list]

    @property
    def cc_header_address(self) -> List[Optional[str]]:
        cc_header_list = self._split_address_header(self.__cc_header)

        return [address for _name, address in cc_header_list]

    @property
    def from_header(self) -> Optional[str]:
        return self.__from_header

    def from_header_list(self) -> List[Tuple[Optional[str], Optional[str]]]:
        header_list = self._split_address_header(self.__from_header)

        return [header for header in header_list]

    @property
    def from_header_names(self) -> List[Optional[str]]:
        from_header_list = self._split_address_header(self.__from_header)

        return [name for name, _address in from_header_list]

    @property
    def from_header_address(self) -> List[Optional[str]]:
        from_header_list = self._split_address_header(self.__from_header)

        return [address for _name, address in from_header_list]

    @property
    def has_file(self) -> bool:
        return len(self.attach_file_list) > 0

    @property
    def has_image(self) -> bool:
        return len(self.images) > 0

    @property
    def has_delivered_to(self) -> bool:
        delivered_to = self._get_header("Delivered-To")
        if delivered_to is not None:
            return True
        return False

    def _get_header(self, name: str) -> Optional[str]:
        if not self.message[name]:
            return None

        header = ""
        for byte, charset in decode_header(self.message[name]):
            if isinstance(byte, bytes):
                if charset:
                    self.header_charset = charset
                    try:
                        header += codecs.decode(byte, charset)
                        continue
                    except:
                        pass

                (decoded_header, detected_charset) = self.__decode_unknown_charset(byte)

                if isinstance(decoded_header, str):
                    self.detected_header_charset = detected_charset
                    header += decoded_header
                else:
                    self.__cannot_decode_header(name, decoded_header, detected_charset)
                    continue
            elif isinstance(byte, str):
                header += byte

        return header

    @overload
    def _header_clean_text(self, header_values: Optional[str]) -> Optional[str]:
        ...

    @overload
    def _header_clean_text(self, header_values: List[str]) -> List[str]:
        ...

    def _header_clean_text(
        self, header_values: Union[Optional[str], List[str]]
    ) -> Union[Optional[str], List[str]]:
        def clean(text: str) -> str:
            text = text.replace("\r", "\n")
            text = text.replace("\n", "")
            text = "".join(text.splitlines())
            text = text.strip()
            text = re.sub(r"http\S+", " ", text)
            text = re.sub(r"\u3000", "", text)

            return text

        if header_values is not None:
            if isinstance(header_values, list):
                return [clean(text) for text in header_values]
            else:
                return clean(header_values)
        return header_values

    def _body_clean_text(self, clean_text: str) -> str:
        if clean_text is not None:
            # 小文字化
            clean_text = clean_text.lower()
            # Styleタグの削除
            clean_text = re.sub(r"<style[^>]*?>[\\s\\S]*?<\\/style>", "", clean_text)
            # Scriptタグの削除
            clean_text = re.sub(r"<script[^>]*?>[\\s\\S]*?<\\/script>", "", clean_text)
            # HTMLタグの削除
            clean_text = re.sub(r"<(\"[^\"]*\"|\'[^\']*\'|[^\'\">])*>", "", clean_text)
            # 行末記号を統一
            clean_text = clean_text.replace("\r\n", "\n")
            # 行末記号を統一
            clean_text = clean_text.replace("\r", "\n")
            # Unicodeの全角スペースを削除
            clean_text = re.sub(r"\u3000", "", clean_text)
            # URLの除去
            clean_text = re.sub(
                r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)",
                "",
                clean_text,
            )
            # メールアドレスの除去
            clean_text = re.sub(
                r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", " ", clean_text
            )
            # {}の中身を消す
            clean_text = re.sub(r"{.*?}", " ", clean_text)
            # &と;の中身を消す
            clean_text = re.sub(r"&.*?;", " ", clean_text)
            # 末尾の空白・改行コードの削除
            clean_text = "".join(clean_text.splitlines())
            # 複数タブ削除
            clean_text = re.sub(r"\t+", "", clean_text)
            # スペース削除
            clean_text = re.sub(r"\s+", " ", clean_text)
            # 全角空白の除去
            clean_text = re.sub(r"　", " ", clean_text)

        return clean_text

    def _split_address_header(
        self, header_text: Optional[str]
    ) -> List[Tuple[Optional[str], Optional[str]]]:
        if header_text is not None:
            address_header_regex = r"[^, ].+?<[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}>|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
            header_name_regex = r".*?[^\s](?=<|\s+<)"
            header_address_regex = r"([^<>](?<=<)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?=>)|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
            header_list: List[str] = re.findall(address_header_regex, header_text)
            splited_list: List[Tuple[Optional[str], Optional[str]]] = []

            for header in header_list:
                splited_name: List[Optional[str]] = re.findall(
                    header_name_regex, header
                )
                splited_address: List[Optional[str]] = re.findall(
                    header_address_regex, header
                )

                if splited_name and splited_name[0]:
                    name: Optional[str] = splited_name[0].strip()
                else:
                    name = None

                if splited_address and splited_address[0]:
                    address: Optional[str] = splited_address[0].strip()
                else:
                    address = None

                splited_list.append((name, address))
            return splited_list
        return [(None, None)]

    def __detect_charset(self, byte: bytes) -> Union[str, None]:
        detected_charset = chardet.detect(byte)["encoding"]
        if detected_charset == "SHIFT_JIS":
            detected_charset = "CP932"
        if detected_charset == "ISO-2022-JP":
            detected_charset = "CP932"

        return detected_charset

    def __is_canable_decode_body(self) -> bool:
        (decoded_string, detected_charset) = self.__decode_unknown_charset(self.payload)
        if isinstance(decoded_string, str):
            self.body = decoded_string
            self.body_charset = detected_charset
            return True
        else:
            self.__cannot_decode_body(self.payload, detected_charset)
            return False

    def __decode_unknown_charset(
        self, byte: bytes
    ) -> Tuple[Union[bytes, str], Union[str, None]]:
        detected_charset: Union[str, None] = None
        try:
            detected_charset = self.__detect_charset(byte)

            if detected_charset is not None:
                return (
                    codecs.decode(byte, encoding=detected_charset),
                    detected_charset,
                )
            else:
                return self.__trial_charset_decode(byte)
        except:
            return self.__trial_charset_decode(byte)

    def __trial_charset_decode(
        self, byte: bytes
    ) -> Union[Tuple[str, str], Tuple[bytes, None]]:
        for charset in self.trial_charset_list:
            try:
                decoded_str = codecs.decode(byte, encoding=charset)
                return (decoded_str, charset)
            except UnicodeDecodeError:
                print(f"generaly charset decoding failed: {charset}")
                continue
        else:
            return (byte, None)

    def __cannot_decode_header(
        self,
        name: str,
        default_byte: Union[str, bytes, None],
        detected_charset: Optional[str],
    ) -> None:
        Mail.failed_decode_count += 1
        print(f'---------- Skipped Because cannot decode header ("{name}") ----------')
        print("Text:")
        print(default_byte)
        print("Content charset")
        print(self.header_charset)
        print("Detected Charset:")
        print(detected_charset)

    def __cannot_decode_body(
        self, default_byte: Union[str, bytes, None], detected_charset: Optional[str]
    ) -> None:
        Mail.failed_decode_count += 1
        print("---------- Skipped Because cannot decode body. ----------")
        print("Subject:")
        print(self.subject)
        print("Text:")
        print("{!r:.128}".format(default_byte))
        print("Structure:")
        _structure(self.message)
        print("Last content minetype:")
        print(self.content_maintype, "/", self.content_subtype)
        print("Content charset:")
        print(self.content_charset)
        print("Detected Charset:")
        print(detected_charset)

    def __str__(self) -> str:
        str_list = [
            "-" * 10,
            "Subject: " + str(self.subject),
            "Date: " + str(self.date),
            "To: " + str(self.to_header),
            "From: " + str(self.from_header),
            "cc: " + str(self.cc_header),
            "-" * 10,
            "Body:",
            str(self.body)
        ]

        return "\n".join(str_list)
