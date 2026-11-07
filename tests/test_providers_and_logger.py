"""Tests for providers, factory, and logger to maximize test coverage."""

import logging
from core.exceptions import (
    ArcEvalException,
    TaskExecutionError,
    GraderInvariantViolationError,
    ProviderRateLimitError,
    InvalidSolutionPayloadError,
)
from core.logger import get_logger, JsonLinesFormatter
from providers.factory import ProviderFactory
from providers.oracle_provider import OracleProvider
from providers.mocked_provider import MockedFrontierProvider

def test_exceptions_hierarchy():
    """Verifies that all domain exceptions derive from ArcEvalException."""
    assert issubclass(TaskExecutionError, ArcEvalException)
    assert issubclass(GraderInvariantViolationError, ArcEvalException)
    assert issubclass(ProviderRateLimitError, ArcEvalException)
    assert issubclass(InvalidSolutionPayloadError, ArcEvalException)

def test_logger_initialization():
    """Verifies logger initializes properly and writes JSON formatted records."""
    logger = get_logger("TestLogger")
    assert logger.name == "TestLogger"
    formatter = JsonLinesFormatter()
    record = logging.LogRecord(
        name="Test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None
    )
    formatted = formatter.format(record)
    assert '"message": "Test message"' in formatted

def test_provider_factory():
    """Verifies ProviderFactory creates oracle and mocked providers."""
    oracle = ProviderFactory.get_provider("oracle")
    assert isinstance(oracle, OracleProvider)

    mocked = ProviderFactory.get_provider("mocked", "gpt-4o")
    assert isinstance(mocked, MockedFrontierProvider)

def test_oracle_generate_response():
    """Verifies oracle provider successfully returns reference solution for known prompt."""
    from core.models import TaskDefinition
    import json
    from core.config import config

    task_file = list(config.tasks_dir.glob("*.json"))[0]
    data = json.loads(task_file.read_text(encoding="utf-8"))
    prompt = data["prompt"]

    oracle = OracleProvider()
    resp = oracle.generate(prompt)
    assert len(resp) > 0
    assert "def " in resp or "void " in resp or "#include" in resp

def test_mocked_generate_response():
    """Verifies mocked provider successfully returns failure traces for known prompt."""
    import json
    from core.config import config

    task_file = list(config.tasks_dir.glob("*.json"))[0]
    data = json.loads(task_file.read_text(encoding="utf-8"))
    prompt = data["prompt"]

    mocked = MockedFrontierProvider("gpt-4o")
    resp = mocked.generate(prompt)
    assert len(resp) > 0
