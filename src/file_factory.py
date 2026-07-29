import os
from pathlib import Path
import re

from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern

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
    def __init__(self, target_path, mode='w') -> None:
        self.target_path = target_path

        if mode not in ["a", "w", "w+"]:
            raise ValueError(f"Unknown file mode: [{mode}]")
        self.mode = mode

    def write(self, content=""):
        if content == "":
            raise ValueError(f"No content found to write into [{self.target_path}].")

        with open(self.target_path, self.mode) as f:
            f.write(content)

        if not os.path.isfile(self.target_path):
            raise FileNotFoundError(f"Creation of [{self.target_path}] failed.")


class PUMLWriter(FileWriter):
    def __init__(self, target_path: str, mode='w') -> None:

        if not target_path.endswith(".puml"):
            raise TypeError(f"The file should be a .puml file, [{target_path.split(".")[1]}] used")

        super().__init__(target_path, mode)

    def write(self, content=""):
        if content == "":
            raise ValueError(f"No content found to write into [{self.target_path}].")

        with open(self.target_path, self.mode) as f:
            f.write(content)

        if not os.path.isfile(self.target_path):
            raise FileNotFoundError(f"Creation of [{self.target_path}] failed.")


class RecursiveSubdirectories:
    def __init__(self, root: Path, directory: Path, blacklist_path="") -> None:
        self.directory = directory

        paths: list[str] = []
        if blacklist_path:
            full_blacklist_path = Path(root / blacklist_path)
            if not full_blacklist_path.exists() and full_blacklist_path.is_file():
                raise FileNotFoundError(str(full_blacklist_path))

            spec = PathSpec.from_lines(
                GitWildMatchPattern,
                open(full_blacklist_path)
            )
            for path in directory.rglob("*"):
                if not path.is_file():
                    continue
                rel = path.relative_to(directory).as_posix()
                if spec.match_file(rel):
                    continue
                paths.append(rel)
        else:
            for path in directory.rglob("*"):
                if not path.is_file():
                    continue
                rel = path.relative_to(directory).as_posix()
                paths.append(rel)

        self.paths = paths
