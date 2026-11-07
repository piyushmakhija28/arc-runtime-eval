"""Local OpenVINO / Intel Arc GPU model provider using real local weights."""

import time
from typing import Optional
from providers.base import ModelProvider

class LocalOpenVINOProvider(ModelProvider):
    """Executes live local inference using Intel Arc GPU / CPU via OpenVINO GenAI."""

    def __init__(self, model_path: str, device: str = "GPU") -> None:
        model_name = model_path.replace("\\", "/").rstrip("/").split("/")[-1]
        super().__init__("local_openvino", f"local-{model_name}-{device.lower()}")
        self.model_path = model_path
        self.device = device
        self._pipeline = None

    def _get_pipeline(self):
        if self._pipeline is None:
            import openvino_genai as og
            try:
                self._pipeline = og.LLMPipeline(self.model_path, self.device)
            except Exception:
                # Fallback to CPU if GPU initialization encounters driver limits
                self._pipeline = og.LLMPipeline(self.model_path, "CPU")
        return self._pipeline

    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        pipeline = self._get_pipeline()
        import openvino_genai as og
        config = og.GenerationConfig()
        config.max_new_tokens = 512
        config.temperature = max(temperature, 0.01) if temperature > 0 else 0.0
        return pipeline.generate(prompt, config)
