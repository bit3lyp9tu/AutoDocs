# AutoDocs

# Workflow for AutoDocs - Tool

1. install autodocs from repo to e.g `~/Documents/tools/`
this location contains dependencies like python-venv and other requred packages like jar files for rendering, ...

2. when wanting to use autodocs tool for a project, run `autodocs init` at the requred location
it creates in `project/`:

project/autodocs.yaml
project/.autodocs/...
                 /logs/...
                 /cache/...
                 ...
project/...

configures some other stuff like git-hooks, ...


3. now to use the autodocs tool, it can be localy run with `autodocs <command>`

Examples for commands:
```
autodocs init
autodocs sync
autodocs analyze
autodocs build
autodocs test
autodocs doctor
autodocs clean
autodocs update
```

`autodocs doctor`:
✓ Python found
✓ Java found
✓ Git installed
✓ Git hooks installed
✓ Configuration valid
✓ Cache writable
✓ Project initialized

# autodocs.py --reload

<!-- TODO -->
# autodocs.py --init
- setting up env `.autodocs/`
- create default yaml-config: `.autodocs/config.yaml`





Manuall for the full install: [https://plantuml.com/starting](https://plantuml.com/starting)


For now, you need to download the renderer manually
`wget https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar -P resources/`

To render a *.puml file manually, run `java -jar resources/plantuml.jar <your_puml_file_path>`.

Valid diagrams are: [https://plantuml.com/guide](https://plantuml.com/guide)

For `tests/configs/commit-convention.md` prompt [https://www.conventionalcommits.org/en/v1.0.0/](https://www.conventionalcommits.org/en/v1.0.0/) was used.

---





# autodocs.py --commit
- generates commit msg by mml

Add the script to the following git-hook:
```sh
echo '#!/bin/sh

uv run python3 smart_commit.py .git/COMMIT_EDITMSG --config "tests/configs/autodocs.yaml"' >> ./.git/hooks/prepare-commit-msg
```
You may need to give the necessary file permissions:
`chmod +x ./.git/hooks/prepare-commit-msg`

# autodocs.py --uml
- generates uml diagrams based on code

# autodocs.py --description
- descibes the code







