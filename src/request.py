from pathlib import Path

from openai import APIConnectionError, OpenAI

from src.config_model import Config


class LLM_API:
    def __init__(self, config: Config, model="") -> None:
        self.config = config
        self.base_url = self.config.llm_service.api.base_url

        if not self.config.llm_service.api.key_value:
            key_location = str(self.config.llm_service.api.key_location)

            path = Path(key_location).expanduser()
            with path.open("r", encoding="utf-8") as f:
                self.llm_key = f.read().strip()
        else:
            self.llm_key = self.config.llm_service.api.key_value

        if not model:
            self.model = self.config.git.commit.llm_model
        else:
            self.model = model


    def call(self, rule, prompt):
        client = OpenAI(
            base_url=self.base_url,
            api_key=self.llm_key,
            timeout=self.config.git.commit.api_auto_abort_duration_seconds
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
