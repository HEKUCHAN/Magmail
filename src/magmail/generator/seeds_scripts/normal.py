from magmail.generator import Seed, generate_email

generator = Seed(
    json_path="../seeds/charsets_seeds.json",
    export_eml_path="../../../tests/test_files/",
    title="Charset Seeds",
)

generator.add()
