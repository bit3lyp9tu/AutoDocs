from pathlib import Path
import sys

from src.config_parser import YAMLConfig
from src.git_master import GitMaster
from src.request import LLM_API


def main():
    print("Generating Commit Message...")

    message_file = Path(sys.argv[1])

    yaml = YAMLConfig('tests/configs/autodocs.yaml')

    if yaml.config.git.commit.allow_auto_msg:
        git_diff = GitMaster(yaml.config).diff()

        api = LLM_API(config=yaml.config)

        with open(yaml.config.git.commit.sysprompt.file_path, 'r') as r:
            prompt = r.read()

        result = ""
        try:
            result = api.call(rule=prompt, prompt=git_diff)
        except ValueError as err:
            print(err)

        result += f"\n\n\nReviewed-by: {yaml.config.git.commit.llm_model}"

        message_file.write_text(result, encoding="utf-8")
main()
