#!/usr/bin/env python3

import os
import sys

def ensure_uv():
    # from: https://github.com/NormanTUD/roARM-m2/blob/main/bootstrap.py (somewhat modified, without dialout())

    from pathlib import Path
    root = Path(__file__).resolve().parent.as_posix()
    script = os.path.abspath(sys.argv[0])

    if os.environ.get("_UV_SAFE_ENV") == "1":
        return

    os.environ["_UV_SAFE_ENV"] = "1"

    from datetime import datetime, timedelta, timezone
    if not os.environ.get("UV_EXCLUDE_NEWER"):
        past = (datetime.now(timezone.utc) - timedelta(days=8)).strftime("%Y-%m-%dT%H:%M:%SZ")
        os.environ["UV_EXCLUDE_NEWER"] = past
    else:
        raise SystemError("ensure_dialout() needed")

    try:
        os.execvpe(
            "uv",
            [
                "uv",
                "run",
                "--quiet",
                "--project", root,
                script,
                "--",
                *sys.argv[1:],
            ],
            os.environ,
        )
    except FileNotFoundError:
        print("uv not installed. Install: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)


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

    ROOT_LOCAL = Path.cwd()
    root_default = Path(__file__).resolve().parent

    hasGitEnv = Path(ROOT_LOCAL / '.git').exists() and Path(ROOT_LOCAL / '.git').is_dir()

    config_path = args.config_path if args.config_path else Path(root_default / "tests/configs/autodocs.yaml").as_posix()

    autodocs_file = Path(ROOT_LOCAL / ".autodocs")
    autodocs_config_file = Path(ROOT_LOCAL / "autodocs.yaml")
    if autodocs_file.exists() or autodocs_config_file.exists():
        print("Some already existing autodocs-files detected. Run `autodocs remove` for full cleanup.")
        sys.exit(1)

    try:
        config = YAMLConfig(config_path)
    except FileNotFoundError as r:
        print(f"File not found: {r}")
        sys.exit(1)
    except ConfigError as e:
        print(e)
        sys.exit(1)

    config.createFile(Path(ROOT_LOCAL / "autodocs.yaml"))

    # create .autodocs directory and children (logs, cache, ...)
    print("Creating new .autodocs directory")
    os.mkdir(f"{ROOT_LOCAL}/.autodocs")

    # check env
    if not Path(ROOT_LOCAL / '.autodocs').exists() or not Path(ROOT_LOCAL / '.autodocs').is_dir():
        raise EnvironmentError(".autodocs/ not found")

    autodocs_path = Path(ROOT_LOCAL / ".autodocs")
    os.mkdir(os.path.join(autodocs_path, PUML_DIR))
    os.mkdir(os.path.join(autodocs_path, IMG_DIR))
    os.mkdir(os.path.join(autodocs_path, LLM_DIR))
    os.mkdir(os.path.join(autodocs_path, LOG_DIR))
    os.mkdir(os.path.join(autodocs_path, PROMPTS_DIR))
    # TODO: create required cache directory?

    replacement_data = {
        "project_title": "Project",
        "LLM_MODEL": config.config.autodocs.model,
        "valid_umls": ','.join(config.config.autodocs.valid_diagrams.umls),
        "valid_non_umls": ','.join(config.config.autodocs.valid_diagrams.non_umls)
    }

    docs_header = PromptReader(
        Path(root_default / config.config.autodocs.prompts.header_path),
        replacement_data
    )

    prompt = PromptReader(
        Path(root_default / config.config.autodocs.prompts.path),
        replacement_data
    )

    docs_footer = PromptReader(
        Path(root_default / config.config.autodocs.prompts.footer_path),
        replacement_data
    )

    with open(Path(ROOT_LOCAL / ".autodocs/setup.json"), mode="w") as f:
        # TODO: change json to class?
        f.write(json.dumps(
            {
                "config_path": config_path,
                "root_path": str(ROOT_LOCAL),
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

    FileWriter(f"{str(ROOT_LOCAL)}/.autodocs/{config.config.autodocs.prompts.header_path}").write(docs_header.text)
    FileWriter(f"{str(ROOT_LOCAL)}/.autodocs/{config.config.autodocs.prompts.path}").write(prompt.text)
    FileWriter(f"{str(ROOT_LOCAL)}/.autodocs/{config.config.autodocs.prompts.footer_path}").write(docs_footer.text)

    try:
        gitignore_content = FileReader(ROOT_LOCAL / '.gitignore').text
        ignore_default_content = FileReader(root_default / 'prompts/.autodocs-ignore-default').text

        FileWriter(f"{str(ROOT_LOCAL)}/.autodocs/{config.config.autodocs.files_ignore_path}").write(
            f"{gitignore_content}\n\n{ignore_default_content}\n"
        )
    except:
        print("No .gitignore file found")
        sys.exit(1)

    # add to .gitignore if in git env
    if hasGitEnv:
        print("Add files to .gitignore")
        FileWriter(
            target_path=f'{ROOT_LOCAL / ".gitignore"}',
            mode='a'
        ).write(content='# AutoDocs\n.autodocs\n.autodocs/*')

    # configure git-hooks
    if args.git and hasGitEnv:
        commit_convention = PromptReader(
            config.config.git.commit.sysprompt.file_path,
            replacement_data
        )
        FileWriter(f"{str(ROOT_LOCAL)}/.autodocs/{config.config.git.commit.sysprompt.file_path}").write(commit_convention.text)

        print("Add to script to ./.git/hooks/prepare-commit-msg")
        FileWriter(
            target_path=f'{ROOT_LOCAL / "./.git/hooks/prepare-commit-msg"}',
            mode='a'
        ).write(content=f'uv run python3 auto_commit_msg.py .git/COMMIT_EDITMSG --config "autodocs.yaml"')


def remove(args):
    ROOT_LOCAL = Path.cwd()
    ROOT_DEFAULT = Path(__file__).resolve().parent

    print("Remove Autodocs environment...")

    if Path(ROOT_LOCAL / "autodocs.yaml").exists() and Path(ROOT_LOCAL / "autodocs.yaml").is_file():
        os.remove(ROOT_LOCAL / "autodocs.yaml")

    if Path(ROOT_LOCAL / ".autodocs").exists() and Path(ROOT_LOCAL / ".autodocs").is_dir():
        shutil.rmtree(ROOT_LOCAL / ".autodocs")

    if Path(ROOT_LOCAL / ".gitignore").exists() and Path(ROOT_LOCAL / ".gitignore").is_file():
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
                        ROOT_LOCAL / ".gitignore"
                    ],
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Entry removal of '{line}' in .gitignore failed: {e}")

    if Path(ROOT_LOCAL / ".git/hooks/prepare-commit-msg").exists() and Path(ROOT_LOCAL / ".git/hooks/prepare-commit-msg").is_file():
        try:
            subprocess.run(
                [
                    "sed",
                    "-i",
                    r'/uv run python3 smart_commit.py \.git\/COMMIT_EDITMSG --config "autodocs\.yaml"/d',
                    ROOT_LOCAL / ".git/hooks/prepare-commit-msg"
                ],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Removal of githook failed in .git/hooks/prepare-commit-msg: [{e}]")


def docs(args):
    try:
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

    except FileNotFoundError as e:
        print(f"{e}. Is the AutoDocs environment initialized? Run '... autodocs.py init'")


def main():
    sessions = []
    try:
        setup = JSONConfig(".autodocs/setup.json")
        sessions = setup.config.sessions
    except FileNotFoundError as f:
        pass
    except ConfigError as e:
        print(e)
        sys.exit(1)

    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command', required=True)

    help_parser = subparser.add_parser('help', help="Show help")
    help_parser.set_defaults(func=lambda args: help())

    init_parser = subparser.add_parser('init', help='Initializes AutoDocs on a local environment.')
    init_parser.add_argument('-c', '--config-path', type=str, default='', help='Path to default autodocs.yaml config')
    # init_parser.add_argument('-i', '--ignore-file', type=str, default='', help='Path to ignorefile')
    init_parser.add_argument('-g', '--git', action=argparse.BooleanOptionalAction, type=__str2bool, default=False, help='Include git support features like commit msg generation')
    init_parser.set_defaults(func=init)

    run_parser = subparser.add_parser('docs', help='Generating a documentation')
    run_parser.add_argument('-c', '--source-code', type=str, default='', help='Relative path to code base')
    run_parser.add_argument('-d', '--docs-file', type=str, default='docs.md', help='Relative path of returned code base documentation')
    run_parser.add_argument('-s', '--session', type=str, default='', choices=sessions, help='Specify used session (default: last session)')
    run_parser.add_argument('-m', '--mode', type=str, default='all', choices=["all", "extract", "render"], help='')
    # TODO: add --vim-edit, if mode=extract, user can edit the API result before extract/render
    run_parser.set_defaults(func=docs)

    # TODO: add readme generation

    remove_parser = subparser.add_parser('remove', help='Removes all related autodocs files and directories from project root')
    remove_parser.set_defaults(func=remove)

    args = parser.parse_args()
    args.func(args)

    # TODO: fix request_stream bug
    # TODO: timeout min only 80sec???


if __name__ == '__main__':
    ensure_uv()

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

    main()
