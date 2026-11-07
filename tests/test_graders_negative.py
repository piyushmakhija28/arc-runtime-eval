"""Rule 36 Negative Testing: Proves flawed and hallucinated LLM outputs score 0.0."""

import pytest
from graders import get_grader
from providers.mocked_provider import FLAWED_TRACES

@pytest.mark.parametrize("task_id", [
    "task_01_sycl_usm_barrier",
    "task_02_xmx_2d_block_pitch",
    "task_03_ipex_int4_dequant_stride",
    "task_04_paged_attention_strides",
    "task_05_ooo_queue_cross_sync",
    "task_06_openvino_npu_subgraph",
    "task_07_speculative_token_mask",
    "task_08_slm_bank_conflict_pad",
])
def test_mocked_llm_failures_score_zero(task_id: str):
    """Verifies that typical frontier LLM failure patterns cleanly score 0.0 (no false passes)."""
    flawed_code = FLAWED_TRACES[task_id]
    grader = get_grader(task_id)
    score, metadata = grader.grade(flawed_code)

    assert score == 0.0, f"Task {task_id} allowed flawed output to pass with score {score}!"
    assert metadata.get("passed_invariants") is False
