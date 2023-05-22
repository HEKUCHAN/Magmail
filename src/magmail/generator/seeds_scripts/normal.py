import os
from magmail.generator import Seed, generate_email

os.chdir(os.path.dirname(os.path.abspath(__file__)))

generator = Seed(
    json_path="../seeds/charsets_seeds.json",
    export_eml_path="../../../tests/test_files/",
    title="Charset Seeds",
)

generator.add()

generator.to_file()
