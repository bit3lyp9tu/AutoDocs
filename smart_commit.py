from pathlib import Path
import sys

from src.config_parser import YAMLConfig
from src.git_master import GitMaster
from src.request import LLM_API
from src.terminal_master import TerminalMaster


def main():
    message_file = Path(sys.argv[1])

    yaml = YAMLConfig('tests/configs/autodocs.yaml')

    if yaml.config.git.commit.allow_auto_msg:
        git_diff = GitMaster(yaml.config).diff()

        api = LLM_API(config=yaml.config, model="openGPT-X/Teuken-7B-instruct-v0.6")

        with open(yaml.config.git.commit.sysprompt.file_path, 'r') as r:
            prompt = r.read()

        result = ""
        try:
            result = api.call(rule=prompt, prompt=git_diff)
        except ValueError as err:
            print(err)

        if yaml.config.git.commit.vim_examination:
            msg = TerminalMaster(config=yaml.config).openVIM(result)
            print(msg)
            message_file.write_text(msg, encoding="utf-8")
        else:
            message_file.write_text(result, encoding="utf-8")

main()
