from pathlib import Path

from argparse import ArgumentParser

from src.config_parser import YAMLConfig
from src.git_master import GitMaster
from src.request import LLM_API


def main():
    parser = ArgumentParser()
    parser.add_argument("commit_msg_file")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file",
    )
    args = parser.parse_args()

    message_file = Path(args.commit_msg_file)
    yaml = YAMLConfig(args.config)

    print("Generating Commit Message...")
    git_diff = GitMaster(yaml.config).diff()
    api = LLM_API(config=yaml.config)

    with open(yaml.config.git.commit.sysprompt.file_path, 'r') as r:
        prompt = r.read()

    result = ""
    try:
        result = api.request(rule=prompt, prompt=git_diff)
    except ValueError as err:
        print(err)

    if result:
        result += f"\n\n\nReviewed-by: {yaml.config.git.commit.llm_model}"

    message_file.write_text(result, encoding="utf-8")


main()
