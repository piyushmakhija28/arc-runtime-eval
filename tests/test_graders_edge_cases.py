"""Rule 37 Edge-Case Testing: Verifies boundary conditions and malformed inputs."""

import pytest
from graders import get_grader

def test_empty_string_input():
    """Empty or whitespace input must score 0.0 without uncaught exceptions."""
    grader = get_grader("task_02_xmx_2d_block_pitch")
    score, metadata = grader.grade("")
    assert score == 0.0
    assert metadata["passed_invariants"] is False

def test_syntax_error_python_payload():
    """Python syntax error should gracefully score 0.0."""
    bad_syntax = "```python\ndef calculate_xmx_pitch(:\n  return\n```"
    grader = get_grader("task_02_xmx_2d_block_pitch")
    score, metadata = grader.grade(bad_syntax)
    assert score == 0.0
    assert "error" in metadata

def test_speculative_decoding_all_zeros():
    """Edge condition where all probabilities are below threshold."""
    code = """```python
import numpy as np
def compute_acceptance_mask(target_probs: np.ndarray, thresholds: np.ndarray) -> np.ndarray:
    return np.cumprod((target_probs >= thresholds).astype(np.int32), dtype=np.int32)
```"""
    grader = get_grader("task_07_speculative_token_mask")
    score, metadata = grader.grade(code)
    assert score == 1.0

def test_slm_coprime_edge_case():
    """Edge condition where width is already coprime with bank count (e.g. 15 and 16)."""
    grader = get_grader("task_08_slm_bank_conflict_pad")
    # Correct solution does not add padding when already coprime
    ref_code = """```python
import math
def calculate_padded_slm_stride(tile_width: int, bank_count: int = 16) -> int:
    return tile_width + 1 if math.gcd(tile_width, bank_count) > 1 else tile_width
```"""
    score, metadata = grader.grade(ref_code)
    assert score == 1.0
