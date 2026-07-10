from time import sleep

from src.config_parser import YAMLConfig
from src.file_factory import FileWriter
from src.git_master import GitMaster
from src.rendering import PlantUMLRendering
from src.plantuml_converter import PlantUMLConverter
from src.request import LLM_API
from src.terminal_master import TerminalMaster


def main():
    print("Converting Code to PlantUML and rendering...")

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

    print(GitMaster(yaml.config).diff())

    # for i in range(len(model_list)):
    #     print(f"Applying Model [{model_list[i]}]...")

    #     # file_path = target_path + f"test_{i}.puml"
    #     # PlantUMLConverter(
    #     #     config=yaml.config,
    #     #     model=model_list[i]
    #     # ).convert(
    #     #     source_file=source,
    #     #     target_path=file_path
    #     # )
    #     # PlantUMLRendering(config=yaml.config, render_source_path=file_path).render()

    #     if yaml.config.git.commit.allow_auto_msg:
    #         # diff_msg_path = "tests/example_data/git_diff"
    #         # with open(diff_msg_path, 'r') as r:
    #         #     git_diff = r.read()

    #         git_diff = GitMaster(yaml.config).diff()

    #         api = LLM_API(config=yaml.config, model=model_list[i])

    #         with open(yaml.config.git.commit.sysprompt.file_path, 'r') as r:
    #             prompt = r.read()

    #         result = ""
    #         try:
    #             result = api.call(rule=prompt, prompt=git_diff)
    #         except ValueError as err:
    #             print(err)

    #         target_path = "tests/results/benchmarks/commit_msg/"
    #         FileWriter(target_path=target_path+f"msg_{i}", content=result)

    #         # diff_msg_path = "tests/example_data/git_diff"
    #         # with open(diff_msg_path, 'r') as r:
    #         #     git_diff = r.read()
    #         # msg = TerminalMaster(config=yaml.config).openVIM(git_diff)
    #         # print(msg)

    #     sleep(yaml.config.llm_service.api.request_delay_seconds)



if __name__ == "__main__":
    main()
