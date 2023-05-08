import shortuuid

def generate_email():
    return f"{shortuuid.uuid()}@{shortuuid.uuid()}.{shortuuid.uuid()}"

