"""Abstract base class for deterministic evaluation graders."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

class TaskGrader(ABC):
    """Abstract contract for task scorers."""

    def __init__(self, task_id: str) -> None:
        """Initializes grader with target task id.

        Args:
            task_id: Unique task identifier.
        """
        self.task_id = task_id

    @abstractmethod
    def grade(self, output: str) -> Tuple[float, Dict[str, Any]]:
        """Scores candidate model output against task invariants.

        Args:
            output: Raw text output from model under test.

        Returns:
            Tuple[float, Dict[str, Any]]: Numerical score [0.0, 1.0] and grading metadata.
        """
        pass
