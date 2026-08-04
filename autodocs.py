import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from src.Docs import Docs
from src.config_parser import ConfigError, JSONConfig, YAMLConfig
from src.file_factory import FileReader, FileWriter, PromptReader
from src.schemas.setup_schema import SetupSchema


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
    config_path = args.config_path if args.config_path else "tests/configs/autodocs.yaml" # TODO remove static path

    # TODO: move to single class
    print("Initializing environment...")

    root_path = Path(__file__).resolve().parent
    # TODO: add as setup parameter
    hasGitEnv = Path(root_path / '.git').exists() and Path(root_path / '.git').is_dir()

    config = YAMLConfig(config_path)
    config.createFile(Path(root_path / "autodocs.yaml"))

    # create .autodocs directory and children (logs, cache, ...)
    print("Creating new .autodocs directory")
    os.mkdir(".autodocs")

    # check env
    if not Path(root_path / '.autodocs').exists() or not Path(root_path / '.autodocs').is_dir():
        raise EnvironmentError(".autodocs/ not found")

    autodocs_path = Path(root_path / ".autodocs")
    os.mkdir(os.path.join(autodocs_path, PUML_DIR))
    os.mkdir(os.path.join(autodocs_path, IMG_DIR))
    os.mkdir(os.path.join(autodocs_path, LLM_DIR))
    os.mkdir(os.path.join(autodocs_path, LOG_DIR))
    os.mkdir(os.path.join(autodocs_path, PROMPTS_DIR))
    # TODO: create required cache directory?

    replacement_data = {
        "project_title": "Project",
        "LLM_MODEL": config.config.autodocs.model
    }

    docs_header = PromptReader(
        config.config.autodocs.prompts.header_path,
        replacement_data
    )

    prompt = PromptReader(
        config.config.autodocs.prompts.path,
        replacement_data
    )

    docs_footer = PromptReader(
        config.config.autodocs.prompts.footer_path,
        replacement_data
    )

    with open(".autodocs/setup.json", mode="w") as f:
        # TODO: change json to class?
        f.write(json.dumps(
            {
                "config_path": config_path,
                "root_path": str(root_path),
                "autodocs_path": str(autodocs_path),
                "resolved_prompt": prompt.getResolved(),
                "docs_header": docs_header.getResolved(),
                "docs_footer": docs_footer.getResolved(),
                "sessions": {}
            },
            indent=4,
            sort_keys=False
        )
    )

    FileWriter(f".autodocs/{config.config.autodocs.prompts.header_path}").write(docs_header.text)
    FileWriter(f".autodocs/{config.config.autodocs.prompts.path}").write(prompt.text)
    FileWriter(f".autodocs/{config.config.autodocs.prompts.footer_path}").write(docs_footer.text)

    try:
        FileWriter(f".autodocs/{config.config.autodocs.files_ignore_path}").write(FileReader(".gitignore").text)
    except:
        print("No .gitignore file found")
        sys.exit(1)

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
        execution_layer = 0

        match args.mode:
            case "all":
                execution_layer = 0
            case "extract":
                execution_layer = 1
            case "render":
                execution_layer = 2

        if execution_layer <= 0:
            print("Requesting LLM docs...")
            docs.createContent(args.source_code, args.session)

        if execution_layer <= 1:
            print("Creating PUML diagrams...")
            docs.createPUML(args.docs_file, args.session)

        if execution_layer <= 2:
            print("Render PUML diagrams...")
            docs.renderPUML(args.session)

    else:
        print("Environment is not initialized (see --help)")


def main():

    sessions = []
    try:
        setup = JSONConfig(".autodocs/setup.json")
        sessions = setup.config.sessions
    except( ConfigError, FileNotFoundError) as e:
        print(e)

    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command', required=True)

    help_parser = subparser.add_parser('help', help="Show help")
    help_parser.set_defaults(func=lambda args: help())

    init_parser = subparser.add_parser('init', help='Initializes AutoDocs on a local environment.')
    init_parser.add_argument('-c', '--config-path', type=str, default='', help='Path to default autodocs.yaml config')
    init_parser.add_argument('-g', '--git', type=__str2bool, default=False, help='Include git support features like commit msg generation')
    init_parser.set_defaults(func=init)

    run_parser = subparser.add_parser('run', help='Running the process')
    run_parser.add_argument('-c', '--source-code', type=str, default='', help='Relative path to code base')
    run_parser.add_argument('-d', '--docs-file', type=str, default='docs.md', help='Relative path of returned code base documentation')
    run_parser.add_argument('-s', '--session', type=str, default='', choices=sessions, help='Specify used session (default: last session)')
    run_parser.add_argument('-m', '--mode', type=str, default='all', choices=["all", "extract", "render"], help='')
    # TODO: add --vim-edit, if mode=extract, user can edit the API result before extraction/processing
    run_parser.set_defaults(func=run)

    remove_parser = subparser.add_parser('remove', help='Removes all related autodocs files and directories from project root')
    remove_parser.set_defaults(func=remove)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
