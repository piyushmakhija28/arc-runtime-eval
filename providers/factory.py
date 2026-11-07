"""Factory pattern for instantiating model providers."""

from typing import Optional
from providers.base import ModelProvider
from providers.oracle_provider import OracleProvider
from providers.mocked_provider import MockedFrontierProvider
from providers.live_providers import LiveOpenAIProvider, LiveAnthropicProvider, LiveGeminiProvider
from providers.local_openvino_provider import LocalOpenVINOProvider

class ProviderFactory:
    """Instantiates model provider based on provider type and model name."""

    @staticmethod
    def get_provider(provider_type: str, model_id: Optional[str] = None) -> ModelProvider:
        """Creates a ModelProvider instance.

        Args:
            provider_type: Provider category: 'oracle', 'mocked', 'openai', 'anthropic', 'gemini', 'local_openvino'.
            model_id: Specific model name identifier or path.

        Returns:
            ModelProvider: Concrete provider instance.
        """
        p_type = provider_type.lower()
        if p_type == "oracle":
            return OracleProvider()
        elif p_type == "local_openvino":
            default_path = "C:/Users/techd/Documents/workspace-spring-tool-suite-4-4.27.0-new/intel-arc-models-runner/models/qwen-2.5-1.5b"
            return LocalOpenVINOProvider(model_id or default_path)
        elif p_type == "mocked":
            return MockedFrontierProvider(model_id or "gpt-4o")
        elif p_type == "openai":
            return LiveOpenAIProvider(model_id or "gpt-4o")
        elif p_type == "anthropic":
            return LiveAnthropicProvider(model_id or "claude-3-5-sonnet-20241022")
        elif p_type == "gemini":
            return LiveGeminiProvider(model_id or "gemini-1.5-pro")
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
