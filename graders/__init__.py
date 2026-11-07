"""Grading registry and factory for evaluation scorers."""

from typing import Dict
from graders.base_grader import TaskGrader
from graders.task_graders import (
    SyclUsmBarrierGrader,
    Xmx2DBlockPitchGrader,
    IpexInt4DequantGrader,
    PagedAttentionStrideGrader,
    OutOfOrderQueueSyncGrader,
    OpenVinoNpuSubgraphGrader,
    SpeculativeTokenMaskGrader,
    SlmBankConflictPadGrader,
)

GRADERS_REGISTRY: Dict[str, TaskGrader] = {
    "task_01_sycl_usm_barrier": SyclUsmBarrierGrader(),
    "task_02_xmx_2d_block_pitch": Xmx2DBlockPitchGrader(),
    "task_03_ipex_int4_dequant_stride": IpexInt4DequantGrader(),
    "task_04_paged_attention_strides": PagedAttentionStrideGrader(),
    "task_05_ooo_queue_cross_sync": OutOfOrderQueueSyncGrader(),
    "task_06_openvino_npu_subgraph": OpenVinoNpuSubgraphGrader(),
    "task_07_speculative_token_mask": SpeculativeTokenMaskGrader(),
    "task_08_slm_bank_conflict_pad": SlmBankConflictPadGrader(),
}

def get_grader(task_id: str) -> TaskGrader:
    """Retrieves the registered grader instance for a task id.

    Args:
        task_id: Unique task identifier.

    Returns:
        TaskGrader: Instantiated task scorer.

    Raises:
        KeyError: If task_id is not registered.
    """
    if task_id not in GRADERS_REGISTRY:
        raise KeyError(f"No grader registered for task_id: {task_id}")
    return GRADERS_REGISTRY[task_id]
