from pathlib import Path
from time import sleep

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
        "openGPT-X/Teuken-7B-instruct-v0.6",
        "Qwen/Qwen3-Coder-30B-A3B-Instruct",
        "Qwen/Qwen3-VL-8B-Instruct",
        "zai-org/GLM-5.2-FP8"
    ]

    # source = "tests/example_data/oop.py"
    # target_path = "tests/results/benchmarks/uml_class_diagram/"
    # source = "tests/example_data/db_schema.py"
    # target_path = "tests/results/benchmarks/entity_relation_diagram/"

    yaml = YAMLConfig('tests/configs/autodocs.yaml')

    prompt = PromptReader(
        "prompts/docs_summary.md",
        {"project_title": "Project"}
    )
    rule = prompt.getResolved()

    # print(prompt.getExtractedTagNames("UML_TAG_"))

    uml = Extraction(FileReader("tests/results/benchmarks/complex_project/doc_0.md").text).extractPlantUML()
    print(uml)

    # for i in range(len(model_list)):
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

    #     sleep(yaml.config.llm_service.api.request_delay_seconds)


if __name__ == "__main__":
    main()
