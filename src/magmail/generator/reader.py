import uuid
import pprint
import json
from typing import Union
from pathlib import Path

from magmail.utils import to_path
from magmail.generator import Mail


class Reader:
    def __init__(self, json_path: Union[str, Path]):
        self.json_path = to_path(json_path)
        if self.json_path.is_dir():
            self.json_path = self.json_path / f"{uuid.uuid4()}.json"

        if self.json_path.suffix != ".json":
            raise ValueError(
                f"Unknown file extension: {self.json_path.suffix}, '.json' or directory path is only supported."
            )

        self.read()

    def read(self):
        with open(self.json_path, "r") as file:
            json_file = json.load(file)

        pprint.pprint(json_file)

    @classmethod
    def serializer(cls, eml_json):
        pass

    def to_file(self):
        pass
