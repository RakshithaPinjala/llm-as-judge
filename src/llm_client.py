import os
from abc import ABC, abstractmethod
from typing import Type, TypeVar
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

T = TypeVar("T", bound=BaseModel)

class LLMClient(ABC):
    @abstractmethod
    def generate_structured(self, prompt: str, schema: Type[T]) -> tuple[T, int]:
        """Generate structured output based on a Pydantic schema. Returns (parsed_output, tokens_used)"""
        pass

class OpenAIClient(LLMClient):
    def __init__(self, model_name: str = "gpt-4o"):
        from openai import OpenAI
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model_name = model_name

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_structured(self, prompt: str, schema: Type[T]) -> tuple[T, int]:
        response = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format=schema,
            temperature=0.0
        )
        msg = response.choices[0].message
        tokens = response.usage.total_tokens if response.usage else 0
        if msg.parsed:
            return msg.parsed, tokens
        else:
            raise ValueError(f"Refusal or unparseable: {msg.refusal}")

class GeminiClient(LLMClient):
    def __init__(self, model_name: str = "gemini-2.5-pro"):
        from google import genai
        from google.genai import types
        
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model_name = model_name

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_structured(self, prompt: str, schema: Type[T]) -> tuple[T, int]:
        from google.genai import types
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.0,
            ),
        )
        parsed = schema.model_validate_json(response.text)
        tokens = response.usage_metadata.total_token_count if response.usage_metadata else 0
        return parsed, tokens

def get_client(provider: str, model_name: str) -> LLMClient:
    if provider.lower() == "openai":
        return OpenAIClient(model_name)
    elif provider.lower() == "gemini":
        return GeminiClient(model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
