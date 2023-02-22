import codecs
import chardet
from enum import Enum
from typing import Callable, Optional, Union

from magmail.errors import CannotDetectEncodingError
from magmail.variant_charset import VARIANT_CHARSETS, STR_OR_CALLABLE_DICT_TYPE


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
        # self.decoded: str = ""

    def detect_charset(self) -> None:
        self.original_encoding = self.encoding
        self.encoding = chardet.detect(self.byte)["encoding"]

        if self.encoding is None:
            self._decode_error()

    def decode(self) -> None:
        if self.encoding:
            try:
                self.decoded = codecs.decode(self.byte, encoding=self.encoding)
            except (UnicodeDecodeError, LookupError):
                self.variant_decode()
        else:
            self.detect_charset()
            self.decode()

    def variant_decode(self) -> None:
        def try_decode(
            byte: bytes, decoder: Union[str, Callable[[bytes], str]]
        ) -> None:
            try:
                if callable(decoder):
                    self.decoded = decoder(byte)
                    return None

                codecs.decode(self.byte, encoding=decoder)
                self.encoding = decoder
            except (UnicodeDecodeError, LookupError):
                pass

        if self.encoding is None:
            self.detect_charset()
            assert self.encoding is not None

        variant_encoding: str = self.encoding.upper()
        if variant_encoding in VARIANT_CHARSETS:
            variant_decoder: STR_OR_CALLABLE_DICT_TYPE = VARIANT_CHARSETS[
                variant_encoding
            ]

            for variant_charset in variant_decoder.values():
                try_decode(self.byte, variant_charset)

        if self.original_encoding is None:
            self.detect_charset()
            self.decode()

        self._decode_error()

    def _warning_decode(self):
        print("Warning!!! Decoding")
        print(self.byte)
        print(self.encoding)
        self.decoded = ""

    def _decode_error(self):
        if self.errors is None or self.errors == "warning":
            self._warning_decode()
        elif self.errors == "ignore":
            pass
        elif self.errors == "exception":
            raise CannotDetectEncodingError("Can't detect charset, so cannot to decode")
