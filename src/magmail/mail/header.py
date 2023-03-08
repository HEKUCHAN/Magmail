from email.header import decode_header
from typing import Any, Callable, Iterator, Optional, List, Tuple

from magmail.decode import _Decoder
from magmail.static import NEW_LINE_REGEX, URL_REGEX, SPACES_REGEX, DEFAULT_AUTO_CLEAN


class _Header:
    def __init__(
        self,
        header: Tuple[str, Any],
        auto_clean: bool = DEFAULT_AUTO_CLEAN,
        custom_clean_function: Optional[Callable[[str], str]] = None,
    ) -> None:
        self.field, self.body = header
        self.encoding: List[Optional[str]] = []
        self.custom_clean_function = custom_clean_function
        self.auto_clean = auto_clean

        self.decode()

    def __iter__(self) -> Iterator[str]:
        return iter([self.field, self.body])

    def decode(self) -> None:
        body_parts = []
        for byte, encoding in decode_header(self.body):
            if isinstance(byte, bytes):
                self.decoder: _Decoder = _Decoder(byte=byte, encoding=encoding)
                self.decoder.decode()

                self.encoding.append(self.decoder.encoding)

                body_parts.append(self.decoder.decoded)
            elif isinstance(byte, str):
                self.encoding.append(None)
                body_parts.append(byte)

        self.body = "".join(body_parts)

        if self.auto_clean:
            self.body = self.clean_header_value(self.body)

    def clean_header_value(self, value: str) -> str:
        value = NEW_LINE_REGEX.sub("", value)
        value = value.strip()
        value = URL_REGEX.sub(" ", value)
        value = SPACES_REGEX.sub(" ", value)

        if self.custom_clean_function is not None:
            value = self.custom_clean_function(value)

        return value
