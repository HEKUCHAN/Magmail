import re
from re import Pattern
from email.utils import parsedate_to_datetime
from typing import Any, Callable, Dict, List, Optional, Union

# VARIABLES
DEFAULT_AUTO_CLEAN = True

# Type
FILTER_CONTENTS_TYPE = Union[str, List[str]]
CUSTOM_FUNCTIONS_DICT_TYPE = Dict[str, Optional[Callable[[Any], Any]]]
CUSTOM_FUNCTIONS_ROOT_DICT_TYPE = Dict[str, CUSTOM_FUNCTIONS_DICT_TYPE]
DEFAULT_FILTER_CONTENTS_DICT: Dict[str, FILTER_CONTENTS_TYPE] = {"content_type": []}

# REGEX
ADDRESS_HEADER_REGEX: Pattern[str] = re.compile(
    r"[^, ].+?<[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}>|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)

HEADER_NAME_REGEX: Pattern[str] = re.compile(r".*?[^\s](?=<|\s+<)")

HEADER_MAIL_REGEX: Pattern[str] = re.compile(
    r"([^<>](?<=<)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?=>)|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
)

NEW_LINE_REGEX: Pattern[str] = re.compile(r"\\R")

URL_REGEX: Pattern[str] = re.compile(
    r"(https?)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)"
)

HTML_TAG_REGEX: Pattern[str] = re.compile(r"<(\"[^\"]*\"|\'[^\']*\'|[^\'\">])*>")

HTML_COMMENTS_REGEX: Pattern[str] = re.compile(r"<!--[\s\S]*?-->*")

HTML_STYLE_TAG_REGEX: Pattern[str] = re.compile(r"<style.*?>[\s\S]*<\/style>*")

HTML_SCRIPT_TAG_REGEX: Pattern[str] = re.compile(r"<script.*?>[\s\S]*<\/script>*")

MAIL_ADDRESS_REGEX: Pattern[str] = re.compile(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
)

TABS_REGEX: Pattern[str] = re.compile(r"\t+")

FULL_WITH_SPACE_REGEX: Pattern[str] = re.compile(r"　")

UNICODE_FULL_WITH_SPACE_REGEX: Pattern[str] = re.compile(r"\u3000")

IDENTIFIER = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)

SPACES_REGEX: Pattern[str] = re.compile(r"\s+")

# List
DEFAULT_COLUMNS: List[str] = ["subject", "date", "to", "cc", "h_from", "body_plain"]


# Dict
CUSTOM_FUNCTIONS_DICT: CUSTOM_FUNCTIONS_ROOT_DICT_TYPE = {
    "headers": {},
    "clean_functions": {
        "all": None,
        "body": None,
        "header": None,
    },
}

CHANGE_HEADER_TYPE_FUNCTIONS = {
    "Date": parsedate_to_datetime,
}
