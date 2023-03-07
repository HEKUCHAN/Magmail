import re
from re import Pattern
from typing import Callable, Dict, List, Optional, Union

# VARIABLES
DEFAULT_AUTO_CLEAN = True


# REGEX
ADDRESS_HEADER_REGEX: Pattern = re.compile(
    r"[^, ].+?<[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}>|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)

HEADER_NAME_REGEX: Pattern = re.compile(r".*?[^\s](?=<|\s+<)")

HEADER_MAIL_REGEX: Pattern = re.compile(
    r"([^<>](?<=<)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?=>)|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
)

NEW_LINE_REGEX: Pattern = re.compile(r"\\R")

URL_REGEX: Pattern = re.compile(
    r"(https?)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)"
)

HTML_TAG_REGEX: Pattern = re.compile(r"<(\"[^\"]*\"|\'[^\']*\'|[^\'\">])*>")

HTML_COMMENTS_REGEX: Pattern = re.compile(r"<!--[\s\S]*?-->*")

HTML_STYLE_TAG_REGEX: Pattern = re.compile(r"<style.*?>[\s\S]*<\/style>*")

HTML_SCRIPT_TAG_REGEX: Pattern = re.compile(r"<script.*?>[\s\S]*<\/script>*")

MAIL_ADDRESS_REGEX: Pattern = re.compile(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
)

TABS_REGEX: Pattern = re.compile(r"\t+")

FULL_WITH_SPACE_REGEX: Pattern = re.compile(r"　")

UNICODE_FULL_WITH_SPACE_REGEX: Pattern = re.compile(r"\u3000")

IDENTIFIER = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)

SPACES_REGEX: Pattern = re.compile(r"\s+")

# List
DEFAULT_COLUMNS: List[str] = ["subject", "date", "to", "cc", "h_from", "body_plain"]


# Dict
DEFAULT_CUSTOM_CLEAN_FUNCTIONS_DICT: Dict[str, Optional[Callable[[str], str]]] = {
    "all": None,
    "headers": None,
    "body": None,
}

FILTER_CONTENTS_TYPE = Union[str, List[str]]
DEFAULT_FILTER_CONTENTS_DICT: Dict[str, FILTER_CONTENTS_TYPE] = {"content_type": []}
