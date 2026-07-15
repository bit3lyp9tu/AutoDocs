import os
from pathlib import Path

class FileReader:
    def __init__(self, target_path) -> None:
        with open(target_path, 'r') as r:
            self.text = r.read()


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
