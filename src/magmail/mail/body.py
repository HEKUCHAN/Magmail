import html
from pathlib import Path
from mailbox import mboxMessage
from email.message import Message
from typing import Callable, Dict, Optional, Union


from magmail.decode import Decoder
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
    FILTER_CONTENTS_TYPE,
    HTML_SCRIPT_TAG_REGEX,
    FULL_WITH_SPACE_REGEX,
    UNICODE_FULL_WITH_SPACE_REGEX,
)


class _Body:
    def __init__(
        self,
        message: Union[Message, mboxMessage],
        auto_clean: bool = DEFAULT_AUTO_CLEAN,
        filters: Dict[str, FILTER_CONTENTS_TYPE] = {},
        custom_clean_function: Optional[Callable[[str], str]] = None,
    ) -> None:
        self.body: Dict[str, str] = {"html": "", "text": ""}
        self.original_body: Dict[str, str] = {"html": "", "text": ""}
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
            self.original_body = self.body.copy()
            self.body = {key: self.clean_body_value(value) for key, value in self.body.items()}

    def walk(self):
        def get_body():
            if self.payload:
                if isinstance(self.payload, str):
                    return self.payload

                self.decoder: Decoder = Decoder(
                    byte=self.payload, encoding=self.content_charset
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
                and content_type not in self.filters["content_type"]
            ):
                continue

            if content_maintype == "multipart":
                self.has_multipart = True
                continue

            if content_maintype == "image":
                continue

            if attach_fname is not None:
                continue

            self.payload = part.get_payload(decode=True)
            self.content_charset = part.get_content_charset()

            if content_type == "text/plain":
                self.body["text"] = get_body()
            elif content_type == "text/html":
                self.body["html"] = get_body()

    def clean_body_value(self, body_value: str) -> str:
        def clean(value: str) -> str:
            value = HTML_COMMENTS_REGEX.sub("", value)
            value = HTML_STYLE_TAG_REGEX.sub("", value)
            value = HTML_SCRIPT_TAG_REGEX.sub("", value)
            value = HTML_TAG_REGEX.sub("", value)

            value = NEW_LINE_REGEX.sub("\n", value)

            value, self.total_urls = URL_REGEX.subn("%URL%", value)

            value, self.total_addresses = MAIL_ADDRESS_REGEX.subn(
                "%MAIL_ADDRESS%", value
            )

            value = html.unescape(value)

            value = value.strip()
            value = TABS_REGEX.sub("", value)
            value = FULL_WITH_SPACE_REGEX.sub("", value)
            value = UNICODE_FULL_WITH_SPACE_REGEX.sub("", value)
            value = SPACES_REGEX.sub(" ", value)

            if self.custom_clean_function is not None:
                value = self.custom_clean_function(value)

            return value

        return clean(body_value)
