"""
This code is used to get codecs current encodings that Python supports.
"""
import os
import re
import ssl
import json
from bs4 import BeautifulSoup
from urllib.request import urlopen

os.chdir(os.path.dirname(os.path.abspath(__file__)))

EXPORT_JSON_PATH = "../src/magmail/generator/seeds_scripts/data/current_encoding.json"

ssl._create_default_https_context = ssl._create_unverified_context

html = urlopen("https://docs.python.org/3/library/codecs.html")
codecs_main_page_bs4 = BeautifulSoup(html, "html.parser")

section = codecs_main_page_bs4.find("section", {"id": "standard-encodings"})
table = section.find("table", {"class": "docutils align-default"})
rows = table.findAll("tr")

lang_encode_dict = {}
for row in rows[1:]:
    charset = row.select_one("td:nth-child(1) p")
    charset = re.sub(r"\n", "", charset.get_text())

    language = row.select_one("td:nth-child(3) p")
    language = re.split(r", *|,", re.sub(r"\n", "", language.get_text()))

    for lang in language:
        lang = lang.replace(" ", "_")

        if not lang in lang_encode_dict:
            lang_encode_dict[lang] = []
        lang_encode_dict[lang].append(charset)

lang_encode_dict["All"] = lang_encode_dict["all_languages"]
del lang_encode_dict["all_languages"]

lang_encode_dict["Simplified_Chinese"].extend(lang_encode_dict["SimplifiedChinese"])
del lang_encode_dict["SimplifiedChinese"]

with open(EXPORT_JSON_PATH, "w+", encoding="utf-8") as file:
    json.dump(lang_encode_dict, file, indent=2)
