from typing import List, Dict

# REGEX
ADDRESS_HEADER_REGEX = r"[^, ].+?<[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}>|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
HEADER_NAME_REGEX = r".*?[^\s](?=<|\s+<)"
HEADER_MAIL_REGEX = r"([^<>](?<=<)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?=>)|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"

# List
TRIAL_CHARSET_LIST: List[str] = ["utf-8", "cp932", "shift-jis", "base64"]
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

# Dictionary
EXTENSION_CHARSET_DICT: Dict[str, str] = {"SHIFT_JIS": "CP932", "ISO-2022-JP": "CP932"}
