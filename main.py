import json
from pathlib import Path
from time import sleep

from lark import GrammarError, Lark, UnexpectedCharacters, UnexpectedToken

from src.config_parser import YAMLConfig
from src.extraction_factory import Extraction
from src.file_factory import FileReader, PromptReader, RecursiveSubdirectories, FileWriter
from src.git_master import GitMaster
from src.rendering import PlantUMLRendering
from src.plantuml_converter import PlantUMLConverter
from src.request import LLM_API
from src.terminal_master import TerminalMaster


def main():
    # print("Converting Code to PlantUML and rendering...")

    model_list = [
        "google/gemma-4-31B-it",
        "meta-llama/Llama-3.1-8B-Instruct",
        "meta-llama/Llama-3.3-70B-Instruct",
        "MiniMaxAI/MiniMax-M3-MXFP8",
        "moonshotai/Kimi-K2.7-Code",
        "openai/gpt-oss-120b",
        "Qwen/Qwen3-Coder-30B-A3B-Instruct",
        "Qwen/Qwen3-VL-8B-Instruct",
        "zai-org/GLM-5.2-FP8"
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

    # uml = Extraction(FileReader("tests/results/benchmarks/complex_project/doc_0.md").text).extractPlantUML()
    # print(uml)



    for i in range(len(model_list)):
    #     print(f"##########################################################-{i}")
    #     contents = []

    #     root = Path(__file__).resolve().parent
    #     directory = Path(root / 'tests/example_data/complex_example1')
    #     for file in RecursiveSubdirectories(directory).children:
    #         contents.append(file)
    #         contents.append(FileReader(target_path=str(directory)+file).text)
    #         contents.append("")

    #     print(f'Prompt length lines: {len(contents)}')

    #     api = LLM_API(config=yaml.config, model=model_list[i])

    #     result = ""
    #     try:
    #         result = api.request_stream(
    #             rule=rule,
    #             prompt=''.join(contents)
    #         )
    #         with open(f'tests/results/benchmarks/complex_project/doc_{i}.md', "w", encoding="utf-8") as f:
    #             for chunk in result:
    #                 f.write(chunk)
    #     except ValueError as err:
    #         print(err)

    #     # print(result)
    #     # FileWriter(target_path=f'tests/results/benchmarks/complex_project/doc_{i}.md', content=result)


    # code = FileReader(target_path="tests/example_data/oop.py").text
        code = FileReader(target_path="src/umlblock_schema.py").text

        api = LLM_API(config=yaml.config, model=model_list[i])
        result = api.request(
            rule=FileReader(target_path="prompts/grammar2.md").text,
            prompt=code
        )
        # for chunk in stream:
        #      print(chunk, end="", flush=True)

        if result:
            FileWriter(target_path=f"tests/results/benchmarks/grammars/grammar{i}.txt", content=result, mode="w+")
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


if __name__ == "__main__":
    main()
