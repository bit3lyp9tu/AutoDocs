import re

from src.config_model import Config
from src.file_factory import FileReader, FileWriter
from src.request import LLM_API


class PlantUMLConverter:
    def __init__(self, config: Config, model="meta-llama/Llama-3.3-70B-Instruct") -> None:
        self.config = config
        self.model = model


    def _split_plantuml_sections(self, text: str) -> list[str]:
        """
        Split a string into PlantUML sections.

        Returns:
            List of complete '@startuml ... @enduml' blocks.

        Raises:
            ValueError: If there are unmatched @startuml/@enduml tags or
                        if there is malformed content.
        """

        if not text:
            return [
                "% ERROR"
            ]

        start_count = len(re.findall(r"@startuml\b", text))
        end_count = len(re.findall(r"@enduml\b", text))

        if start_count != end_count:
            raise ValueError(
                f"Mismatched tags: found {start_count} '@startuml' and "
                f"{end_count} '@enduml'."
            )

        sections = [m.group(0).strip() for m in re.compile(
            r"@startuml\b.*?@enduml\b",
            re.DOTALL,
        ).finditer(text)]

        if len(sections) != start_count:
            raise ValueError("Failed to extract all PlantUML sections.")

        # Validate each section
        for i, section in enumerate(sections, start=1):
            lines = [line.strip() for line in section.splitlines() if line.strip()]

            if lines[0] != "@startuml":
                raise ValueError(f"Section {i} does not start with '@startuml'.")

            if lines[-1] != "@enduml":
                raise ValueError(f"Section {i} does not end with '@enduml'.")

        return sections


    def convert(self, source_file, target_path):
        text = FileReader(source_file).text

        with open(self.config.autodocs.sysprompt.file_path, 'r') as r:
            prompt = r.read()

        api = LLM_API(
            config=self.config,
            model=self.model
        )

        result = []
        try:
            raw_result = api.call(rule=prompt, prompt=text)
            result = self._split_plantuml_sections(raw_result)
        except ValueError as err:
            print(err)

        path = target_path
        try:
            FileWriter(target_path=path, content=(result[0] if len(result) > 0 else ""))
        except ValueError as err:
            print(err)
