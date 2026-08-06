
from dataclasses import dataclass
import re
from time import sleep
from typing import Generator


@dataclass
class Text:
    content: str

@dataclass
class Code:
    content: str
    language: str
    reverence_tag: str

@dataclass
class Think:
    content: str


def line_assembler(chunks: Generator[str]):
    buffer = ""

    for chunk in chunks:
        buffer += chunk

        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            yield line + "\n"

    if buffer:
        yield buffer

def parser(stream: Generator[str]):
    in_code = False
    in_think_tag = False
    think_text: list[str] = []
    code_language = ""
    reference_tag = ""
    code: list[str] = []

    for line in stream:
        open_tag = re.findall(r'\<mm:think\>.*', line)
        if len(open_tag) > 0:
            in_think_tag = True

        close_tag = re.findall(r'.*(?:\</mm:think\>)', line)
        if in_think_tag:
            if len(close_tag) > 0:
                yield Think(close_tag[0])
            else:
                yield Think(line)

        if in_think_tag and len(close_tag) > 0:
            after_closed_tag = re.findall(r'(?<=\</mm:think\>).*', line)
            if len(after_closed_tag) > 0:
                yield Text(after_closed_tag[0])

            in_think_tag = False
            think_text.clear()

            continue

        if not in_think_tag and line.startswith("```"):
            if not in_code:
                # Opening fence
                match_lang = re.findall(r'(?<=```)\w+', line)
                if len(match_lang) > 0:
                    code_language = match_lang[0]

                in_code = True
                code.clear()
            else:
                # Closing fence
                in_code = False
                yield Code("".join(code), code_language, reference_tag)

                code_language = ""
                reference_tag = ""
            continue

        if in_code:
            code.append(line)
        else:
            if not in_think_tag:
                yield Text(line)

        match_ref = re.findall(r'\{\{TAG_UML_\w+\}\}', line)
        if len(match_ref) > 0:
            reference_tag = match_ref[0]


def event_consumer(stream: Generator[Think | Text | Code], think_file, text_result_file):
    for line in stream:
        sleep(0.05)
        if type(line) == Think:
            think_file.write(line.content)
            think_file.flush()
        if type(line) == Text:
            text_result_file.write(line.content)
            text_result_file.flush()
        if type(line) == Code:
            if line.reverence_tag and line.language == "plantuml":
                file_name = line.reverence_tag.replace("{{", "").replace("}}", "")
                file_path = f".autodocs/puml/{"2026-08-05_15-46-44"}/{file_name}-new.puml"

                with open(file_path, "w") as f:
                    f.write(line.content)
