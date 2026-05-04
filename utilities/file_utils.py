"""
File utility helpers — all paths accept str or pathlib.Path.
"""

import csv
import json
from pathlib import Path


def read_lines(path) -> list[str]:
    return Path(path).read_text(encoding="utf-8").splitlines()


def write_lines(path, lines: list[str]) -> None:
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_json(path) -> dict | list:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data, indent: int = 2) -> None:
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=indent), encoding="utf-8")


def read_csv_as_dicts(path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


if __name__ == "__main__":
    import tempfile, os

    with tempfile.TemporaryDirectory() as tmp:
        # Text file
        txt = Path(tmp) / "demo.txt"
        write_lines(txt, ["line one", "line two", "line three"])
        print("Lines:", read_lines(txt))

        # JSON file
        jsf = Path(tmp) / "demo.json"
        write_json(jsf, {"name": "Alice", "scores": [95, 87, 92]})
        print("JSON: ", read_json(jsf))
