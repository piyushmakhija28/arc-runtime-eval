"""Evaluation harness runner: executes benchmark tasks across models and reports metrics."""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List
from tabulate import tabulate

from core.config import config
from core.logger import get_logger
from core.models import (
    ConfidenceInterval,
    OverallModelBenchmark,
    TaskDefinition,
    TaskSummaryMetrics,
    TrialResult,
)
from graders import get_grader
from providers.factory import ProviderFactory

logger = get_logger("HarnessRunner")

class BenchmarkHarness:
    """Orchestrates benchmark task execution, grading, and statistical aggregation."""

    def __init__(self) -> None:
        """Initializes benchmark harness and ensures directories exist."""
        config.results_dir.mkdir(parents=True, exist_ok=True)
        config.transcripts_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def load_tasks() -> List[TaskDefinition]:
        """Loads and parses all task definitions from the tasks directory.

        Returns:
            List[TaskDefinition]: Sorted list of benchmark tasks.
        """
        tasks = []
        for p in sorted(config.tasks_dir.glob("*.json")):
            data = json.loads(p.read_text(encoding="utf-8"))
            tasks.append(TaskDefinition(**data))
        return tasks

    def evaluate_model(
        self,
        provider_type: str,
        model_id: str,
        trials_per_task: int = 3,
        temperature: float = 0.0
    ) -> OverallModelBenchmark:
        """Runs the full evaluation benchmark across all tasks for a designated model provider.

        Args:
            provider_type: Moniker of provider ('oracle', 'mocked', 'openai', etc.).
            model_id: Target model name or path.
            trials_per_task: Number of trials per task for variance calculation.
            temperature: Sampling temperature for inference.

        Returns:
            OverallModelBenchmark: Aggregated performance metrics, Pass@1, Pass^k, and Wilson CIs.
        """
        provider = ProviderFactory.get_provider(provider_type, model_id)
        tasks = self.load_tasks()
        all_task_metrics: List[TaskSummaryMetrics] = []
        total_trials = 0
        all_tasks_consistent_successes = 0

        sanitized_model_id = Path(model_id).name if "/" in model_id or "\\" in model_id else model_id
        transcripts_dir = config.transcripts_dir / sanitized_model_id
        transcripts_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting benchmark run for model: {model_id} (Provider: {provider_type})")

        for task in tasks:
            grader = get_grader(task.id)
            trial_scores: List[float] = []
            trial_latencies: List[float] = []
            task_transcripts: List[Dict] = []

            for trial_idx in range(trials_per_task):
                start_t = time.perf_counter()
                error_msg = None
                try:
                    output = provider.generate(task.prompt, temperature=temperature)
                except Exception as e:
                    output = ""
                    error_msg = str(e)
                    logger.error(f"Error on {task.id} trial {trial_idx}: {e}")

                latency_ms = (time.perf_counter() - start_t) * 1000.0
                trial_latencies.append(latency_ms)

                score, metadata = grader.grade(output)
                trial_scores.append(score)

                task_transcripts.append({
                    "trial": trial_idx + 1,
                    "prompt": task.prompt,
                    "output": output,
                    "score": score,
                    "metadata": metadata,
                    "latency_ms": round(latency_ms, 2),
                    "error": error_msg
                })

                total_trials += 1

            (transcripts_dir / f"{task.id}_transcripts.json").write_text(
                json.dumps(task_transcripts, indent=2), encoding="utf-8"
            )

            task_success_count = sum(1 for s in trial_scores if s >= 1.0)
            pass_at_1 = task_success_count / trials_per_task
            pass_pow_k = 1.0 if task_success_count == trials_per_task else 0.0
            if pass_pow_k == 1.0:
                all_tasks_consistent_successes += 1

            wilson_ci = ConfidenceInterval.calculate_wilson_interval(task_success_count, trials_per_task)

            task_metric = TaskSummaryMetrics(
                task_id=task.id,
                model_id=model_id,
                trials_count=trials_per_task,
                pass_at_1=round(pass_at_1, 4),
                pass_pow_k=round(pass_pow_k, 4),
                wilson_ci=wilson_ci,
                mean_latency_ms=round(sum(trial_latencies) / len(trial_latencies), 2)
            )
            all_task_metrics.append(task_metric)
            logger.info(f"Task {task.id}: Pass@1={pass_at_1*100:.1f}%, Pass^k={pass_pow_k*100:.1f}%, CI=[{wilson_ci.lower_bound}, {wilson_ci.upper_bound}]")

        tasks_solved = sum(1 for tm in all_task_metrics if tm.pass_at_1 >= 1.0)
        overall_pass_rate = round(tasks_solved / len(tasks), 4)
        overall_consistency = 1.0 if all_tasks_consistent_successes == len(tasks) else 0.0
        overall_ci = ConfidenceInterval.calculate_wilson_interval(tasks_solved, len(tasks))

        benchmark = OverallModelBenchmark(
            model_id=model_id,
            total_tasks=len(tasks),
            total_trials=total_trials,
            overall_pass_rate=overall_pass_rate,
            consistency_pass_pow_k=overall_consistency,
            overall_wilson_ci=overall_ci,
            approximate_cost_usd=0.01 if provider_type != "oracle" else 0.0,
            task_metrics=all_task_metrics
        )

        result_file = config.results_dir / f"benchmark_{sanitized_model_id}.json"
        result_file.write_text(benchmark.model_dump_json(indent=2), encoding="utf-8")
        return benchmark

    @staticmethod
    def format_table(benchmarks: List[OverallModelBenchmark]) -> str:
        """Formats benchmark results as a GitHub Markdown table.

        Args:
            benchmarks: List of completed model benchmarks.

        Returns:
            str: Formatted markdown table string.
        """
        table_data = []
        for b in benchmarks:
            ci_str = f"[{b.overall_wilson_ci.lower_bound*100:.1f}%, {b.overall_wilson_ci.upper_bound*100:.1f}%]"
            table_data.append([
                b.model_id,
                b.total_tasks,
                b.total_trials,
                f"{b.overall_pass_rate*100:.1f}%",
                f"{b.consistency_pass_pow_k*100:.1f}%",
                ci_str,
                f"${b.approximate_cost_usd:.2f}"
            ])
        headers = ["Model", "Tasks", "Trials", "Pass@1", "Pass^k", "95% Wilson CI", "Est. Cost"]
        return tabulate(table_data, headers=headers, tablefmt="github")

def load_tasks() -> List[TaskDefinition]:
    """Loads all task definitions from the tasks directory."""
    return BenchmarkHarness.load_tasks()

def run_evaluation(
    provider_type: str,
    model_id: str,
    trials_per_task: int = 3,
    temperature: float = 0.0
) -> OverallModelBenchmark:
    """Runs full benchmark suite across all tasks for a designated provider."""
    harness = BenchmarkHarness()
    return harness.evaluate_model(provider_type, model_id, trials_per_task, temperature)

def display_summary_table(benchmarks: List[OverallModelBenchmark]) -> None:
    """Prints clean markdown-style table of benchmark results."""
    print("\n" + BenchmarkHarness.format_table(benchmarks) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run arc-runtime-eval benchmark harness.")
    parser.add_argument("--provider", default="oracle", choices=["oracle", "mocked", "openai", "anthropic", "gemini", "local_openvino"], help="Model provider category")
    parser.add_argument("--model", default="oracle-reference", help="Target model identifier")
    parser.add_argument("--mode", choices=["replay", "oracle", "live"], default=None, help="Convenience mode selector ('replay' sets provider=mocked)")
    parser.add_argument("--trials", type=int, default=3, help="Number of trials per task")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature")
    args = parser.parse_args()

    provider = args.provider
    model = args.model
    if args.mode == "replay":
        provider = "mocked"
        if model == "oracle-reference":
            model = "gpt-4o"
    elif args.mode == "oracle":
        provider = "oracle"
        model = "oracle-reference"

    bench = run_evaluation(provider, model, args.trials, args.temperature)
    display_summary_table([bench])
