import json
from pathlib import Path

from openai import APIConnectionError, OpenAI, PermissionDeniedError
from pydantic import ValidationError
import requests

from src.config_model import Config
from src.state_schemas import Model, ScadsAIModelsStatus


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


    def request(self, rule, prompt):
        client = OpenAI(
            base_url=self.base_url,
            api_key=self.llm_key,
            timeout=self.config.git.commit.timeout
        )

        success, status, time_taken = self.check_model_status(model=self.model)
        if success:
            print(f"{self.model} [{status}] ({time_taken}s)")

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
            except PermissionDeniedError as p:
                print(p)
                return ""
        else:
            print("Connection to API failed")
            return ""


    def request_stream(self, rule, prompt):
        client = OpenAI(
            base_url=self.base_url,
            api_key=self.llm_key,
            timeout=self.config.git.commit.timeout,
            max_retries=5
        )

        success, status, time_taken = self.check_model_status(model=self.model)
        if success:
            print(f"{self.model} [{status}] ({time_taken}s)")

            with client.responses.stream(
                model=self.model,
                instructions=rule,
                input=prompt,
            ) as stream:
                for event in stream:
                    if event.type == "response.output_text.delta":
                        yield event.delta

                response = stream.get_final_response()
        else:
            print("Connection to API failed")
            return ""


    def check_model_status(self, model, hasPermission=True) -> tuple[bool, str, float]:
        if not self.config.llm_service.status.pre_check_connection or not hasPermission:
            return (False, "", 0)

        try:
            response = requests.get(self.config.llm_service.status.url).json()
        except requests.exceptions.RequestException as e:
            print(f"Connection to LLM status page failed: {e}")
            return (False, "", 0)

        try:
            data = ScadsAIModelsStatus.model_validate(response)
        except ValidationError as e:
            print(e.errors())
            return (False, "", 0)

        if self.config.llm_service.status.type in data.models.keys():
            for i in data.models[self.config.llm_service.status.type]:
                if i.real_name==model:
                    return (
                        True,
                        i.state,
                        i.time_taken
                    )
            else:
                raise ValueError("Model not in list")
        else:
            raise ValueError("LLM type is not in list")


