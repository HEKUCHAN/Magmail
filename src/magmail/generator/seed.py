import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Union

from magmail.utils import to_path


class Seed:
    def __init__(
            self,
            json_path: Union[str, Path],
            export_path: Union[str, Path],
            title: str = ''
        ):
        self.title = title
        self.json_path = to_path(json_path)
        self.export_path = to_path(export_path)
        self.seeds: List[Dict[str, Any]] = {}


        if self.json_path.is_dir():
            self.json_path = self.json_path / f"{uuid.uuid4()}.json"

        if self.json_path.suffix != 'json':
            raise ValueError(f'Unknown file extension: {self.json_path.suffix}, `.json` or directory path is only supported.')

    def add(
        self,
        addr_to: str = '',
        addr_from: str = '',
        addr_cc: Union[str, List[str]] = '',
        subject: str = '',
        message: Union[str, Dict[str, str]] = '',
        headers: Dict[str, str] = {},
        encoding: str = "utf-8",
        mime_type: str = "plain",
        transfer_encoding: str = "base64",
        attach_files_path: Union[List[str], str] = [],
    ):
        self.seeds.append({
            "addr_to": addr_to,
            "addr_from": addr_from,
            "addr_cc": addr_cc,
            "subject": subject,
            "message": message,
            "headers": headers,
            "encoding": encoding,
            "mime_type": mime_type,
            "transfer_encoding": transfer_encoding,
            "attach_files_path": attach_files_path,
        })

    def to_file(self):
        template_json = {
            "title": self.title,
            "json_path": self.json_path,
            "export_path": self.export_path,
            "amount": len(self.seeds),
            "seeds": self.seeds
        }

        with open(self.json_path, "w") as file:
            json.dump(template_json, file, indent=4)



