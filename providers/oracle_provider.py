"""Oracle reference provider returning verified ground-truth solutions."""

from pathlib import Path
from core.config import config
from providers.base import ModelProvider

class OracleProvider(ModelProvider):
    """Provides ground-truth solutions for verification and grader calibration."""

    def __init__(self) -> None:
        super().__init__("oracle", "oracle-ground-truth")

    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """Extracts task reference solution based on prompt context."""
        for task_file in config.tasks_dir.glob("*.json"):
            import json
            data = json.loads(task_file.read_text(encoding="utf-8"))
            if data["prompt"].strip() == prompt.strip():
                task_id = data["id"]
                ref_num = task_id.split("_")[1]
                ref_file = config.reference_dir / f"solve_task_{ref_num}.py"
                if ref_file.exists():
                    return ref_file.read_text(encoding="utf-8")
        return ""
