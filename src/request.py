from pathlib import Path

from openai import APIConnectionError, OpenAI

from src.config_model import Config


class LLM_API:
    def __init__(self, config: Config, llm_key_path="~/.llm_key", model="meta-llama/Llama-3.3-70B-Instruct") -> None:
        self.base_url = config.llm_service.api.base_url

        if not config.llm_service.api.key_value:
            path = Path(llm_key_path).expanduser()
            with path.open("r", encoding="utf-8") as f:
                self.llm_key = f.read().strip()
        else:
            self.llm_key = config.llm_service.api.key_value

        self.model = model

    def call(self, rule, prompt):
        client = OpenAI(
            base_url=self.base_url,
            api_key=self.llm_key,
        )

        try:
            response = client.responses.create(
                model=self.model,
                instructions=rule,
                input=prompt,
            )
            return response.output_text

        except APIConnectionError as e:
            print(e)
            return ""
