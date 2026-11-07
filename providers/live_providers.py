"""Live API clients for OpenAI, Anthropic, and Gemini models."""

import os
from typing import Optional
import httpx
from core.exceptions import ProviderRateLimitError, TaskExecutionError
from providers.base import ModelProvider

class LiveOpenAIProvider(ModelProvider):
    """Executes calls against OpenAI API."""

    def __init__(self, model_id: str = "gpt-4o", api_key: Optional[str] = None) -> None:
        super().__init__("openai", model_id)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")

    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        if not self.api_key:
            raise TaskExecutionError("OPENAI_API_KEY is not set.")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code == 429:
                    raise ProviderRateLimitError("OpenAI Rate Limit Exceeded")
                res.raise_for_status()
                return res.json()["choices"][0]["message"]["content"]
        except ProviderRateLimitError:
            raise
        except Exception as e:
            raise TaskExecutionError(f"OpenAI call failed: {e}") from e

class LiveAnthropicProvider(ModelProvider):
    """Executes calls against Anthropic API."""

    def __init__(self, model_id: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None) -> None:
        super().__init__("anthropic", model_id)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")

    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        if not self.api_key:
            raise TaskExecutionError("ANTHROPIC_API_KEY is not set.")
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_id,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code == 429:
                    raise ProviderRateLimitError("Anthropic Rate Limit Exceeded")
                res.raise_for_status()
                return res.json()["content"][0]["text"]
        except ProviderRateLimitError:
            raise
        except Exception as e:
            raise TaskExecutionError(f"Anthropic call failed: {e}") from e

class LiveGeminiProvider(ModelProvider):
    """Executes calls against Google Gemini API."""

    def __init__(self, model_id: str = "gemini-1.5-pro", api_key: Optional[str] = None) -> None:
        super().__init__("gemini", model_id)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")

    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        if not self.api_key:
            raise TaskExecutionError("GEMINI_API_KEY is not set.")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature}
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code == 429:
                    raise ProviderRateLimitError("Gemini Rate Limit Exceeded")
                res.raise_for_status()
                return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        except ProviderRateLimitError:
            raise
        except Exception as e:
            raise TaskExecutionError(f"Gemini call failed: {e}") from e
