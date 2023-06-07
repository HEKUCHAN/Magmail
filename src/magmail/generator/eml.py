import os
from pathlib import Path
from typing import Union, List

from magmail.generator import Reader
from magmail.utils import to_path

os.chdir(os.path.dirname(os.path.abspath(__file__)))

JSON_DIC_PATH: Union[str, Path] = "./seeds/"
JSON_DIC_PATH = to_path(JSON_DIC_PATH)

readers: List[Reader] = []

for file in JSON_DIC_PATH.iterdir():
    readers.append(Reader(file))

