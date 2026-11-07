"""Deterministic replay provider injecting realistic frontier model failure traces."""

from providers.base import ModelProvider

FRONTIER_MODEL_TRACES = {
    "gpt-4o": {
        "task_01_sycl_usm_barrier": """```cpp
// GPT-4o typically emits CUDA-like stream assumptions without depends_on
#include <sycl/sycl.hpp>

void submit_workload(sycl::queue& q, const float* h_weights, float* d_weights, size_t count) {
    q.memcpy(d_weights, h_weights, count * sizeof(float));
    q.parallel_for(sycl::range<1>(count), [=](sycl::id<1> idx) {
        d_weights[idx] = d_weights[idx] * 2.0f;
    });
}
```""",
        "task_02_xmx_2d_block_pitch": """```python
def calculate_xmx_pitch(width: int, element_size_bytes: int, alignment_bytes: int = 64) -> int:
    # Standard mistake: naive row stride without cache alignment padding
    return width * element_size_bytes
```""",
        "task_03_ipex_int4_dequant_stride": """```python
import numpy as np

def dequantize_int4_symmetric(packed_weights: np.ndarray, scales: np.ndarray) -> np.ndarray:
    # Standard mistake: Big-endian high-nibble first or inverted nibble order
    total = len(packed_weights) * 2
    out = np.empty(total, dtype=np.float32)
    for i, b in enumerate(packed_weights):
        # Inverted: high nibble unpacked first
        w0 = int((b >> 4) & 0x0F)
        w1 = int(b & 0x0F)
        idx = i * 2
        out[idx] = float(w0 - 8) * float(scales[idx])
        out[idx + 1] = float(w1 - 8) * float(scales[idx + 1])
    return out
```""",
        "task_04_paged_attention_strides": """```python
def calculate_kv_offset(token_idx: int, head_idx: int, dim_idx: int, block_table: list, page_size: int, num_heads: int, head_dim: int) -> int:
    # Omits head count in page stride
    page_id = block_table[token_idx // page_size]
    slot = token_idx % page_size
    return page_id * page_size * head_dim + slot * head_dim + dim_idx
```""",
        "task_05_ooo_queue_cross_sync": """```cpp
#include <sycl/sycl.hpp>

void execute_dual_engine_pipeline(sycl::queue& copy_queue, sycl::queue& compute_queue, const float* h_src, float* d_buf, size_t count) {
    copy_queue.memcpy(d_buf, h_src, count * sizeof(float));
    copy_queue.wait(); // Anti-pattern: host blocking stalls the CPU thread
    compute_queue.parallel_for(sycl::range<1>(count), [=](sycl::id<1> i) {
        d_buf[i] *= 3.14159f;
    });
}
```""",
        "task_06_openvino_npu_subgraph": """```python
def validate_npu_compatibility(subgraph_spec: dict) -> bool:
    # Ignores dynamic rank check, allowing invalid runtime fallback
    return True
```""",
        "task_07_speculative_token_mask": """```python
import numpy as np

def compute_acceptance_mask(target_probs: np.ndarray, thresholds: np.ndarray) -> np.ndarray:
    # Standard failure: evaluates tokens independently without stopping at first rejection
    return (target_probs >= thresholds).astype(np.int32)
```""",
        "task_08_slm_bank_conflict_pad": """```python
def calculate_padded_slm_stride(tile_width: int, bank_count: int = 16) -> int:
    # Standard mistake: returns flat width with 0 padding
    return tile_width
```"""
    }
}

class MockedFrontierProvider(ModelProvider):
    """Replays realistic frontier model failure traces for offline testing."""

    def __init__(self, target_model: str = "gpt-4o") -> None:
        super().__init__("mocked", target_model)

    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """Looks up the realistic failure mode for the corresponding task."""
        from core.config import config
        import json

        for task_file in config.tasks_dir.glob("*.json"):
            data = json.loads(task_file.read_text(encoding="utf-8"))
            if data["prompt"].strip() == prompt.strip():
                task_id = data["id"]
                traces = FRONTIER_MODEL_TRACES.get(self.model_id, FRONTIER_MODEL_TRACES["gpt-4o"])
                return traces.get(task_id, "")
        return ""
