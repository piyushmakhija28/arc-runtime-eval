"""Abstract base class for all LLM providers."""

from abc import ABC, abstractmethod

class ModelProvider(ABC):
    """Abstract interface for querying language models."""

    def __init__(self, name: str, model_id: str) -> None:
        """Initializes model provider.

        Args:
            name: Provider moniker, e.g. 'openai'.
            model_id: Target model identifier.
        """
        self.name = name
        self.model_id = model_id

    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """Generates completion for a given prompt.

        Args:
            prompt: Text prompt input.
            temperature: Sampling temperature.

        Returns:
            str: Generated text response.
        """
        pass
