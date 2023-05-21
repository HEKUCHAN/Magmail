ISO2022_JP_SIMILAR_CHARSET_LIST = [
    "iso2022_jp",
    "iso2022_jp_ext",
    "iso2022_jp_ms",
    "iso2022_jp_1",
    "iso2022_jp_2",
    "iso2022_jp_2004",
    "iso2022_jp_3",
]

CP932_SIMILAR_CHARSET = ["cp932", "shift_jis", "shift_jis_2004", "shift_jisx0213"]

EUC_JP_SIMILAR_CHARSET = ["euc_jp", "euc_jis_2004", "euc_jisx0213"]

ASCII_SIMILAR_CHARSET = ["ascii", "utf_8"]

SIMILAR_CHARSET_LIST = [
    ISO2022_JP_SIMILAR_CHARSET_LIST,
    CP932_SIMILAR_CHARSET,
    EUC_JP_SIMILAR_CHARSET,
    ASCII_SIMILAR_CHARSET,
]

SIMILAR_CHARSET_DICT = {
    charset: list(filter(lambda x: x != charset, charset_list))
    for charset_list in SIMILAR_CHARSET_LIST
    for charset in charset_list
}
