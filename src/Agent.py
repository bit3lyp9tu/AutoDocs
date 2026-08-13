from dataclasses import dataclass
from time import sleep

from lark import GrammarError, Lark, UnexpectedCharacters, UnexpectedToken
from openai import BadRequestError

from src.llm_processing_pipeline import Text, line_assembler, parser_tag, tag_extraction
from src.request import LLM_API
from src.schemas.config_model import ConfigSchema


@dataclass
class Roles:
    name: str
    content: str

@dataclass
class Application(Roles):
    pass

@dataclass
class LLM(Roles):
    pass

class Agent:
    def __init__(self, config: ConfigSchema, rule, model="MiniMaxAI/MiniMax-M3-MXFP8") -> None:
        self.config = config
        self.rule = rule
        self.api = LLM_API(config, model=model)

        self.conversation: list[Roles] = []
        self.conversation_summarized: str = ""


    def run(self, code, tag="", keep_message_depth = 10):
        successful_answer = ""
        successful_result = ""
        retry_counter = 0

        # System instructions --> master prompt
        # Conversation summary --> run other model to constantly summarize the conversation
        # Last 10 messages --> record messages
        # Relevant retrieved messages
        # Current user message

        rule_prefix=""""
            You are an agent.
        """

        error_msg = ""
        while not successful_result:
            conversation = self.conversation_summarized if self.conversation_summarized else self.getConversation()

                # SUMMARY OF CONVERSATION: \n{conversation_summary}\n\n
            full_input = f"""
                GIVEN CODE: \n{code}\n
                CONTEXT: \n{conversation}\n
            """

            with open(f"tests/results/ast_generator/input_prompt_{tag}.md", "w") as f:
                f.writelines(full_input)

            response = None
            try:
                response = self.api.request_stream(
                    rule=rule_prefix+"\n"+self.rule,
                    prompt=full_input,
                    check_for_alt_models=False
                )
            except BadRequestError as e:
                error = e.body.get("error", {}) if isinstance(e.body, dict) else {}

                if (
                    error.get("code") == "context_length_exceeded"
                    or "context_length_exceeded" in str(e)
                ):
                    print("Tokenlimit exceeded. Summarize chat and retry...")
                    self.conversation_summarized = self.__conversion_summarizer()
                    continue
                else:
                    raise

            print(f"\n[{self.api.model}]: \n", end="")
            resp = []

            with open(f"tests/results/ast_generator/full_result_log_{tag}_{retry_counter}.md", "w") as f:
                for chunk in tag_extraction(self.api.model, line_assembler(response), name_tag=r'\{\{TAG_UML_\w+\}\}'):
                    f.write(chunk.content)
                    f.flush()

                    if self.api.model == "MiniMaxAI/MiniMax-M3-MXFP8":
                        if type(chunk) == Text:
                            print(chunk.content, end="", flush=True)
                            resp.append(chunk.content)
                    else:
                        print(chunk.content, end="", flush=True)
                        resp.append(chunk.content)

            self.conversation.append(
                LLM(self.api.model, ''.join(resp).split("<|close|> message ")[-1])
            )

            try:
                parser = Lark(
                    grammar=''.join(resp).split("<|close|> message ")[-1],
                    start="program",
                    parser="earley",
                    ambiguity='explicit'
                )
                tree = parser.parse(code)
                successful_answer = ''.join(resp).split("<|close|> message ")[-1]
                successful_result = tree.pretty()
            except GrammarError as e:
                error_msg = f"ERROR - GrammarError occurred: {e}"
            except UnexpectedToken as t:
                error_msg = f"ERROR - UnexpectedToken occurred: {t}"
            except UnexpectedCharacters as c :
                error_msg = f"ERROR - UnexpectedCharacters found: {c}"

            answer = successful_result if successful_result else error_msg

            self.conversation.append(
                Application("Lark parser", answer)
            )

            print(f"\n\n[Lark parser]: {answer}")

            retry_counter += 1

            if retry_counter > 10:
                break
            sleep(3)

        # with open(f"tests/results/ast_generator/conversation_log_{tag}.md") as f:
        #     f.write(self.getConversation())

        return retry_counter, successful_answer, successful_result


    def __conversion_summarizer(self, min_depth=10):
        # if len(self.conversation) * 2 >= min_depth:
            response = self.api.request_stream(
                rule="Summarize the given conversation. Is is for LLM context.",
                prompt=f"Conversation: \n{self.getConversation()}",
                check_for_alt_models=False
            )
            return ''.join(response)


    def getConversation(self):
        if self.conversation == []:
            return ""

        return ''.join([f"[{role.name}]: \n{role.content}\n\n" for role in self.conversation[:-2]])
