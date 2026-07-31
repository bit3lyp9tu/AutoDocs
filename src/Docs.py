
from datetime import datetime
import os
from pathlib import Path

from src.config_parser import ConfigError, JSONConfig, YAMLConfig
from src.extraction_factory import Extraction
from src.file_factory import FileReader, FileWriter, PUMLWriter, RecursiveSubdirectories
from src.rendering import PlantUMLRendering, PrintMode
from src.request import LLM_API
from src.schemas.setup_schema import MetaData, Session


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
        self.config = YAMLConfig(self.setup.config.config_path).config

        self.meta_data: MetaData = MetaData()

    def createContent(self, source_code_path: str, model: str = "MiniMaxAI/MiniMax-M3-MXFP8"):
        current_session = str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        self.setup.config.sessions[current_session] = None

        os.mkdir(os.path.join((Path(self.setup.config.autodocs_path) / self.PUML_DIR), current_session))
        os.mkdir(os.path.join((Path(self.setup.config.autodocs_path) / self.IMG_DIR), current_session))

        self.save_setup()

        target_file = f".autodocs/{self.LLM_DIR}/{current_session}.md"

        contents = []
        directory = Path(self.setup.config.root_path) / source_code_path
        # TODO: use path from config
        # TODO: everything breaks + strange bug appears when this is used: blacklist_path=".autodocs/.autodocs-ignore"
        for file in RecursiveSubdirectories(Path(self.setup.config.root_path), directory, blacklist_path=".gitignore").paths:
            full_path = directory / file
            contents.extend([
                file,
                FileReader(str(full_path)).text,
                ""
            ])

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

        self.meta_data = MetaData(**api.meta_data)


    def createPUML(self, docs_file: str = "docs.md", session: str = ""):
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
        self.setup.config.sessions[local_session] = Session(meta_data=self.meta_data, content=names)
        self.save_setup()

        think_text, text = extractor.extractThinkTagPrefix(text)

        text = extractor.setPointersAll(
            text=text,
            keys=list(umls.keys()),
            paths=paths,
            tag=tag
        )

        # TODO: add to log?
        for k, v in paths.items():
            PUMLWriter(target_path=v).write(umls[k])

        # TODO: make optional in config
        input = self.setup.config.docs_header + "\n" + text + "\n" + self.setup.config.docs_footer
        FileWriter(docs_file).write(input)

        # TODO: use file name form config
        think_file_path = f"{target_file.replace(".md", "")}_thinking.md"
        FileWriter(think_file_path).write(think_text)


    def renderPUML(self, session: str = ""):
        local_session = self.__validateSession(session)

        root = self.setup.config.root_path
        source_file = Path(root) / f".autodocs/{self.PUML_DIR}/{local_session}"
        target_path =  Path(root) / f".autodocs/{self.IMG_DIR}/{local_session}"

        if source_file.exists() and source_file.is_dir():
            for file in source_file.glob('*'):
                rel = file.relative_to(root).as_posix()

                plantuml = PlantUMLRendering(self.config, source_file=rel)
                plantuml.render(str(target_path), PrintMode.ALWAYS)
        else:
            raise NotADirectoryError(str(source_file))


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
