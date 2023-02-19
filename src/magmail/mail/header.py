import re
import codecs
from email.header import decode_header
from typing import Any, Callable, Optional ,List, Tuple, Union, overload

from magmail.decode import Decoder
from magmail.static import (
    NEW_LINE_REGEX,
    URL_REGEX,
    SPACES_REGEX,
    DEFAULT_AUTO_CLEAN
)

class _Header:
    def __init__(
        self,
        header: Tuple[str, Any],
        auto_clean: bool = DEFAULT_AUTO_CLEAN,
        custom_clean_function: Optional[Callable[[str], str]] = None
    ) -> None:
        self.field, self.body = header
        self.encoding = []
        self.custom_clean_function = custom_clean_function
        self.auto_clean = auto_clean

        self.decode()

    def decode(self):
        body_parts = []
        for byte, encoding in decode_header(self.body):
            if isinstance(byte, bytes):
                decoder: Decoder = Decoder(byte=byte, encoding=encoding)
                decoder.decode()

                body_parts.append(decoder.decoded)
            elif isinstance(byte, str):
                body_parts.append(byte)

        body = "".join(body_parts)

        if self.auto_clean:
            body = self.clean_header_value(body)

        self.body = body
    @overload
    def clean_header_value(self, header_value: None) -> None:
        ...

    @overload
    def clean_header_value(self, header_value: str) -> str:
        ...

    @overload
    def clean_header_value(self, header_value: List[str]) -> List[str]:
        ...

    def clean_header_value(
        self,
        header_values: Union[Optional[str], List[str]]
    ):
        def clean(value: str) -> str:
            value = NEW_LINE_REGEX.sub('', value)
            print(value)
            value = value.strip()
            value = URL_REGEX.sub(" ", value)
            value = SPACES_REGEX.sub(" ", value)

            if self.custom_clean_function is not None:
                value = self.custom_clean_clean(value)

            return value

        print(clean('i=1; a=rsa-sha256; c=relaxed/relaxed; d=google.com; s=arc-20160816;\r\n        h=message-id:mime-version:subject:to:reply-to:from:date\r\n         :dkim-signature;\r\n        bh=Ei3/HQJPcOuLp+Z9XRWD68WQoxShRWCww5c7scEPB7U=;\r\n        b=aVLbrnnECPJ3LynJPLdUtBPNVRZG1D4p7nG1RmkwFk51sLmaPRzzFFmS6vrbBmmwIX\r\n         ZAYqGdoAcn0N5iBLSBPOmOn4r0r8Ci34R8xulursS7BffUIVXZ+m011NxvqKwsXh/0Ab\r\n         ve0LGT7GU3TEP/7upNordNlKS7O29ajbMaLMpm4BDyeSuZ/9VI5zfgd2VrbIgaQOJ1r8\r\n         Ge/4wb278bEk5ujfmDhrYqnW7SHdDRq7pm3kqJdi2SIB2EIXGPACem6kiEbeMTOTic3C\r\n         56dnVuBnifpDlWaXLfuwQdLMA9Mc8bqT+guO6yETC+0vhjw7O4mNi4QhbkJU24gTYd8I\r\n         X0+g=='))

        if header_values is not None:
            if isinstance(header_values, list):
                return [clean(value) for value in header_values]
            else:
                return clean(header_values)
        return header_values
