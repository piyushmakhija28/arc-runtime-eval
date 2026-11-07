"""Domain exception taxonomy for the evaluation harness and verifiers."""

class ArcEvalException(Exception):
    """Base exception for all domain-specific evaluation errors."""
    pass

class TaskExecutionError(ArcEvalException):
    """Raised when an external model call or sandbox process execution fails."""
    pass

class GraderInvariantViolationError(ArcEvalException):
    """Raised when an internal assertion in grading logic is violated."""
    pass

class ProviderRateLimitError(ArcEvalException):
    """Raised when an upstream LLM API rate limit or quota is exceeded."""
    pass

class InvalidSolutionPayloadError(ArcEvalException):
    """Raised when a model response contains unparseable syntax or missing code blocks."""
    pass
