
Manuall for the full install: [https://plantuml.com/starting](https://plantuml.com/starting)


For now, you need to download the renderer manually
`wget https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar -P resources/`

To render a *.puml file manually, run `java -jar resources/plantuml.jar <your_puml_file_path>`.

Valid diagrams are: [https://plantuml.com/guide](https://plantuml.com/guide)

For `tests/configs/commit-convention.md` prompt [https://www.conventionalcommits.org/en/v1.0.0/](https://www.conventionalcommits.org/en/v1.0.0/) was used.


## Smart commit
Add the script to the following git-hook:
```sh
echo '#!/bin/sh

uv run python3 smart_commit.py "$1"' >> ./.git/hooks/prepare-commit-msg
```
You may need to give the necessary file permissions:
`chmod +x ./.git/hooks/prepare-commit-msg`
