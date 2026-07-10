import os

class FileReader:
    def __init__(self, target_path) -> None:
        with open(target_path, 'r') as r:
            self.text = r.read()


class FileWriter:
    def __init__(self, target_path, content="") -> None:
        if content == "":
            raise ValueError(f"No content found to write into [{target_path}].")

        with open(target_path, 'w') as f:
            f.write(content)

        if not os.path.isfile(target_path):
            raise FileNotFoundError(f"Creation of [{target_path}] failed.")
