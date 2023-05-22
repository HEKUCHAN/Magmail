import os
import random
from magmail.generator import Seed, generate_email, generate_japanese


os.chdir(os.path.dirname(os.path.abspath(__file__)))

generator = Seed(
    json_path="../seeds/charsets_seeds.json",
    export_eml_path="../../../tests/test_files/",
    title="Charset Seeds",
    explain="Normal mail samples"
)

for _ in range(75):
    cc_range = 5
    rand = random.randrange(cc_range)
    if rand == (cc_range - 1):
        cc_header_addr = ""
    else:
        cc_header_addr = [generate_email() for _ in range(rand)]

    generator.add(
        addr_to=generate_email(),
        addr_from=generate_email(),
        addr_cc=cc_header_addr,
        subject=generate_japanese(),
        message=generate_japanese(250)
    )

for _ in range(75):
    cc_range = 5
    rand = random.randrange(cc_range)
    if rand == (cc_range - 1):
        cc_header_addr = ""
    else:
        cc_header_addr = [generate_email() for _ in range(rand)]

    generator.add(
        addr_to=(generate_email(), generate_japanese(6)),
        addr_from=(generate_email(), generate_japanese(6)),
        addr_cc=cc_header_addr,
        subject=generate_japanese(),
        message=generate_japanese(250)
    )

generator.to_file(indent=2, ensure_ascii=False)
