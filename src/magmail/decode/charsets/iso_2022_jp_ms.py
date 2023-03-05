from codecs import CodecInfo


def search_iso_2022_jp_ms(name):
    alias_name = [
        'iso_2022_jp_ms',
        'iso-2022-jp-ms',
        'iso2022_jp_ms',
        'iso2022-jp-ms',
        'iso2022jp_ms',
        'iso2022jp-ms',
    ]

    if name not in alias_name:
        return None

    return CodecInfo(
        name='iso2022_jp_ms',
        encode=None,
        decode=None
    )
