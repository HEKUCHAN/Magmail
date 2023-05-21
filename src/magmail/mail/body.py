import html
from pathlib import Path
from mailbox import mboxMessage
from email.message import Message
from typing import Callable, Dict, Optional, Union


from magmail.decode import _Decoder
from magmail.magmail.filter import _Filter
from magmail.static import (
    URL_REGEX,
    TABS_REGEX,
    SPACES_REGEX,
    NEW_LINE_REGEX,
    HTML_TAG_REGEX,
    MAIL_ADDRESS_REGEX,
    DEFAULT_AUTO_CLEAN,
    HTML_COMMENTS_REGEX,
    HTML_STYLE_TAG_REGEX,
    HTML_SCRIPT_TAG_REGEX,
    FULL_WITH_SPACE_REGEX,
    UNICODE_FULL_WITH_SPACE_REGEX,
)
from magmail.types import FILTER_CONTENTS_TYPE


class _Body:
    def __init__(
        self,
        message: Union[Message, mboxMessage],
        auto_clean: bool = DEFAULT_AUTO_CLEAN,
        filters: Dict[str, FILTER_CONTENTS_TYPE] = {},
        custom_clean_function: Optional[Callable[[str], str]] = None,
    ) -> None:
        self.body: Dict[str, Optional[str]] = {"html": "", "plain": ""}
        self.original_body: Dict[str, Optional[str]] = {"html": "", "plain": ""}
        self.content_charset: Dict[str, Optional[str]] = {"html": "", "plain": ""}
        self.total_urls = 0
        self.total_addresses = 0
        self.message: Union[Message, mboxMessage] = message
        self.auto_clean = auto_clean
        self.filters = _Filter(filters)
        self.custom_clean_function: Optional[
            Callable[[str], str]
        ] = custom_clean_function

        self.walk()

        if self.auto_clean:
            self.body = {
                key: self.clean_body_value(value)
                for key, value in self.body.items()
                if value is not None
            }

        self.body_html = self.body["html"]
        self.body_plain = self.body["plain"]

    def walk(self) -> None:
        def get_body() -> str:
            payload = part.get_payload(decode=True)
            content_charset = part.get_content_charset()
            content_subtype = part.get_content_subtype()

            self.content_charset[content_subtype] = content_charset
            self.original_body[content_subtype] = payload

            if payload:
                if isinstance(payload, str):
                    return payload

                self.decoder: _Decoder = _Decoder(
                    byte=payload, encoding=self.content_charset[content_subtype]
                )
                self.decoder.decode()

                self.encoding = self.decoder.encoding
                self.original_encoding = self.decoder.original_encoding

                return self.decoder.decoded
            else:
                return ""

        for part in self.message.walk():
            attach_fname = part.get_filename()
            content_type = part.get_content_type()
            content_maintype = part.get_content_maintype()
            # self.attach_files = []

            if (
                self.filters.is_has("content_type")
                and content_type in self.filters["content_type"]
            ):
                continue

            if content_maintype == "multipart":
                self.has_multipart = True
                continue

            if content_maintype == "image":
                continue

            if attach_fname is not None:
                continue

            if content_type == "text/plain":
                self.body["plain"] = get_body()
            elif content_type == "text/html":
                self.body["html"] = get_body()

    def clean_body_value(self, value: str) -> str:
        value = HTML_COMMENTS_REGEX.sub("", value)
        value = HTML_STYLE_TAG_REGEX.sub("", value)
        value = HTML_SCRIPT_TAG_REGEX.sub("", value)
        value = HTML_TAG_REGEX.sub("", value)

        value = NEW_LINE_REGEX.sub("\n", value)

        value, self.total_urls = URL_REGEX.subn("%URL%", value)

        value, self.total_addresses = MAIL_ADDRESS_REGEX.subn("%MAIL_ADDRESS%", value)

        value = html.unescape(value)

        value = value.strip()
        value = TABS_REGEX.sub("", value)
        value = FULL_WITH_SPACE_REGEX.sub("", value)
        value = UNICODE_FULL_WITH_SPACE_REGEX.sub("", value)
        value = SPACES_REGEX.sub(" ", value)

        if self.custom_clean_function is not None:
            value = self.custom_clean_function(value)

        return value
