import re
import codecs
import chardet
from datetime import datetime
from mailbox import mboxMessage
from email.message import Message
from email.header import decode_header
from email.iterators import _structure
from email.utils import parsedate_to_datetime
from typing import Tuple, Union, List, Dict

class Mail:
    decode_error_count = 0

    def __init__(self, message: Union[Message, mboxMessage], auto_clean: bool = True):
        self.message: Union[Message, mboxMessage] = message
        self.auto_clean: bool = auto_clean
        self.is_multipart: bool = False
        self.default_decode_charset: List[str] = [
            "utf-8",
            "cp932",
            "shift-jis",
            "base64",
        ]
        self.images: List[bytes] = []

        self.__subject = self._get_header("Subject")
        self.__date = self._get_header("Date")
        self.__to_address = self._get_header("To")
        self.__cc_address = self._get_header("Cc")
        self.__from_address = self._get_header("From")

        for part in self.message.walk():
            self.content_maintype = part.get_content_maintype()
            self.content_subtype = part.get_content_subtype()

            if self.content_maintype == "multipart":
                self.is_multipart = True
                continue

            if self.content_maintype == "image":
                self.images.append(part.get_payload())
                continue

            self.attach_file_list: List[Dict[str, Union[str, bytes]]] = []

            attach_fname = part.get_filename()

            if attach_fname is None:
                self.payload = part.get_payload(decode=True)
                self.charset = part.get_content_charset()

                try:
                    if self.payload and self.charset:
                        try:
                            self.body = codecs.decode(
                                self.payload, encoding=self.charset
                            )
                        except:
                            if not self.__is_canable_decode_body():
                                continue
                    elif self.payload:
                        if not self.__is_canable_decode_body():
                            continue
                    else:
                        self.body = ""
                except:
                    decoded_payload, detected_charset = self.__generaly_charset_decode(
                        self.payload
                    )
                    if type(decoded_payload) is bytes:
                        self.body = decoded_payload
                    else:
                        self.__cannot_decode_body(self.payload, detected_charset)
            else:
                self.attach_file_list.append(
                    {"name": attach_fname, "data": part.get_payload(decode=True)}
                )

        if auto_clean:
            self.body = self._body_clean_text(self.body)

    @property
    def subject(self):
        subject = self.__subject
        if self.auto_clean:
            subject = self._header_clean_text(subject)

        return subject

    @property
    def date(self) -> datetime:
        return parsedate_to_datetime(self.__date)

    @property
    def to_address(self) -> str:
        return self.__to_address

    @property
    def cc_address(self) -> str:
        return self.__cc_address

    @property
    def from_address(self) -> str:
        return self.__from_address

    def has_file(self):
        return len(self.attach_file_list) > 0

    def has_image(self):
        return len(self.images) > 0

    def _get_header(self, name: str) -> Union[List[Union[str, None]], Union[str, None]]:
        if self.message[name]:
            header_list = []
            for byte, charset in decode_header(self.message[name]):
                header = ""
                if type(byte) is bytes:
                    if charset:
                        self.header_charset = charset
                        try:
                            header += codecs.decode(byte, charset)
                            header_list.append(header)
                            continue
                        except:
                            pass

                    (decoded_header, detected_charset) = self.__decode_unknown_charset(
                        byte
                    )

                    if type(decoded_header) is str:
                        header += decoded_header
                    else:
                        self.__cannot_decode_header(
                            name, decoded_header, detected_charset
                        )
                        continue
                elif type(byte) is str:
                    header += byte
                header_list.append(header)

            if len(decode_header(self.message[name])) > 1:
                return header_list
            elif header_list:
                return header_list[0]


    def _header_clean_text(self, header_values):
        def clean(text):
            text = text.replace("\r", "\n")
            text = text.replace("\n", "")
            text = "".join(text.splitlines())
            text = text.strip()
            text = re.sub(r"http\S+", " ", text)
            text = re.sub(r"\u3000", "", text)

            return text

        if not header_values is None:
            if type(header_values) is list:
                return [clean(text) for text in header_values]
            else:
                return clean(header_values)
        return header_values

    def _body_clean_text(self, clean_text):
        if not clean_text is None:
            # 小文字化
            clean_text = clean_text.lower()
            # Styleタグの削除
            clean_text = re.sub(r'<style(.|\s)*?<\/(no)?style>', "", clean_text)
            # Scriptタグの削除
            clean_text = re.sub(r'<(no)?script(.|\s)*?<\/(no)?script>', "", clean_text)
            # HTMLタグの削除
            clean_text = re.sub(r"<(\"[^\"]*\"|\'[^\']*\'|[^\'\">])*>", "", clean_text)
            # 複数タブ削除
            clean_text = re.sub(r"\t+", "", clean_text)
            # スペース削除
            clean_text = re.sub(r"\s+", "", clean_text)
            # 行末記号を統一
            clean_text = clean_text.replace("\r\n", "\n")
            # 行末記号を統一
            clean_text = clean_text.replace("\r", "\n")
            # Unicodeの全角スペースを削除
            clean_text = re.sub(r"\u3000", "", clean_text)
            # URLの除去
            clean_text = re.sub(r"http\S+", " ", clean_text)
            # メールアドレスの除去
            clean_text = re.sub(
                r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", " ", clean_text
            )
            # 全角空白の除去
            clean_text = re.sub(r"　", " ", clean_text)
            # {}の中身を消す
            clean_text = re.sub(r"{.*?}", " ", clean_text)
            # &と;の中身を消す
            clean_text = re.sub(r"&.*?;", " ", clean_text)
            # 末尾の空白・改行コードの削除
            clean_text = "".join(clean_text.splitlines())

        return clean_text

    def __detect_charset(self, byte: bytes) -> Union[str, None]:
        detected_charset = chardet.detect(byte)["encoding"]
        if detected_charset == "SHIFT_JIS":
            detected_charset = "CP932"
        if detected_charset == "ISO-2022-JP":
            detected_charset = "CP932"

        return detected_charset

    def __is_canable_decode_body(self) -> bool:
        (
            decoded_string,
            detected_charset,
        ) = self.__decode_unknown_charset(self.payload)
        if type(decoded_string) is str:
            self.body = decoded_string
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
                return self.__generaly_charset_decode(byte)
        except:
            return self.__generaly_charset_decode(byte)

    def __generaly_charset_decode(
        self, byte: bytes
    ) -> Union[Tuple[str, str], Tuple[bytes, None]]:
        for charset in self.default_decode_charset:
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
        name,
        default_string,
        detected_charset,
    ) -> None:
        Mail.decode_error_count += 1
        print(f"---------- Skipped Because cannot decode header ({name}) ----------")
        print("Text:")
        print(default_string)
        print("Content charset")
        print(self.header_charset)
        print("Detected Charset:")
        print(detected_charset)

    def __cannot_decode_body(
        self,
        default_string,
        detected_charset,
    ) -> None:
        Mail.decode_error_count += 1
        print("---------- Skipped Because cannot decode body. ----------")
        print("Subject:")
        print(self.subject)
        print("Text:")
        print(default_string[:129])
        print("Structure:")
        _structure(self.message)
        print("Last content minetype:")
        print(self.content_maintype, "/", self.content_subtype)
        print("Content charset:")
        print(self.charset)
        print("Detected Charset:")
        print(detected_charset)

    def __str__(self):
        str_list = [
            str(i)
            for i in [
                self.subject,
                self.date,
                self.to_address,
                self.cc_address,
                self.from_address,
                self.body,
                self.attach_file_list,
            ]
        ]

        return "\n".join(str_list)