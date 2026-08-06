import json
from pathlib import Path, PurePosixPath
import re
from time import sleep

from lark import GrammarError, Lark, UnexpectedCharacters, UnexpectedToken

from src.config_parser import JSONConfig, YAMLConfig
from src.extraction_factory import Extraction
from src.file_factory import FileReader, PUMLWriter, PromptReader, RecursiveSubdirectories, FileWriter
from src.git_master import GitMaster
from src.llm_processing_pipeline import Code, Text, Think, event_consumer, line_assembler, parser
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


def llm_test():
    yaml = YAMLConfig('tests/configs/autodocs.yaml')

    code = FileReader(target_path="src/schemas/umlblock_schema.py").text
    api = LLM_API(config=yaml.config, model="MiniMaxAI/MiniMax-M3-MXFP8")

    stream = api.request_stream(
        rule=PromptReader(target_path="prompts/grammar2.md", data={"language": "python"}).getResolved(),
        prompt=code
    )

    chunks = []
    for chunk in stream:
        print(chunk, end="", flush=True)
        chunks.append(chunk)


    _, text = Extraction("").extractThinkTagPrefix(str("".join(chunks)).replace("<|open|>", ""))

    print(text)

    try:
        parser = Lark(
            grammar=text,
            start="program",
            parser="earley",
            ambiguity='explicit'
        )
        tree = parser.parse(code)

        print("\n\n")
        print(tree.pretty())
    except GrammarError as e:
        print(f"ERROR grammar is faulty: {e}")
    except UnexpectedToken as t:
        print(f"ERROR made an UnexpectedToken: {t}")
    except UnexpectedCharacters as c :
        print(f"ERROR made an UnexpectedCharacters: {c}")


def get_chars(file):
    with open(file, "r") as f:
        while True:
            ch = f.read(1)
            if ch == "":
                break
            yield ch

def get_chunks(file, size=5):
    with open(file, "r") as f:
        while chunk := f.read(size):
            yield chunk

def extraction_stream():
    with open(".autodocs/llm_logs/2026-08-05_15-46-44_text.md", "w") as text_result_file, open(".autodocs/llm_logs/2026-08-05_15-46-44_think.md", "w") as think_file:
        event_consumer(parser(
            line_assembler(
                get_chunks(".autodocs/llm_logs/2026-08-05_15-46-44.md")
            )
        ), think_file, text_result_file)


if __name__ == "__main__":
    # main()
    # llm_test()
    extraction_stream()
