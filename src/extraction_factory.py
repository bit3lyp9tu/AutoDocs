import re

from lark import Lark, Transformer

from src.umlblock_schema import Tag, Block, Document


class ToModels(Transformer):
    def tag(self, items):
        return Tag(
            type=items[0],
            name=items[1],
        )
    def block(self, items):
        return Block(
            tag=items[0],
            language=items[1],
            content=items[2]
        )
    def start(self, items):
        return Document(blocks=items)

class Extraction:
    def __init__(self, text) -> None:
        self.text = text

    def extractTags(self, tag_prefix) -> list[str]:
        return [tag for tag in re.findall(r'\{\{.*\}\}', self.text) if tag_prefix in tag]

    def extractTagNames(self, tag_prefix) -> list[str]:
        return [str(tag).replace('{{', '').replace('}}', '').replace(tag_prefix, '') for tag in re.findall(r'\{\{.*\}\}', self.text) if tag_prefix in tag]

    def extractPlantUML(self, tag_infix: str):
        cleared_text = []
        extraction: dict[str, str] = {}
        full_tag = ""
        pointer = -1

        lines = self.text.split("\n")
        for i in range(len(lines)):
            line: str = lines[i]

            # start
            if "```plantuml" in line:
                if i > 0:
                    full_tag = re.findall(r'\{\{TAG_\w+_\w+\}\}', lines[i-1])[0]
                    if full_tag and str("{{TAG_" + tag_infix) in full_tag and i < len(lines) and "@startuml" in lines[i+1]:
                        pointer = i

            # end
            if "```" in line and "plantuml" not in line and pointer != -1:
                if "@enduml" in lines[i-1]:
                    if full_tag:
                        sublist = lines[pointer:i+1]
                        extraction[full_tag] = '\n'.join(sublist[1:-1])

                        pointer = -1
                        full_tag = ""

            if pointer == -1 and "```" not in line:
                cleared_text.append(line)

        return extraction, '\n'.join(cleared_text)

    def setPointersAll(self, text: str, keys: list[str], paths: dict[str, str], tag: str):
        result = text

        for k in keys:
            uml_name = k.replace("}}", "").replace(str("{{TAG_" + tag + "_"), "")
            url = f"{paths[k]}/{uml_name}.puml"
            alt = f"{uml_name}"
            pattern = f"![{alt}]({url})"

            result = result.replace(k, pattern)

        return result

    def createPaths(self, keys: list[str], path: str, tag: str):
        results: dict[str, str] = {}

        for i in keys:
            uml_name = i.replace("}}", "").replace(str("{{TAG_" + tag + "_"), "")
            url = f"{path}/{uml_name}.puml"

            results[i] = url

        return results
