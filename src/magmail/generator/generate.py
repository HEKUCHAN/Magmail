import shortuuid


def generate_email() -> str:
    return f"{shortuuid.uuid()}@{shortuuid.uuid()}.{shortuuid.uuid()}"
