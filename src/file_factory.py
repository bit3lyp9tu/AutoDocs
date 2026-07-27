import os
from pathlib import Path
import re

from src.extraction_factory import Extraction

class FileReader:
    def __init__(self, target_path) -> None:
        with open(target_path, 'r') as r:
            self.text = r.read()

class PromptReader(FileReader):
    def __init__(self, target_path, data: dict = {}) -> None:
        super().__init__(target_path)
        self.data = data

    def getExtractedTags(self, tag_prefix) -> list[str]:
        return Extraction(self.text).extractTags(tag_prefix)

    def getExtractedTagNames(self, tag_prefix) -> list[str]:
        return Extraction(self.text).extractTagNames(tag_prefix)

    def getResolved(self) -> str:
        result = self.text

        for k,v in self.data.items():
            identifier = "{{" + k + "}}"
            result = result.replace(identifier, v)

        match = re.findall(r'\{\{\w*\}\}', result)
        if match:
            raise ValueError(f"Unresolved identifier(s) found: {','.join(match)}")

        return result


class FileWriter:
    def __init__(self, target_path, content="", mode='w') -> None:
        if content == "":
            raise ValueError(f"No content found to write into [{target_path}].")

        with open(target_path, mode) as f:
            f.write(content)

        if not os.path.isfile(target_path):
            raise FileNotFoundError(f"Creation of [{target_path}] failed.")


class RecursiveSubdirectories:
    def __init__(self, directory: Path, allowOnlyFiles=True) -> None:
        self.directory = directory
        self.allowOnlyFiles = allowOnlyFiles

        children = []
        for child in directory.rglob("*"):
            if child.is_file():
                children.append(str(child).replace(str(directory), ''))
            else:
                if child.is_dir() and not self.allowOnlyFiles:
                    children.append(str(child).replace(str(directory), ''))

        self.children = children
