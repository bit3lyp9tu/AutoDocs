
from pathlib import Path

from src.config_parser import YAMLConfig
from src.extraction_factory import Extraction
from src.file_factory import FileReader, PUMLWriter, PromptReader, RecursiveSubdirectories
from src.rendering import PlantUMLRendering
from src.request import LLM_API


class Docs:
    def __init__(self, config_path='autodocs.yaml') -> None:
        # config_path='tests/configs/autodocs.yaml'
        self.config = YAMLConfig(config_path).config

        prompt = PromptReader(
            "prompts/docs_summary.md",  # TODO: use path from config
            {
                "project_title": "Project"
            }
        )
        self.rule = prompt.getResolved()

        # TODO: create required cache directory?

    def createContent(self, model):
        target_file = 'tests/results/benchmarks/complex_project/doc_0.md'
        source_code_path = 'tests/example_data/complex_example1'

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
        target_path = "tests/results/benchmarks/complex_project/doc_0.md"
        puml_path = f"tests/results/benchmarks/generated_umls"

        current_session = "" # TODO

        # TODO: original target in log?
        extractor = Extraction(FileReader(target_path=target_path).text)
        umls, text = extractor.extractPlantUML(tag_infix=tag)

        # TODO: store in current session directory
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
        # TODO: render and put img in directory

        source_path = ""
        target_path = ""

        renderer = PlantUMLRendering(self.config, render_source_path=source_path)
        renderer.renderAll()
