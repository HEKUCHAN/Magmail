from typing import Any
from faker import Faker

fake = {"en": Faker("en-US"), "ja": Faker("ja_JP")}

DEFAULT_LOCAL = "ja"


def gen_email(lang: str = DEFAULT_LOCAL) -> Any:
    return fake[lang].email()


def gen_name(lang: str = DEFAULT_LOCAL) -> Any:
    return fake[lang].name()


def gen_word(length: int = 250, lang: str = DEFAULT_LOCAL) -> Any:
    return fake[lang].text(max_nb_chars=length)
