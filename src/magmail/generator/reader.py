import uuid
import json
from typing import Union, Any
from pathlib import Path

from magmail.utils import to_path


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

    def read(self) -> None:
        with open(self.json_path, "r") as file:
            self.data = self.serializer(json.load(file))

    @classmethod
    def serializer(cls, eml_json: Any) -> Any:
        for seed_key, seed in enumerate(eml_json["seeds"]):
            for addr in seed["addr_cc"]:
                if isinstance(addr, list):
                    addr = tuple(addr)
                    eml_json["seeds"][seed_key]["addr_cc"] = addr

            if isinstance(seed["addr_to"], list):
                eml_json["seeds"][seed_key]["addr_to"] = tuple(seed["addr_to"])

            if isinstance(seed["addr_from"], list):
                eml_json["seeds"][seed_key]["addr_from"] = tuple(seed["addr_from"])
        return eml_json
