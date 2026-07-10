import subprocess

from src.config_model import Config


class PlantUMLRendering:
    def __init__(self, config: Config, render_source_path="") -> None:
        self.config = config
        self.jar_path = self.config.autodocs.plantuml.renderer_path
        self.render_source_path = render_source_path

    def render(self):
        if self.config.autodocs.plantuml.auto_render:
            print(f"Render source: [{self.render_source_path}]...")
            try:
                result = subprocess.run(
                    [
                        "java",
                        "-jar",
                        self.jar_path,
                        self.render_source_path,
                    ],
                    check=True,
                    capture_output=True,
                    text=True
                )
                stdout = result.stdout
                stderr = result.stderr

            except subprocess.CalledProcessError as e:
                print(f"PlantUML failed to render, Exit code: {e.returncode}")
                print(f"stderr: {e.stderr}")

