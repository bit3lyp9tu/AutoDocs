
from datetime import datetime
import os
from pathlib import Path

from src.config_parser import JSONConfig, YAMLConfig
from src.extraction_factory import Extraction
from src.file_factory import FileReader, FileWriter, PUMLWriter, RecursiveSubdirectories
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
        if not file.exists() or not file.is_file() or not str(file).endswith(".json"):
            raise NameError(f"Setup file [{setup_file}] not found")

        self.setup_file = setup_file
        self.setup = JSONConfig(setup_file)
        self.config = YAMLConfig(self.setup.config_path).config


    def createContent(self, source_code_path: str, model: str = "MiniMaxAI/MiniMax-M3-MXFP8"):
        current_session = str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        self.setup.config.sessions[current_session] = []

        os.mkdir(os.path.join((Path(self.setup.config.autodocs_path) / self.PUML_DIR), current_session))
        os.mkdir(os.path.join((Path(self.setup.config.autodocs_path) / self.IMG_DIR), current_session))

        self.save_setup()

        target_file = f".autodocs/{self.LLM_DIR}/{current_session}.md"

        contents = []
        directory = Path(self.setup.config.root_path) / source_code_path
        for file in RecursiveSubdirectories(Path(self.setup.config.root_path), directory, blacklist_path=".gitignore").paths:
            full_path = directory / file
            contents.extend([
                file,
                FileReader(str(full_path)).text,
                ""
            ])

        # TODO: meta data in log?
        print(f'Prompt length lines: {len(contents)}')

        api = LLM_API(config=self.config, model=model)
        # TODO: meta data in log?

        result = ""
        try:
            result = api.request_stream(
                rule=self.setup.config.resolved_prompt,
                prompt=''.join(contents)
            )
            with open(target_file, "w", encoding="utf-8") as f:
                for chunk in result:
                    f.write(chunk)
        except ValueError as err:
            print(err)


    def createPUML(self, docs_file: str = "docs.md", session: str = "", docsHeader: str = ""):
        local_session = self.__validateSession(session)

        tag="UML"
        target_file = f".autodocs/{self.LLM_DIR}/{local_session}.md"
        puml_path = f".autodocs/{self.PUML_DIR}/{local_session}"

        # TODO: original target in log?
        extractor = Extraction(FileReader(target_path=target_file).text)
        umls, text = extractor.extractPlantUML(tag_infix=tag)

        # TODO: store in current session directory?
        paths, names = extractor.createPaths(
            keys=list(umls.keys()),
            tag=tag,
            path=puml_path
        )
        self.setup.config.sessions[local_session] = names
        self.save_setup()

        text = extractor.setPointersAll(
            text=text,
            keys=list(umls.keys()),
            paths=paths,
            tag=tag
        )

        # TODO: add to log?
        for k, v in paths.items():
            PUMLWriter(target_path=v).write(umls[k])

        input = docsHeader + "\n" + text
        FileWriter(docs_file).write(input)


    def renderPUML(self, session: str = ""):
        local_session = self.__validateSession(session)

        # TODO: do not use glob, iterate manually (for log entries)
        source_file =  f".autodocs/{self.PUML_DIR}/{local_session}/*.puml"
        target_path =  Path(self.setup.config.root_path) / f".autodocs/{self.IMG_DIR}/{local_session}"

        plantuml = PlantUMLRendering(self.config, source_file)
        plantuml.render(str(target_path))


    def save_setup(self):
        self.setup.createFile(self.setup_file)


    def __validateSession(self, session):
        if session:
            if session in self.setup.config.sessions.keys():
                return session
            else:
                raise KeyError(session)
        else:
            return list(self.setup.config.sessions.keys())[-1]
