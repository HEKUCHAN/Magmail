import codecs
import chardet
from typing import Callable, Optional, Union

from magmail.errors import CannotDetectEncodingError
from magmail.variant_charset import VARIANTS_CHARSET

class Decoder:
    def __init__(
        self,
        byte: bytes,
        encoding: str,
    ):
        self.byte = byte
        self.encoding: Optional[str] = encoding
        self.original_encoding: Optional[str] = None

    def detect_charset(self):
        self.original_encoding = self.encoding
        self.encoding = chardet.detect(self.byte)["encoding"]

    def decode(self):
        if self.encoding:
            try:
                self.decoded = codecs.decode(self.byte, encoding=self.encoding)
            except UnicodeDecodeError:
                self.variant_decode()
        else:
            self.detect_charset()
            self.decode()

    def variant_decode(self):
        variant_encoding: Union[str, Callable[[bytes], str]] = self.encoding.upper()
        if variant_encoding in VARIANTS_CHARSET:
            if callable(VARIANTS_CHARSET[variant_encoding]):
                self.decoded = variant_encoding(self.byte)
            else:
                for variant_charset in VARIANTS_CHARSET[variant_encoding]:
                    try:
                        self.decoded = codecs.decode(self.byte, encoding=variant_charset)
                        self.encoding = variant_charset
                    except UnicodeDecodeError:
                        if self.original_encoding is None:
                            self.detect_charset()
                            self.decode()
                        else:
                            raise CannotDetectEncodingError("Can't detect encoding, Please tell to owner.")
        else:
            raise CannotDetectEncodingError("Can't detect encoding, Please tell to owner.")