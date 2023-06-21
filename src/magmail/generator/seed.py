import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Union

from magmail.utils import to_path
from magmail.types import ADDRESS_HEADER_TYPE, HEADER_TYPE


class Seed:
    def __init__(
        self,
        json_path: Union[str, Path],
        export_eml_path: Union[str, Path],
        title: str = "",
        explain: str = "",
    ):
        self.title = title
        self.explain = explain
        self.json_path = to_path(json_path)
        self.export_eml_path = to_path(export_eml_path)
        self.seeds: List[Dict[str, Any]] = []

        if self.json_path.is_dir():
            self.json_path = self.json_path / f"{uuid.uuid4()}.json"

        if self.json_path.suffix != ".json":
            raise ValueError(
                f"Unknown file extension: {self.json_path.suffix}, '.json' or directory path is only supported."
            )

    def add(
        self,
        addr_to: ADDRESS_HEADER_TYPE = "",
        addr_from: ADDRESS_HEADER_TYPE = "",
        addr_cc: HEADER_TYPE = "",
        subject: str = "",
        message: Union[str, Dict[str, str]] = "",
        headers: Dict[str, str] = {},
        encoding: str = "utf-8",
        mime_type: str = "plain",
        transfer_encoding: str = "base64",
        attachment_file_paths: Union[List[str], str] = [],
    ) -> None:
        self.seeds.append(
            {
                "addr_to": addr_to,
                "addr_from": addr_from,
                "addr_cc": addr_cc,
                "subject": subject,
                "message": message,
                "headers": headers,
                "encoding": encoding,
                "mime_type": mime_type,
                "transfer_encoding": transfer_encoding,
                "attachment_file_paths": attachment_file_paths,
            }
        )

    def to_file(
        self, encoding: str = "utf-8", indent: int = 4, ensure_ascii: bool = True
    ) -> None:
        template_json = {
            "title": self.title,
            "explain": self.explain,
            "json_path": str(self.json_path),
            "export_eml_path": str(self.export_eml_path),
            "amount": len(self.seeds),
            "seeds": self.seeds,
        }

        self.create_parent_dic(self.json_path.parent)

        with open(self.json_path, "w", encoding=encoding) as file:
            json.dump(template_json, file, indent=indent, ensure_ascii=ensure_ascii)

    @classmethod
    def create_parent_dic(self, path: Union[str, Path]) -> None:
        if not isinstance(path, Path):
            path = to_path(path)

        path.mkdir(parents=True, exist_ok=True)
