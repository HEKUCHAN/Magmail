from typing import Callable, Dict, TypeAlias, Union

STR_OR_CALLABLE_DICT_TYPE: TypeAlias = Dict[str, Union[str, Callable[[bytes], str]]]


def example(string: bytes) -> str:
    return string.decode("utf-8")


ISO_2022_JP_VARIANTS: STR_OR_CALLABLE_DICT_TYPE = {
    "ISO-2022-JP-MS": example,
    "ISO-2022-JP-EXT": "iso2022_jp_ext",
    "ISO-2022-JP-2004": "iso2022_jp_2004",
    "ISO-2022-JP-1": "iso2022_jp_1",
    "ISO-2022-JP-2": "iso2022_jp_2",
    "ISO-2022-JP-3": "iso2022_jp_3",
}

SHIFT_JIS_VARIANTS: STR_OR_CALLABLE_DICT_TYPE = {
    "Shift_JIS": "shift_jis",
    "CP932": "cp932",
    "Shift_JIS-2004": "shift_jis_2004",
    "Shift_JISX0213": "shift_jisx0213",
}

VARIANT_CHARSETS: Dict[str, STR_OR_CALLABLE_DICT_TYPE] = {
    "SHIFT_JIS": SHIFT_JIS_VARIANTS,
    "ISO-2022-JP": ISO_2022_JP_VARIANTS,
}
