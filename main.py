from time import sleep

from src.config_parser import YAMLConfig
from src.rendering import PlantUMLRendering
from src.plantuml_converter import PlantUMLConverter


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
    # target_path = f"tests/results/benchmarks/uml_class_diagram/"
    source = "tests/example_data/db_schema.py"
    target_path = f"tests/results/benchmarks/entity_relation_diagram/"

    yaml = YAMLConfig('tests/configs/autodocs.yaml')

    for i in range(len(model_list)):
        print(f"Applying Model [{model_list[i]}]...")

        file_path = target_path + f"test_{i}.puml"

        PlantUMLConverter(
            config=yaml.config,
            model=model_list[i]
        ).convert(
            source_file=source,
            target_path=file_path
        )

        PlantUMLRendering(config=yaml.config, render_source_path=file_path).render()

        sleep(yaml.config.llm_service.api.request_delay_seconds)

if __name__ == "__main__":
    main()
