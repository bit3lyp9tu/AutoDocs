
from datetime import datetime
import os
from pathlib import Path

from src.config_parser import YAMLConfig
from src.extraction_factory import Extraction
from src.file_factory import FileReader, PUMLWriter, PromptReader, RecursiveSubdirectories
from src.rendering import PlantUMLRendering
from src.request import LLM_API


class Docs:

    PUML_DIR = "puml"
    IMG_DIR = "img"
    LLM_DIR = "llm_logs"
    LOG_DIR = "log"
    PROMPTS_DIR = "prompts"

    def __init__(self, root_path: Path, config_path='autodocs.yaml') -> None:
        self.config = YAMLConfig(config_path).config

        # check env
        if not Path(root_path / '.autodocs').exists() or not Path(root_path / '.autodocs').is_dir():
            raise EnvironmentError(".autodocs/ not found")

        self.autodocs_path = Path(root_path / ".autodocs")

        os.mkdir(os.path.join(self.autodocs_path, self.PUML_DIR))
        os.mkdir(os.path.join(self.autodocs_path, self.IMG_DIR))
        os.mkdir(os.path.join(self.autodocs_path, self.LLM_DIR))
        os.mkdir(os.path.join(self.autodocs_path, self.LOG_DIR))
        os.mkdir(os.path.join(self.autodocs_path, self.PROMPTS_DIR))
        # TODO: create required cache directory?

        prompt = PromptReader(
            "prompts/docs_summary.md",  # TODO: use path from config
            {
                "project_title": "Project"
            }
        )
        self.rule = prompt.getResolved()
        self.sessions: list[str] = []


    def createContent(self, source_code_path: str, model: str):
        current_session = str(datetime.now())
        self.sessions.append(current_session)
        target_file = f".autodocs/{self.LLM_DIR}/{current_session}.md"

        contents = []
        directory = Path(Path(__file__).resolve().parent / source_code_path)
        for file in RecursiveSubdirectories(directory).children:
            contents.append(file)
            contents.append(FileReader(target_path=str(directory)+file).text)
            contents.append("")

        # TODO: meta data in log?
        print(f'Prompt length lines: {len(contents)}')

        api = LLM_API(config=self.config, model=model)
        # TODO: meta data in log?

        result = ""
        try:
            result = api.request_stream(
                rule=self.rule,
                prompt=''.join(contents)
            )
            with open(target_file, "w", encoding="utf-8") as f:
                for chunk in result:
                    f.write(chunk)
        except ValueError as err:
            print(err)


    def createPUML(self):
        tag="UML"
        target_file = f".autodocs/{self.LLM_DIR}/{self.sessions[-1]}.md"
        puml_path = f".autodocs/{self.PUML_DIR}/{self.sessions[-1]}.puml"

        # TODO: original target in log?
        extractor = Extraction(FileReader(target_path=target_file).text)
        umls, text = extractor.extractPlantUML(tag_infix=tag)

        # TODO: store in current session directory?
        paths = extractor.createPaths(
            keys=list(umls.keys()),
            tag=tag,
            path=puml_path
        )

        text = extractor.setPointersAll(
            text=text,
            keys=list(umls.keys()),
            paths=paths,
            tag=tag
        )

        # TODO: add to log?
        for k, v in paths.items():
            PUMLWriter(target_path=v).write(umls[k])


    def renderPUML(self):
        source_file =  f".autodocs/{self.PUML_DIR}/{self.sessions[-1]}.puml"
        target_path =  f".autodocs/{self.IMG_DIR}/{self.sessions[-1]}.png"

        plantuml = PlantUMLRendering(self.config, source_file)
        plantuml.render(target_path)
