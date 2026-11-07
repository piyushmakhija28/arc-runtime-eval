"""Configuration settings and environment bindings for the evaluation framework."""

from dataclasses import dataclass
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class EvalConfig:
    """Immutable global settings for the evaluation harness."""
    base_dir: Path = Path(__file__).resolve().parent.parent
    tasks_dir: Path = base_dir / "tasks"
    reference_dir: Path = base_dir / "reference"
    results_dir: Path = base_dir / "results"
    transcripts_dir: Path = base_dir / "transcripts"
    logs_dir: Path = base_dir / "logs"
    default_trials_per_task: int = int(os.getenv("DEFAULT_TRIALS_PER_TASK", "3"))
    default_temperature: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.0"))
    timeout_seconds: float = float(os.getenv("TIMEOUT_SECONDS", "30.0"))
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

config = EvalConfig()
