import os
import random
from typing import List, Union

from magmail.generator import Seed, gen_email, gen_word, gen_name
from magmail.types import HEADER_TYPE


os.chdir(os.path.dirname(os.path.abspath(__file__)))

generator = Seed(
    json_path="../seeds/normal_jp_seeds.json",
    export_eml_path="../../../tests/test_files/eml/normal_jp/",
    title="Normal Japanese Seeds",
    explain="Normal Japanese mail samples",
)

for i in range(75):
    cc_range = 5
    rand = random.randrange(cc_range)
    cc_header_addr: HEADER_TYPE = ""

    if rand != (cc_range - 1):
        if i % 2 == 0:
            cc_header_addr = [gen_email() for _ in range(rand)]
        else:
            cc_header_addr = [(gen_name(), gen_email()) for _ in range(rand)]

    if i % 2 == 0:
        generator.add(
            addr_to=gen_email(),
            addr_from=gen_email(),
            addr_cc=cc_header_addr,
            subject=gen_word(length=25),
            message=gen_word(),
        )
    else:
        generator.add(
            addr_to=(gen_name(), gen_email()),
            addr_from=(gen_name(), gen_email()),
            addr_cc=cc_header_addr,
            subject=gen_word(length=25),
            message=gen_word(),
        )

generator.to_file(indent=2, encoding="utf-8")
