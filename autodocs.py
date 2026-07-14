import argparse
from pathlib import Path

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

    # create .autodocs directory and children (logs, cache, ...)
    # TODO

    # add to .gitignore if in git env
    if hasGitEnv:
        print("Add files to .gitignore")
        FileWriter(
            target_path=f'{current_path / ".gitignore"}',
            content='\n\n# AutoDocs\n.autodocs\n.autodocs/*',
            mode='a'
        )

    # configure git-hooks
    if args.git and hasGitEnv:
        print("Add to script to ./.git/hooks/prepare-commit-msg")
        FileWriter(
            target_path=f'{current_path / "./.git/hooks/prepare-commit-msg"}',
            content=f'uv run python3 smart_commit.py .git/COMMIT_EDITMSG --config "autodocs.yaml"',
            mode='a'
        )

    # create default autodocs.yaml config (only includes git attribute if args.git==True)
    # TODO


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command', required=True)

    help_parser = subparser.add_parser('help', help="Show help")
    help_parser.set_defaults(func=lambda args: help())

    init_parser = subparser.add_parser('init', help='Initializes AutoDocs on a local environment.')
    init_parser.add_argument('-g', '--git', type=__str2bool, default=True, help='Include git support features like commit msg generation')
    init_parser.add_argument('-u', '--uml', type=__str2bool, default=True, help='Include rendering uml diagrams from code')
    init_parser.set_defaults(func=init)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
