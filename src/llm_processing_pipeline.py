from io import TextIOWrapper
from pathlib import Path
from typing import Generator

from llm_api_toolcollection.llm_processing_pipeline import Code, Text, Think

from src.rendering import PlantUMLRendering


def event_consumer(config, root: Path, stream: Generator[Think | Text | Code], name: str, puml_path: Path, img_path: Path, think_file: TextIOWrapper, text_result_file: TextIOWrapper):
    tag = "UML"

    for line in stream:
        tag_name = line.content.replace("}}", "").replace(str("{{TAG_" + tag + "_"), "").replace("\n", "")

        if type(line) == Think:
            think_file.write(line.content)
            think_file.flush()

        if type(line) == Text:
            if line.isTag:
                rel_img_path = img_path.relative_to(root)
                img_link = str(rel_img_path / name / f"{tag_name}.png")
                md_img = f"![{tag_name}]({img_link})"
                text_result_file.write(md_img)
            else:
                text_result_file.write(line.content)
            text_result_file.flush()

        if type(line) == Code:
            if line.reverence_tag and line.language == "plantuml":
                file_name = line.reverence_tag.replace("}}", "").replace(str("{{TAG_" + tag + "_"), "").replace("\n", "")
                file_path = puml_path / name / f"{file_name}.puml"

                with open(file_path, "w") as f:
                    f.write(line.content)
                    f.flush()

                plantuml = PlantUMLRendering(config, file_path)
                plantuml.render(str(img_path / name).replace(".puml", ".png"))
