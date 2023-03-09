import codecs
import chardet
from enum import Enum
from typing import Callable, Optional, Union

from magmail.errors import CannotDetectEncodingError, UnknownEncodingType
from magmail.decode.charsets import search_iso_2022_jp_ms
from magmail.similar_charset import SIMILAR_CHARSET_DICT


codecs.register(search_iso_2022_jp_ms)


class _Decoder:
    def __init__(
        self,
        byte: bytes,
        encoding: Optional[str],
        errors: Optional[str] = None,
    ) -> None:
        self.byte = byte
        self.encoding: Optional[str] = encoding
        self.errors = errors
        self.original_encoding: Optional[str] = None
        self.decoded = ""

    def detect_charset(self) -> None:
        self.original_encoding = self.encoding
        self.encoding = chardet.detect(self.byte)["encoding"]

        if self.encoding is None:
            self.__decode_error()

    def decode(self) -> None:
        if self.encoding:
            try:
                if self.encoding == "unknown-8bit":
                    self.encoding = "shift-jis"

                codecs.lookup(self.encoding)
                try:
                    self.decoded = codecs.decode(self.byte, encoding=self.encoding)
                except (UnicodeDecodeError, LookupError):
                    self.variant_decode()
            except LookupError:
                self.__unknown_encoding_error()
        else:
            self.detect_charset()
            self.decode()

    def variant_decode(self) -> None:
        if self.encoding is None:
            self.detect_charset()
            assert self.encoding is not None

        try:
            self.encoding = codecs.lookup(self.encoding).name
        except LookupError:
            pass

        if self.encoding.lower() in SIMILAR_CHARSET_DICT.keys():
            for similar_charset in SIMILAR_CHARSET_DICT[self.encoding.lower()]:
                try:
                    self.decoded = codecs.decode(self.byte, encoding=similar_charset)
                    self.encoding = similar_charset
                    return
                except (UnicodeDecodeError, LookupError):
                    continue

        if self.original_encoding is None:
            self.detect_charset()
            self.decode()
            return

        self.__decode_error()

    def _warning_decode(self) -> None:
        print("Warning!!! Decoding")
        print("Encoding:", self.encoding)
        print("Body: ")
        print(self.byte)
        print("=" * 32)

    def __unknown_encoding_error(self) -> None:
        if self.errors == "warning" or self.errors is None:
            print("UNKNOWN")
            self._warning_decode()
        elif self.errors == "exception":
            raise UnknownEncodingType("Can't detect charset, so cannot to decode")
        elif self.errors == "ignore":
            pass

    def __decode_error(self) -> None:
        if self.errors == "warning" or self.errors is None:
            print("ERROR")
            self._warning_decode()
        elif self.errors == "exception":
            raise CannotDetectEncodingError("Can't detect charset, so cannot to decode")
        elif self.errors == "ignore":
            pass
