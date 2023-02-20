import re
from re import Pattern
from typing import Callable, Dict, List, Optional

# VARIABLES
DEFAULT_AUTO_CLEAN = False


# REGEX
ADDRESS_HEADER_REGEX: Pattern[str] = re.compile(
    r"[^, ].+?<[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}>|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)

HEADER_NAME_REGEX: Pattern[str] = re.compile(r".*?[^\s](?=<|\s+<)")

HEADER_MAIL_REGEX: Pattern[str] = re.compile(
    r"([^<>](?<=<)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?=>)|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
)

NEW_LINE_REGEX: Pattern[str] = re.compile(r"\\R")

URL_REGEX: Pattern[str] = re.compile(r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+")

SPACES_REGEX: Pattern[str] = re.compile(r"\s+")

# List
DEFAULT_COLUMNS: List[str] = [
    "subject",
    "date",
    "to_header",
    "cc_header",
    "from_header",
    "body",
    "has_file",
    "attach_file_list",
    "has_image",
    "is_multipart",
    "has_delivered_to",
]

# Dict
DEFAULT_CUSTOM_FUNCTIONS_DICT: Dict[str, Optional[Callable[[str], str]]] = {
    "all": None,
    "headers": None,
    "body": None,
}
