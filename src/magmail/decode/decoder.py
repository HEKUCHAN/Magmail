import codecs
import chardet
from typing import Callable, Optional, Union

from magmail.errors import CannotDetectEncodingError
from magmail.variant_charset import VARIANT_CHARSETS, STR_OR_CALLABLE_DICT_TYPE


class Decoder:
    def __init__(self, byte: bytes, encoding: Optional[str]) -> None:
        self.byte = byte
        self.encoding: Optional[str] = encoding
        self.original_encoding: Optional[str] = None

    def detect_charset(self) -> None:
        self.original_encoding = self.encoding
        self.encoding = chardet.detect(self.byte)["encoding"]

        if self.encoding is None:
            raise CannotDetectEncodingError(
                "Can't detect encoding, Please tell to owner."
            )

    def decode(self) -> None:
        if self.encoding:
            try:
                self.decoded = codecs.decode(self.byte, encoding=self.encoding)
            except UnicodeDecodeError:
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
            except UnicodeDecodeError:
                if self.original_encoding is None:
                    self.detect_charset()
                    self.decode()

                raise CannotDetectEncodingError(
                    "Can't detect encoding, Please tell to owner."
                )

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

        raise CannotDetectEncodingError("Can't detect encoding, Please tell to owner.")
