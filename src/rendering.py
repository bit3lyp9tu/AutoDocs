from enum import Enum
import subprocess
import threading

from src.schemas.config_model import ConfigSchema


class PrintMode(Enum):
    NEVER = 0
    ONLY_WHEN_ERROR = 1
    ALWAYS = 2

class PlantUMLRendering:
    def __init__(self, config: ConfigSchema, source_file) -> None:
        self.config = config
        self.jar_path = self.config.autodocs.plantuml.renderer_path
        self.source_file: str = source_file


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

            return result.stdout, result.returncode, result.stderr

        except subprocess.CalledProcessError as e:
            return e.stdout, e.returncode, e.stderr


    def __render_thread(self, command):
        try:
            p = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except OSError as e:
            print("Failed to start Java:", e)
            return

        def monitor():
            stdout, stderr = p.communicate()

            if p.returncode != 0:
                print(f"Java process failed ({p.returncode}):")
                print(stderr)

        threading.Thread(target=monitor, daemon=True).start()

    def render(self, target_path: str, mode: PrintMode = PrintMode.ONLY_WHEN_ERROR):
        if mode.value == 2:
            print(f"Render source: [{self.source_file}]...")

        # stdout, returncode, stderr = self.__render([
        #     "java",
        #     "-jar",
        #     self.jar_path,
        #     self.source_file,
        #     "--output-dir",
        #     target_path,
        #     "--png"
        # ])
        self.__render_thread([
            "java",
            "-jar",
            self.jar_path,
            self.source_file,
            "--output-dir",
            target_path,
            "--png"
        ])

        # if returncode != 0:
        #     if mode.value >= 1:
        #         if returncode == 50 or returncode == 100:
        #             print("PlantUML renderer could not find file")
        #         elif returncode == 200:
        #             print(f"File [{self.source_file}] contains syntax error")
        #         else:
        #             print(f"PlantUML failed to render, Exit code: {returncode}")
        #             print(f"stderr: {stderr}")
        # else:
        #     if mode.value == 2:
        #         print(f"Rendered PlantUML: [{target_path}/{self.source_file.split('/')[-1]}]")

