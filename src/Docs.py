
from datetime import datetime
import json
import os
from pathlib import Path

from src.config_parser import YAMLConfig
from src.extraction_factory import Extraction
from src.file_factory import FileReader, FileWriter, PUMLWriter, PromptReader, RecursiveSubdirectories
from src.rendering import PlantUMLRendering
from src.request import LLM_API


class Docs:

    PUML_DIR = "puml"
    IMG_DIR = "img"
    LLM_DIR = "llm_logs"
    LOG_DIR = "log"
    PROMPTS_DIR = "prompts"

    def __init__(self, setup_file='.autodocs/setup.json') -> None:

        file = Path(str(setup_file))
        if not file.exists() or not file.is_file() or not str(file).endswith("json"):
            raise NameError(f"Setup file [{setup_file}] not found")

        with open(setup_file) as f:
            setup = json.loads(f.read())

        self.config_path = setup["config_path"]
        self.autodocs_path = setup["autodocs_path"]
        self.root_path = setup["config_path"]
        self.rule = setup["resolved_prompt"]
        self.sessions = setup["sessions"]

        self.config = YAMLConfig(self.config_path).config


    def createContent(self, source_code_path: str, model: str = "MiniMaxAI/MiniMax-M3-MXFP8"):
        current_session = str(datetime.now())
        self.sessions.append(current_session)

        with open(str(Path(".autodocs/setup.json"))) as f:
            f.write(json.dumps(setup))

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


    def createPUML(self, docs_file: str = "docs.md"):
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

        FileWriter(docs_file).write(text)


    def renderPUML(self):
        source_file =  f".autodocs/{self.PUML_DIR}/{self.sessions[-1]}.puml"
        target_path =  f".autodocs/{self.IMG_DIR}/{self.sessions[-1]}.png"

        plantuml = PlantUMLRendering(self.config, source_file)
        plantuml.render(target_path)
