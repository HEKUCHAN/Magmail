import os
import json
from faker import Faker

from magmail.generator import Seed
from magmail.generator.generate import gen_email, gen_name, gen_word

os.chdir(os.path.dirname(os.path.abspath(__file__)))

LANG_FAKER_DICT = {
    "English": Faker("en_US"),
    "Traditional_Chinese": Faker("zh-TW"),
    "German": Faker("de_DE"),
    "Hebrew": Faker("he_IL"),
    "Western_Europe": None,  # Unknown
    "Arabic": None,  # NON TEXT METHOD
    "Greek": Faker("el_GR"),
    "Baltic_languages": None,
    "Central_and_Eastern_Europe": None,
    "Bulgarian": Faker("bg_BG"),
    "Byelorussian": None,
    "Macedonian": None,
    "Russian": Faker("ru_RU"),
    "Serbian": None,
    "Turkish": Faker("tr_TR"),
    "Portuguese": Faker("pt_PT"),
    "Icelandic": None,
    "Canadian": Faker("fr_CA"),
    "Danish": Faker("da_DK"),
    "Norwegian": None,
    "Thai": Faker("th_TH"),
    "Japanese": Faker("ja_JP"),
    "Korean": Faker("ko_KR"),
    "Urdu": None,
    "Ukrainian": None,  # NON TEXT METHOD
    "Vietnamese": Faker("vi_VN"),
    "Simplified Chinese": Faker("zh-CN"),
    "Unified Chinese": Faker("zh-CN"),
    "Esperanto": None,
    "Maltese": Faker("mt_MT"),
    "Nordic_languages": None,  # Unknown
    "Thai_languages": None,  # Unknown
    "Celtic_languages": None,  # Unknown
    "South-Eastern_Europe": None,  # Unknown
    "Tajik": None,  # Unknown
    "Kazakh": None,  # Unknown
    "All": None,  # Don't need
}

generator_dict = {}

LANG_ENCODE_DATA_PATH = "./data/current_encoding.json"
with open(LANG_ENCODE_DATA_PATH, "r", encoding="utf-8") as file:
    lang_encode_dict = json.load(file)

for lang, charsets in lang_encode_dict.items():
    for charset in charsets:
        if lang in LANG_FAKER_DICT and not LANG_FAKER_DICT[lang] is None:
            faker = LANG_FAKER_DICT[lang]
            if faker is not None:
                if not charset in generator_dict:
                    generator_dict[charset] = Seed(
                        json_path=f"../seeds/charset/{charset}.json",
                        export_eml_path=f"../../../../../tests/test_files/eml/charset/{charset}/",
                        title=f"Charset `{charset}` Test",
                        explain=f"Test {charset}",
                    )

                print(f"Generating... : Charset: {charset}, Language: {lang}")

                for i in range(1, 16):
                    generator = generator_dict[charset]
                    generator.add(
                        addr_to=(faker.name(), faker.email()),
                        addr_from=(faker.name(), faker.email()),
                        subject=f"{lang}: {charset} - {i}",
                        message=faker.text(max_nb_chars=250),
                        encoding=charset,
                    )

for generator in generator_dict.values():
    generator.to_file(indent=2, encoding="utf-8")
else:
    print("Generated the seeds files!")
