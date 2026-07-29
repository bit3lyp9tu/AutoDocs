from pydantic import BaseModel


class Tag(BaseModel):
    type: str
    name: str

class Block(BaseModel):
    tag: Tag
    language: str
    content: str

class Document(BaseModel):
    blocks: list[Block]
