import json
from pathlib import Path, PurePosixPath
import re
from time import sleep
from typing import Generator, Literal

from lark import GrammarError, Lark, UnexpectedCharacters, UnexpectedToken
from openai import BadRequestError

from src.Agent import Agent
from src.config_parser import JSONConfig, YAMLConfig
from src.extraction_factory import Extraction
from src.file_factory import FileReader, PUMLWriter, PromptReader, RecursiveSubdirectories, FileWriter
from src.git_master import GitMaster
from src.llm_processing_pipeline import Code, Text, Think, event_consumer, line_assembler, parser, tag_extraction
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
    api = LLM_API(config=yaml.config, model="moonshotai/Kimi-K3")

    stream = api.request_stream(
        rule=PromptReader(target_path="prompts/grammar2.md", data={"language": "python"}).getResolved(),
        prompt=code
    )

    chunks = []
    for chunk in stream:
        print(chunk, end="", flush=True)
        chunks.append(chunk)


    _, text = Extraction("").extractThinkTagPrefix(str("".join(chunks)).replace("<|open|>", ""))

    print("################")
    print(text)
    print("################")

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

# def extraction_stream():
#     session = "2026-08-05_15-46-44"

#     with open(f".autodocs/llm_logs/{session}_text.md", "w") as text_result_file, open(f".autodocs/llm_logs/{session}_think.md", "w") as think_file:
#         event_consumer(parser(
#             line_assembler(
#                 get_chunks(f".autodocs/llm_logs/{session}.md")
#             )
#         ), f".autodocs/puml/{session}", think_file, text_result_file)


def llm_conversation():

    code = """
from pydantic import BaseModel


class Tag(BaseModel):
    type: str
    name: str

class Block(BaseModel):
    tag: Tag
    language: str
    content: str

class Document(BaseModel):
    blocks: list[Block]
"""

    with open("tests/example_data/task_manager.py") as f:
        code2 = f.read()

    yaml = YAMLConfig('tests/configs/autodocs.yaml')
    # models = [
    #     "google/gemma-4-26B-A4B-it",
    #     "google/gemma-4-31B-it",
    #     "MiniMaxAI/MiniMax-M3-MXFP8",
    #     "moonshotai/Kimi-K3",
    #     "openai/gpt-oss-120b",
    #     "zai-org/GLM-5.2-FP8"
    # ]

    rule = """
        Based on the given python code input, create a formal grammar schema for it.
        Ignore commends in the code.
        Follow the EBNF syntax for it:
        - ignore comments in code
        - use `program` as start variable
        - when defining a variable, use `:` instead of `=`, e.g. like this: `variable: values`
        - define each rule only once
        - use lowercase variables, unless its a token then use uppercase
        - use regular expressions to describe a token, put the regex in between `/regex/`, avoid using `/.*/`
        - do not use variables or TOKENS in regular expressions
        - do not forget to account for whitespaces
        - do not return it as markdown
        - do not end the line with an `;`
        - at the end of the grammar add %import common.WS and %ignore WS
        - make sure that you only have one grammar rule per line

        Your answer gets directly parsed.
        Should the parser fail, you are provided with the corresponding error message.
        Fix your Grammar Schema based on this error and return your new result.
    """

    model = "MiniMaxAI/MiniMax-M3-MXFP8"
    # model = "moonshotai/Kimi-K3"

    data = {}
    agent = Agent(yaml.config, rule, model)

    for code_chunks in code_splitter(yaml.config, "MiniMaxAI/MiniMax-M3-MXFP8", code2):
        tag = code_chunks.reverence_tag.replace("{{", "").replace("}}", "")
        model_tag = model.split("/")[-1].split("-")[0].lower()
        print(f"Code Chunk: {tag}")
        # print(code_chunks.content)
        retries_counter, answer, tree = agent.run(code_chunks.content, f"test2_{model_tag}_{tag}")
        print(answer)
        print("Counter:", retries_counter)
        # try:
        # except Exception as e:
        #     print(e)

        sleep(2)


def parser_test():

    text = """
program: statement

statement: typed_assignment

typed_assignment: NAME ":" TYPE "=" value

value: list_literal

list_literal: "[" "]"

NAME: /[a-zA-Z_][a-zA-Z_0-9]*/
TYPE: "list"

%import common.WS
%ignore WS
    """

# ignore whitespaces

    code = """
tasks: list = []
    """

    # s = []
    # for chunk in tag_extraction("moonshotai/Kimi-K3", get_chunks("tests/results/ast_generator/full_result_log_3_0.md")):
    #     if type(chunk) == Think:
    #         # print(chunk.content, end="", flush=True)
    #         s.append(chunk.content)

    st = text#''.join(s).split("<|close|> message ")[-1]

    print(st)

    try:
        parser = Lark(
            grammar=st,
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


def code_splitter(config, model, code):
    api = LLM_API(config, model)

    rule = """
        Your task is to split the code you are given into chunks.
        For each chunk you return put it in a markdown code-block and lable it as python.
        You may decide the size of an chunk, but try to keep them as small as possible, also try to group logical steps together.
        You also have to give each chunk a tag, surrounded by `{{}}`.

        Here is an example:
        {{SIMPLE_PRINT}}
        ```python
        print('Hello World')
        ```

        You can ignore all comments.

        DO NOT CHANGE ANYTHING IN THE CODE!
    """

    response = None
    try:
        response = api.request_stream(
            rule=rule,
            prompt=code,
            check_for_alt_models=False
        )
    except BadRequestError as e:
        error = e.body.get("error", {}) if isinstance(e.body, dict) else {}

        if (
            error.get("code") == "context_length_exceeded"
            or "context_length_exceeded" in str(e)
        ):
            print("Tokenlimit exceeded")
        else:
            raise

    for chunk in tag_extraction(model, line_assembler(response), name_tag=r'\{\{[\w_]+\}\}'):
        if type(chunk) == Code:
            yield chunk


if __name__ == "__main__":
    # main()
    # llm_test()
    # extraction_stream()
    llm_conversation()
    # parser_test()
