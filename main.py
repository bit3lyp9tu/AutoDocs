import json
from pathlib import Path
import re
from time import sleep

from lark import GrammarError, Lark, UnexpectedCharacters, UnexpectedToken

from src.config_parser import YAMLConfig
from src.extraction_factory import Extraction
from src.file_factory import FileReader, PUMLWriter, PromptReader, RecursiveSubdirectories, FileWriter
from src.git_master import GitMaster
from src.rendering import PlantUMLRendering
from src.plantuml_converter import PlantUMLConverter
from src.request import LLM_API
from src.terminal_master import TerminalMaster


def main():
    # print("Converting Code to PlantUML and rendering...")

    model_list = [
        # "google/gemma-4-31B-it",
        # "meta-llama/Llama-3.1-8B-Instruct",
        # "meta-llama/Llama-3.3-70B-Instruct",
        # "MiniMaxAI/MiniMax-M3-MXFP8",
        "moonshotai/Kimi-K3",
        # "openai/gpt-oss-120b",
        # "Qwen/Qwen3-Coder-30B-A3B-Instruct",
        # "Qwen/Qwen3-VL-8B-Instruct",
        # "zai-org/GLM-5.2-FP8"
    ]
        # "openGPT-X/Teuken-7B-instruct-v0.6",

    # source = "tests/example_data/oop.py"
    # target_path = "tests/results/benchmarks/uml_class_diagram/"
    # source = "tests/example_data/db_schema.py"
    # target_path = "tests/results/benchmarks/entity_relation_diagram/"

    yaml = YAMLConfig('tests/configs/autodocs.yaml')

    prompt = PromptReader(
        "prompts/docs_summary.md",
        {"project_title": "Project"}
    )
    # rule = prompt.getResolved()

    # print(prompt.getExtractedTagNames("UML_TAG_"))


    for i in range(len(model_list)):
        print(f"##########################################################-{i}")

        # code = FileReader(target_path="tests/example_data/oop.py").text
        code = FileReader(target_path="src/schemas/umlblock_schema.py").text

        api = LLM_API(config=yaml.config, model=model_list[i])
        result = api.request(
            rule=PromptReader(target_path="prompts/grammar2.md", data={"language": "python"}).getResolved(),
            prompt=code
        )
        # for chunk in stream:
        #      print(chunk, end="", flush=True)

        if result:
            FileWriter(target_path=f"tests/results/benchmarks/grammars/grammar{i}.txt", mode="w+").write(content=result)
            print(result)

            try:
                parser = Lark(
                    grammar=result,
                    start="program",
                    parser="earley",
                    ambiguity='explicit'
                )
                tree = parser.parse(code)

                print(tree.pretty())
            except GrammarError as e:
                print(f"ERROR: [{model_list[i]}] grammar is faulty: {e}")
            except UnexpectedToken as t:
                print(f"ERROR: [{model_list[i]}] made an UnexpectedToken: {t}")
            except UnexpectedCharacters as c :
                print(f"ERROR: [{model_list[i]}] made an UnexpectedCharacters: {c}")

        sleep(yaml.config.llm_service.api.request_delay_seconds)


def test():

    tag="UML"
    target_file = f".autodocs/llm_logs/2026-08-03_09-47-04.md"
    # puml_path = f".autodocs/self.PUML_DIR}/{local_session}"

    extractor = Extraction(FileReader(target_path=target_file).text)
    umls, text = extractor.extractPlantUML(tag_infix=tag)

    paths, names = extractor.createPaths(
        keys=list(umls.keys()),
        tag=tag,
        path=""
    )

    think_text, text = extractor.extractThinkTagPrefix(text)

    print("#################")
    print(think_text)
    print("#################")
    print(text)
    print("#################")

    print(re.findall(r'.*\</mm:think\>', "</mm:think>"))

if __name__ == "__main__":
    main()
    # test()
