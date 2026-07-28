import argparse
import os
from pathlib import Path
import shutil
import subprocess

from src.Docs import Docs
from src.config_parser import YAMLConfig
from src.file_factory import FileWriter


def __str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "y", "true", "t", "1"):
        return True
    if v.lower() in ("no", "n", "false", "f", "0"):
        return False
    raise argparse.ArgumentTypeError("Boolean value expected.")

def help():
    print("Helping...")

def init(args):
    print("Initializing environment...")

    current_path = Path(__file__).resolve().parent
    hasGitEnv = Path(current_path / '.git').exists() and Path(current_path / '.git').is_dir()

    config_path = "tests/configs/autodocs.yaml"
    config = YAMLConfig(config_path)
    config.createFile(Path(current_path / "autodocs.yaml"))

    # create .autodocs directory and children (logs, cache, ...)
    print("Creating new .autodocs directory")
    os.mkdir(".autodocs")

    docs = Docs(current_path, config_path)

    # add to .gitignore if in git env
    if hasGitEnv:
        print("Add files to .gitignore")
        FileWriter(
            target_path=f'{current_path / ".gitignore"}',
            mode='a'
        ).write(content='# AutoDocs\n.autodocs\n.autodocs/*')

    # configure git-hooks
    if args.git and hasGitEnv:
        print("Add to script to ./.git/hooks/prepare-commit-msg")
        FileWriter(
            target_path=f'{current_path / "./.git/hooks/prepare-commit-msg"}',
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


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command', required=True)

    help_parser = subparser.add_parser('help', help="Show help")
    help_parser.set_defaults(func=lambda args: help())

    init_parser = subparser.add_parser('init', help='Initializes AutoDocs on a local environment.')
    init_parser.add_argument('-g', '--git', type=__str2bool, default=True, help='Include git support features like commit msg generation')
    init_parser.add_argument('-u', '--uml', type=__str2bool, default=True, help='Include rendering uml diagrams from code')
    init_parser.set_defaults(func=init)

    remove_parser = subparser.add_parser('remove', help='Removes all related autodocs files and directories from project root.')
    remove_parser.set_defaults(func=remove)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
