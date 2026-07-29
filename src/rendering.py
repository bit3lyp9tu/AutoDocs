import subprocess

from src.schemas.config_model import Config


class PlantUMLRendering:
    def __init__(self, config: Config, source_file) -> None:
        self.config = config
        self.jar_path = self.config.autodocs.plantuml.renderer_path
        self.source_file = source_file


    def __render(self, command):
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            stdout = result.stdout
            stderr = result.stderr

        except subprocess.CalledProcessError as e:
            if e.returncode == 50 or e.returncode == 100:
                print("PlantUML renderer could not find file")
            elif e.returncode == 200:
                print(f"File [{self.source_file}] contains syntax error")
            else:
                print(f"PlantUML failed to render, Exit code: {e.returncode}")
                print(f"stderr: {e.stderr}")


    def render(self, target_path: str):

        if self.config.autodocs.plantuml.auto_render:   # TODO: move to higher level
            print(f"Render source: [{self.source_file}]...")
            self.__render([
                "java",
                "-jar",
                self.jar_path,
                self.source_file,
                "--output-dir",
                target_path,
                "--png"
            ])
