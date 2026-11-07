"""Rule 35 Positive Testing: Proves all 8 reference solutions score 100% (1.0)."""

from pathlib import Path
import pytest
from core.config import config
from graders import get_grader

@pytest.mark.parametrize("task_id, ref_file", [
    ("task_01_sycl_usm_barrier", "solve_task_01.py"),
    ("task_02_xmx_2d_block_pitch", "solve_task_02.py"),
    ("task_03_ipex_int4_dequant_stride", "solve_task_03.py"),
    ("task_04_paged_attention_strides", "solve_task_04.py"),
    ("task_05_ooo_queue_cross_sync", "solve_task_05.py"),
    ("task_06_openvino_npu_subgraph", "solve_task_06.py"),
    ("task_07_speculative_token_mask", "solve_task_07.py"),
    ("task_08_slm_bank_conflict_pad", "solve_task_08.py"),
])
def test_all_reference_solutions_pass(task_id: str, ref_file: str):
    """Verifies that human reference solutions achieve 1.0 on every task grader."""
    solution_path = config.reference_dir / ref_file
    assert solution_path.exists(), f"Reference file {ref_file} not found"
    
    code = solution_path.read_text(encoding="utf-8")
    grader = get_grader(task_id)
    score, metadata = grader.grade(code)

    assert score == 1.0, f"Task {task_id} reference solution failed: {metadata}"
    assert metadata.get("passed_invariants") is True
