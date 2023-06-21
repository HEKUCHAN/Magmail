import os
import random
from faker import Faker

from magmail.generator import Seed
from magmail.types import HEADER_TYPE

os.chdir(os.path.dirname(os.path.abspath(__file__)))

generator = Seed(
    json_path="../seeds/normal_en_seeds.json",
    export_eml_path="../../../../../tests/test_files/eml/normal_en/",
    title="Normal English Seeds",
    explain="Normal English mail samples. (encoding=UTF-8)",
)

faker = Faker("en_US")

print("Start generate English seeds...")

for i in range(75):
    cc_range = 5
    rand = random.randrange(cc_range)
    cc_header_addr: HEADER_TYPE = ""

    if rand != (cc_range - 1):
        if i % 2 == 0:
            cc_header_addr = [faker.email() for _ in range(rand)]
        else:
            cc_header_addr = [(faker.name(), faker.email()) for _ in range(rand)]

    if i % 2 == 0:
        generator.add(
            addr_to=faker.email(),
            addr_from=faker.email(),
            addr_cc=cc_header_addr,
            subject=faker.text(max_nb_chars=25),
            message=faker.text(max_nb_chars=250),
        )
    else:
        generator.add(
            addr_to=(faker.name(), faker.email()),
            addr_from=(faker.name(), faker.email()),
            addr_cc=cc_header_addr,
            subject=faker.text(max_nb_chars=25),
            message=faker.text(max_nb_chars=250),
        )

generator.to_file(indent=2, encoding="utf-8")
print("Generated English seeds!")
