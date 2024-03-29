import re
from re import Pattern
from email.utils import parsedate_to_datetime
from typing import Dict, List, Optional

from magmail.types import (
    CUSTOM_FUNCTIONS_DICT_TYPE,
    CUSTOM_FUNCTIONS_ROOT_DICT_TYPE,
    FILTER_CONTENTS_TYPE,
)

# VARIABLES
DEFAULT_AUTO_CLEAN = True

# REGEX
ADDRESS_HEADER_REGEX = re.compile(
    r"[^, ].+?<[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}>|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)

HEADER_NAME_REGEX = re.compile(r".*?[^\s](?=<|\s+<)")

HEADER_MAIL_REGEX = re.compile(
    r"([^<>](?<=<)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?=>)|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
)

NEW_LINE_REGEX = re.compile(r"\\R")

URL_REGEX = re.compile(r"(https?)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)")

HTML_TAG_REGEX = re.compile(r"<(\"[^\"]*\"|\'[^\']*\'|[^\'\">])*>")

HTML_COMMENTS_REGEX = re.compile(r"<!--[\s\S]*?-->*")

HTML_STYLE_TAG_REGEX = re.compile(r"<style.*?>[\s\S]*<\/style>*")

HTML_SCRIPT_TAG_REGEX = re.compile(r"<script.*?>[\s\S]*<\/script>*")

MAIL_ADDRESS_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

TABS_REGEX = re.compile(r"\t+")

FULL_WITH_SPACE_REGEX = re.compile(r"　")

UNICODE_FULL_WITH_SPACE_REGEX = re.compile(r"\u3000")

SPACES_REGEX = re.compile(r"\s+")

# List
DEFAULT_COLUMNS: List[str] = ["subject", "date", "to", "cc", "h_from", "body_plain"]


# Dict
CUSTOM_FUNCTIONS_DICT: CUSTOM_FUNCTIONS_ROOT_DICT_TYPE = {
    "headers": {},
    "clean_functions": {"all": None, "body": None, "header": None},
}

CHANGE_HEADER_TYPE_FUNCTIONS: Optional[CUSTOM_FUNCTIONS_DICT_TYPE] = {
    "Date": parsedate_to_datetime
}

DEFAULT_FILTER_CONTENTS_DICT: Dict[str, FILTER_CONTENTS_TYPE] = {"content_type": []}
