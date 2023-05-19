import array
from codecs import CodecInfo
from typing import Callable, Dict, Iterator, List, Tuple, Union


from magmail.decode.mappings import (
    jis90_map,
    jis78_map,
    jis78_target,
    nec_ibm_map,
    nec_map,
)


def decode(byte: Union[bytes, str], error: str = "strict") -> Tuple[str, int]:
    if isinstance(byte, str):
        return (byte, len(byte))

    index = 0
    byte_decoded: List[str] = []
    byte_array: Iterator[int] = iter(array.array("B", byte))
    decode_type: Dict[str, bool] = {
        "ascii": False,
        "katakana": False,
        "jis78": False,
        "jis90": False,
    }

    def set_decode_type(key: str) -> None:
        for value in decode_type.keys():
            decode_type[value] = False
        decode_type[key] = True

    def is_decode_type(key: str) -> bool:
        return decode_type[key]

    def has_decode_type() -> bool:
        return True in decode_type.values()

    def join_hex(first_byte: int, second_byte: int) -> str:
        return hex((first_byte << 8) + second_byte)

    def next_byte(byte_array: Iterator[int]) -> int:
        index += 1
        return next(byte_array)

    try:
        while True:
            byte_1 = next_byte(byte_array)

            if byte_1 == 0x1B:
                byte_1, byte_2 = next_byte(byte_array), next_byte(byte_array)

                if (byte_1, byte_2) == (0x28, 0x42):
                    # US-ASCII ('ESC ( B')
                    set_decode_type("ascii")
                elif (byte_1, byte_2) == (0x28, 0x4A):
                    # JIS X 0201 ラテン文字 ('ESC ( J')
                    set_decode_type("ascii")
                elif (byte_1, byte_2) == (0x28, 0x49):
                    # JIS X 0201 片仮名 ('ESC ( I')
                    set_decode_type("katakana")
                elif (byte_1, byte_2) == (0x24, 0x40):
                    # JIS X 0208:1978 ('ESC $ @')
                    set_decode_type("jis78")
                elif (byte_1, byte_2) == (0x24, 0x42):
                    # JIS X 0208:1997 ('ESC $ B')
                    set_decode_type("jis90")
                else:
                    raise UnicodeDecodeError(
                        'iso_2022_jp_ms',
                        byte,
                        index,
                        index + 1,
                        'invalid start byte'
                    )

            elif has_decode_type():
                if is_decode_type("ascii") and 0x00 <= byte_1 and byte_1 <= 0x7F:
                    # US-ASCII ('ESC ( B')
                    # JIS X 0201 ラテン文字 ('ESC ( J')
                    byte_decoded.append(chr(byte_1))
                elif is_decode_type("katakana") and 0x21 <= byte_1 and byte_1 <= 0x5F:
                    # JIS X 0201 片仮名 ('ESC ( I')
                    byte_decoded.append(chr(byte_1 + 0xFF40))
                elif is_decode_type("jis78"):
                    # JIS X 0208:1978 ('ESC $ @')
                    byte_2 = next_byte(byte_array)

                    if (
                        (0x21 <= byte_1 and byte_1 <= 0x28)
                        or (0x30 <= byte_1 and byte_1 <= 0x74)
                    ) and (0x21 <= byte_2 and byte_2 <= 0x7E):
                        joined_byte = join_hex(byte_1, byte_2)
                        if joined_byte in jis78_target:
                            byte_decoded.append(chr(jis78_map.get(joined_byte, 0x0000)))
                        else:
                            byte_decoded.append(chr(jis90_map.get(joined_byte, 0x0000)))
                elif is_decode_type("jis90"):
                    # JIS X 0208:1997 ('ESC $ B')
                    # NEC特殊文字 ('ESC $ B')
                    # NEC選定IBM拡張文字 ('ESC $ B')

                    byte_2 = next_byte(byte_array)

                    if (
                        (0x21 <= byte_1 and byte_1 <= 0x28)
                        or (0x30 <= byte_1 and byte_1 <= 0x74)
                    ) and (0x21 <= byte_2 and byte_2 <= 0x7E):
                        # JIS X 0208:1997 ('ESC $ B')
                        joined_byte = join_hex(byte_1, byte_2)
                        byte_decoded.append(chr(jis90_map.get(joined_byte, 0x0000)))
                    elif (byte_1 == 0x2D) and (0x21 <= byte_2 and byte_2 <= 0x7E):
                        # NEC特殊文字 ('ESC $ B')
                        joined_byte = join_hex(byte_1, byte_2)
                        byte_decoded.append(chr(nec_map.get(joined_byte, 0x0000)))
                    elif (0x79 <= byte_1 and byte_1 <= 0x7C) and (
                        0x21 <= byte_2 and byte_2 <= 0x7E
                    ):
                        # NEC選定IBM拡張文字 ('ESC $ B')
                        joined_byte = join_hex(byte_1, byte_2)
                        byte_decoded.append(chr(nec_ibm_map.get(joined_byte, 0x0000)))
    except StopIteration:
        decoded_string = "".join(byte_decoded)

    return decoded_string, len(decoded_string)

def search_iso_2022_jp_ms(name: str) -> Union[None, CodecInfo]:
    alias_name: List[str] = [
        "iso_2022_jp_ms",
        "iso-2022-jp-ms",
        "iso2022_jp_ms",
        "iso2022-jp-ms",
        "iso2022jp_ms",
        "iso2022jp-ms",
    ]

    if name not in alias_name:
        return None

    return CodecInfo(name="iso2022_jp_ms", encode=None, decode=decode) # type: ignore
