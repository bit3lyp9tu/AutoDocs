import json
from pathlib import Path

from openai import APIConnectionError, OpenAI, PermissionDeniedError
from pydantic import ValidationError
import requests

from src.schemas.config_model import Config
from src.schemas.state_schemas import Model, ScadsAIModelsStatus


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
                    timeout=200,
                    temperature=1
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
            timeout=120,#self.config.git.commit.timeout,
            max_retries=5
        )

        success, status, time_taken = self.check_model_status(model=self.model)
        if success:
            print(f"{self.model} [{status}] ({time_taken}s)")

            responses = client.responses
            stream = responses.create(
                model=self.model,
                instructions=rule,
                input=prompt,
                stream=True
            )
            for event in stream:
                match event.type:
                    case "response.output_text.delta":
                        yield event.delta

                    case "response.output_text.done":
                        print("\nText complete")

                    case "response.completed":
                        response = event.response
                        max_tokens = response.max_output_tokens
                        if max_tokens:
                            print(f"\nMax_Tokens: {max_tokens}")

                        temp = response.temperature
                        if max_tokens:
                            print(f"Temperature: {temp}")

                        usage = response.usage
                        if usage:
                            print(f"Input_Tokens:  {usage.input_tokens}")
                            print(f"Output_Tokens: {usage.output_tokens}")
                            print(f"Total_Tokens: {usage.total_tokens}")
                            print("\n")

                    case "response.error":
                        print(event.error)

                    case _:
                        pass

            return ""
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
                        i.state.lower()=="up",
                        i.state,
                        i.time_taken
                    )
            else:
                raise ValueError("Model not in list")
        else:
            raise ValueError("LLM type is not in list")


