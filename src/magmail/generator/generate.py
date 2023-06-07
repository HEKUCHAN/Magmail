import random
import shortuuid
from typing import Dict, Union
from faker import Faker
from collections import OrderedDict

fake = {"en": Faker("en-US"), "ja": Faker("ja_JP")}

DEFAULT_LOCAL = "ja"


def gen_email(lang: str = DEFAULT_LOCAL) -> str:
    return fake[lang].email()


def gen_name(lang: str = DEFAULT_LOCAL) -> str:
    return fake[lang].name()


def gen_word(length: int = 250, lang: str = DEFAULT_LOCAL) -> str:
    return fake[lang].text(max_nb_chars=length)
