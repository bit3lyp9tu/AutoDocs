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

    def extractPlantUML(self):
        grammar = r"""
            start: PREFIX* block* PREFIX?

            block: tag "```" LANGUAGE " " CONTENT "```"

            PREFIX: /.+[^\n\{\{]/

            tag: "{{" TYPE "_" NAME "}}"
            TYPE: /[A-Za-z_][A-Za-z0-9_]*/
            NAME: /[A-Za-z_][A-Za-z0-9_]*/

            LANGUAGE: /plantuml/
            CONTENT: /.+[^```]/

            NEWLINE: /\n/

            %import common.WS
            %ignore WS
        """

        parser = Lark(
            grammar,
            parser="cyk",
            transformer=ToModels(),
        )

        # document: Document = parser.parse(self.text)
        # document.blocks

        tree = parser.parse(self.text)
        document = ToModels().transform(tree)

        document_dict = document.model_dump()

        return document_dict
