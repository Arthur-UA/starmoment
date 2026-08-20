from typing import List, Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

class LLM:
    def __init__(self, model_name: str, provider: str = "openai"):
        self.model_name = model_name
        self.provider = provider

    def _ask_openai(self, messages: List[Dict]):
        stream = OpenAI().responses.create(
            model=self.model_name,
            input=messages,
            stream=True,
        )
        for event in stream:
            if event.type == "response.output_text.delta":
                yield event.delta
            elif event.type == "response.completed":
                break

    def _ask_vLLM(self, messages: List[Dict]):
        BASE_URL = "http://localhost:8000/v1"
        API_KEY = "EMPTY"

        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        stream = client.responses.create(
            model=self.model_name,
            input=messages,
            stream=True,
        )

        for event in stream:
            if event.type == "response.output_text.delta":
                yield event.delta
            elif event.type == "response.completed":
                break

    def generate(self, messages: List[Dict]):
        providers = {
            "openai": self._ask_openai,
            "vLLM": self._ask_vLLM
        }

        if self.provider not in providers:
            raise ValueError(f"Unsupported provider: {self.provider}")

        yield from providers[self.provider](messages)
