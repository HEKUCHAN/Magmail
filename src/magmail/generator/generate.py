import random
import shortuuid


def generate_email() -> str:
    return f"{shortuuid.uuid()[:10]}@{shortuuid.uuid()[:4]}.{shortuuid.uuid(pad_length=3)[:3]}"


def generate_japanese(length: int = 20) -> str:
    return "".join(chr(random.choice(range(0x4E00, 0x9FD5))) for _ in range(length))
