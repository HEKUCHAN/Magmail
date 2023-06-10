from pathlib import Path
from typing import List, Union

from magmail.utils import to_path
from magmail.generator import Reader, Mail


class Eml:
    def __init__(self, json_path: Union[str, Path]):
        self.files: List[Reader] = []
        self.json_path: Path = to_path(json_path)
        self.mails: List[Mail] = []
        self.read()
        self.init()

    def read(self) -> None:
        if not self.json_path.is_dir() and self.json_path.suffix != ".json":
            raise ValueError(
                f"Unknown file extension: {self.json_path.suffix}, '.json' or directory path is only supported."
            )

        if self.json_path.is_dir():
            for file in self.json_path.iterdir():
                self.files.append(
                    Reader(file)
                )
        else:
            self.files.append(
                Reader(self.json_path)
            )

    def init(self) -> None:
        for file in self.files:
            _title = file.data["title"]
            _explain = file.data["explain"]
            export_eml_path = to_path(file.data["export_eml_path"])
            self.create_parent_dic(export_eml_path)

            for i, seed in enumerate(file.data["seeds"]):
                Mail(
                    **seed
                ).to_file(export_eml_path / f"{self.json_path.stem}-{i}.eml")

    def create_parent_dic(self, path: Union[str, Path]):
        if not isinstance(path, Path):
            path = to_path(path)

        path.mkdir(parents=True, exist_ok=True)
