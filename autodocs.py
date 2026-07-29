import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

from src.Docs import Docs
from src.config_parser import YAMLConfig
from src.file_factory import FileWriter, PromptReader


def __str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "y", "true", "t", "1"):
        return True
    if v.lower() in ("no", "n", "false", "f", "0"):
        return False
    raise argparse.ArgumentTypeError("Boolean value expected.")

def help():
    # TODO: resume
    print("Helping...")

PUML_DIR = "puml"
IMG_DIR = "img"
LLM_DIR = "llm_logs"
LOG_DIR = "log"
PROMPTS_DIR = "prompts"

def init(args):
    # TODO: move to single class
    print("Initializing environment...")

    root_path = Path(__file__).resolve().parent
    # TODO: add as setup parameter
    hasGitEnv = Path(root_path / '.git').exists() and Path(root_path / '.git').is_dir()

    # TODO: fix strange yaml dump
    # TODO: use dynamic path
    config_path = "tests/configs/autodocs.yaml"
    config = YAMLConfig(config_path)
    config.createFile(Path(root_path / "autodocs.yaml"))

    # create .autodocs directory and children (logs, cache, ...)
    print("Creating new .autodocs directory")
    os.mkdir(".autodocs")

    # check env
    if not Path(root_path / '.autodocs').exists() or not Path(root_path / '.autodocs').is_dir():
        raise EnvironmentError(".autodocs/ not found")

    autodocs_path = Path(root_path / ".autodocs")

    config = YAMLConfig(config_path).config
    os.mkdir(os.path.join(autodocs_path, PUML_DIR))
    os.mkdir(os.path.join(autodocs_path, IMG_DIR))
    os.mkdir(os.path.join(autodocs_path, LLM_DIR))
    os.mkdir(os.path.join(autodocs_path, LOG_DIR))
    os.mkdir(os.path.join(autodocs_path, PROMPTS_DIR))
    # TODO: create required cache directory?

    with open(".autodocs/setup.json", mode="w") as f:
        # TODO: change json to class?
        f.write(json.dumps(
            {
                "config_path": config_path,
                "root_path": str(root_path),
                "autodocs_path": str(autodocs_path),
                "resolved_prompt": PromptReader(
                    "prompts/docs_summary.md",  # TODO: use path from config
                    {
                        "project_title": "Project"
                    }
                ).getResolved(),
                "sessions": {}
            },
            indent=4,
            sort_keys=False
        )
    )

    # TODO: copy docs_summary.md prompt to .autodocs/prompts

    # add to .gitignore if in git env
    if hasGitEnv:
        print("Add files to .gitignore")
        FileWriter(
            target_path=f'{root_path / ".gitignore"}',
            mode='a'
        ).write(content='# AutoDocs\n.autodocs\n.autodocs/*')

    # configure git-hooks
    if args.git and hasGitEnv:
        print("Add to script to ./.git/hooks/prepare-commit-msg")
        FileWriter(
            target_path=f'{root_path / "./.git/hooks/prepare-commit-msg"}',
            mode='a'
        ).write(content=f'uv run python3 smart_commit.py .git/COMMIT_EDITMSG --config "autodocs.yaml"')


def remove(args):
    current_path = Path(__file__).resolve().parent

    print("Remove Autodocs environment...")

    if Path(current_path / "autodocs.yaml").exists() and Path(current_path / "autodocs.yaml").is_file():
        os.remove("autodocs.yaml")

    if Path(current_path / ".autodocs").exists() and Path(current_path / ".autodocs").is_dir():
        shutil.rmtree(".autodocs")

    if Path(current_path / ".gitignore").exists() and Path(current_path / ".gitignore").is_file():
        for line in [
            '/# AutoDocs/d',
            '/.autodocs/d'
        ]:
            try:
                subprocess.run(
                    [
                        "sed",
                        "-i",
                        line,
                        ".gitignore"
                    ],
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Entry removal of '{line}' in .gitignore failed: {e}")

    if Path(current_path / ".git/hooks/prepare-commit-msg").exists() and Path(current_path / ".git/hooks/prepare-commit-msg").is_file():
        try:
            subprocess.run(
                [
                    "sed",
                    "-i",
                    r'/uv run python3 smart_commit.py \.git\/COMMIT_EDITMSG --config "autodocs\.yaml"/d',
                    ".git/hooks/prepare-commit-msg"
                ],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Removal of githook failed in .git/hooks/prepare-commit-msg: [{e}]")


def run(args):

    # TODO: check if init exists
    if True:
        docs = Docs()

        print("Requesting LLM docs...")
        docs.createContent(args.code)

        print("Creating PUML diagrams...")
        docs.createPUML(args.docs_file)

        print("Render PUML diagrams...")
        docs.renderPUML()
    else:
        print("Environment is not initialized (see --help)")


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command', required=True)

    help_parser = subparser.add_parser('help', help="Show help")
    help_parser.set_defaults(func=lambda args: help())

    init_parser = subparser.add_parser('init', help='Initializes AutoDocs on a local environment.')
    # TODO: add config path parameter
    init_parser.add_argument('-g', '--git', type=__str2bool, default=False, help='Include git support features like commit msg generation')
    # TODO: redundant to subparser run?
    init_parser.add_argument('-u', '--uml', type=__str2bool, default=True, help='Include rendering uml diagrams from code')
    init_parser.set_defaults(func=init)

    run_parser = subparser.add_parser('run', help='')
    run_parser.add_argument('-c', '--code', type=str, default="src", help='Path to code base.')
    # TODO: add ai disclaimer to summary
    run_parser.add_argument('-d', '--docs-file', type=str, default="docs.md", help='Path of code base documentation')
    # TODO: add argument --all?
    # TODO: add argument --extract <session>?
    # TODO: --render <session> in single subparser?
    run_parser.set_defaults(func=run)

    remove_parser = subparser.add_parser('remove', help='Removes all related autodocs files and directories from project root.')
    remove_parser.set_defaults(func=remove)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
