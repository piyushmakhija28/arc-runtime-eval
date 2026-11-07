"""Adversarial mutation and security checks to guarantee 0 false passes."""

import pytest
from graders import get_grader

def test_adversarial_c_plus_plus_stream_hallucination():
    """Adversarial injection: Valid C++ syntax but missing SYCL event dependencies."""
    adversarial_payload = """```cpp
#include <sycl/sycl.hpp>
void submit_workload(sycl::queue& q, const float* h, float* d, size_t n) {
    // Looks convincingly modern, but omits depends_on
    auto ev = q.memcpy(d, h, n * sizeof(float));
    q.submit([&](sycl::handler& cgh) {
        cgh.parallel_for(sycl::range<1>(n), [=](sycl::id<1> i) { d[i] += 1.0f; });
    });
}
```"""
    grader = get_grader("task_01_sycl_usm_barrier")
    score, metadata = grader.grade(adversarial_payload)
    assert score == 0.0
    assert metadata["passed_invariants"] is False

def test_adversarial_xmx_half_pitch():
    """Adversarial: Off-by-one in alignment arithmetic."""
    adversarial_code = """```python
def calculate_xmx_pitch(width: int, element_size_bytes: int, alignment_bytes: int = 64) -> int:
    # Intentionally flawed rounding formula
    return (width * element_size_bytes // alignment_bytes) * alignment_bytes
```"""
    grader = get_grader("task_02_xmx_2d_block_pitch")
    score, metadata = grader.grade(adversarial_code)
    assert score == 0.0

def test_adversarial_int4_signed_overflow():
    """Adversarial: Omits -8 zero-point offset in INT4 dequantization."""
    adversarial_code = """```python
import numpy as np
def dequantize_int4_symmetric(packed_weights: np.ndarray, scales: np.ndarray) -> np.ndarray:
    out = np.empty(len(packed_weights) * 2, dtype=np.float32)
    for i, b in enumerate(packed_weights):
        # Forgot to subtract zero-point 8
        out[i * 2] = float(b & 0x0F) * float(scales[i * 2])
        out[i * 2 + 1] = float((b >> 4) & 0x0F) * float(scales[i * 2 + 1])
    return out
```"""
    grader = get_grader("task_03_ipex_int4_dequant_stride")
    score, metadata = grader.grade(adversarial_code)
    assert score == 0.0
