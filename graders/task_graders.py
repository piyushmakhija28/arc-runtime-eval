"""Deterministic scorers for the 8 hardware runtime benchmark tasks."""

import re
from typing import Any, Dict, Tuple
import numpy as np
from graders.base_grader import TaskGrader
from graders.ast_verifier import AstInvariantChecker
from graders.numeric_verifier import NumericInvariantChecker

class SyclUsmBarrierGrader(TaskGrader):
    """Grader for Task 1: SYCL USM Asynchronous Barrier Invariant."""

    def __init__(self) -> None:
        super().__init__("task_01_sycl_usm_barrier")

    def grade(self, output: str) -> Tuple[float, Dict[str, Any]]:
        code = AstInvariantChecker.extract_code_block(output, "cpp")
        has_depends_on = bool(re.search(r"(\w+)\.depends_on\s*\(\s*(\w+)\s*\)", code))
        has_event_capture = bool(re.search(r"(?:sycl::event|auto)\s+(\w+)\s*=\s*(?:\w+)\.memcpy", code))
        has_forbidden_wait = bool(re.search(r"(?:\w+)\.wait\s*\(\s*\)", code))

        passed = has_depends_on and has_event_capture and not has_forbidden_wait
        score = 1.0 if passed else 0.0
        return score, {
            "has_depends_on": has_depends_on,
            "has_event_capture": has_event_capture,
            "has_forbidden_wait": has_forbidden_wait,
            "passed_invariants": passed
        }

class Xmx2DBlockPitchGrader(TaskGrader):
    """Grader for Task 2: Intel Arc XMX 2D Block Load Pitch Alignment."""

    def __init__(self) -> None:
        super().__init__("task_02_xmx_2d_block_pitch")

    def grade(self, output: str) -> Tuple[float, Dict[str, Any]]:
        code = AstInvariantChecker.extract_code_block(output, "python")
        scope: Dict[str, Any] = {}
        try:
            exec(code, scope)
            calculate_pitch_func = scope.get("calculate_xmx_pitch")
            if not callable(calculate_pitch_func):
                return 0.0, {"error": "Function calculate_xmx_pitch not found", "passed_invariants": False}

            test_cases = [
                (128, 4, 64, 512),
                (127, 4, 64, 512),
                (13, 2, 64, 64),
                (1024, 2, 64, 2048),
            ]
            for width, elem_size, align, expected_pitch in test_cases:
                actual_pitch = calculate_pitch_func(width, elem_size, align)
                if actual_pitch != expected_pitch:
                    return 0.0, {
                        "error": f"Failed on width={width}: got {actual_pitch}, expected {expected_pitch}",
                        "passed_invariants": False
                    }
                if not NumericInvariantChecker.verify_pitch_alignment(actual_pitch, align):
                    return 0.0, {"error": "Pitch not aligned to boundary", "passed_invariants": False}

            return 1.0, {"passed_invariants": True}
        except Exception as e:
            return 0.0, {"error": str(e), "passed_invariants": False}

class IpexInt4DequantGrader(TaskGrader):
    """Grader for Task 3: IPEX INT4 Symmetric Weight Dequantization Unpack."""

    def __init__(self) -> None:
        super().__init__("task_03_ipex_int4_dequant_stride")

    def grade(self, output: str) -> Tuple[float, Dict[str, Any]]:
        code = AstInvariantChecker.extract_code_block(output, "python")
        scope: Dict[str, Any] = {}
        try:
            exec(code, scope)
            dequant_func = scope.get("dequantize_int4_symmetric")
            if not callable(dequant_func):
                return 0.0, {"error": "Function dequantize_int4_symmetric not found", "passed_invariants": False}

            packed_weights = np.array([0x5A, 0x1F, 0xE2], dtype=np.uint8)
            scales = np.array([0.5, 0.5, 1.0, 1.0, 2.0, 2.0], dtype=np.float32)
            expected = np.array([
                (0x0A - 8) * 0.5,
                (0x05 - 8) * 0.5,
                (0x0F - 8) * 1.0,
                (0x01 - 8) * 1.0,
                (0x02 - 8) * 2.0,
                (0x0E - 8) * 2.0
            ], dtype=np.float32)

            actual = dequant_func(packed_weights, scales)
            if not isinstance(actual, np.ndarray):
                actual = np.array(actual, dtype=np.float32)

            if NumericInvariantChecker.compare_tensors(actual, expected, atol=1e-4):
                return 1.0, {"passed_invariants": True}
            else:
                return 0.0, {"error": "Tensor values mismatched expected ground truth", "passed_invariants": False}
        except Exception as e:
            return 0.0, {"error": str(e), "passed_invariants": False}

class PagedAttentionStrideGrader(TaskGrader):
    """Grader for Task 4: Dynamic Paged Attention KV Cache Stride Alignment."""

    def __init__(self) -> None:
        super().__init__("task_04_paged_attention_strides")

    def grade(self, output: str) -> Tuple[float, Dict[str, Any]]:
        code = AstInvariantChecker.extract_code_block(output, "python")
        scope: Dict[str, Any] = {}
        try:
            exec(code, scope)
            calc_offset_func = scope.get("calculate_kv_offset")
            if not callable(calc_offset_func):
                return 0.0, {"error": "Function calculate_kv_offset not found", "passed_invariants": False}

            block_table = [4, 7, 2, 9]
            page_size = 16
            num_heads = 32
            head_dim = 128
            test_cases = [
                (0, 0, 0, (4 * 16 * 32 * 128) + (0 * 32 * 128) + (0 * 128) + 0),
                (17, 3, 50, (7 * 16 * 32 * 128) + (1 * 32 * 128) + (3 * 128) + 50),
                (35, 31, 127, (2 * 16 * 32 * 128) + (3 * 32 * 128) + (31 * 128) + 127),
            ]
            for token_idx, head_idx, dim_idx, expected_offset in test_cases:
                actual_offset = calc_offset_func(token_idx, head_idx, dim_idx, block_table, page_size, num_heads, head_dim)
                if actual_offset != expected_offset:
                    return 0.0, {
                        "error": f"Offset mismatch: got {actual_offset}, expected {expected_offset}",
                        "passed_invariants": False
                    }
            return 1.0, {"passed_invariants": True}
        except Exception as e:
            return 0.0, {"error": str(e), "passed_invariants": False}

class OutOfOrderQueueSyncGrader(TaskGrader):
    """Grader for Task 5: Out-of-Order Queue Inter-Engine Barrier."""

    def __init__(self) -> None:
        super().__init__("task_05_ooo_queue_cross_sync")

    def grade(self, output: str) -> Tuple[float, Dict[str, Any]]:
        code = AstInvariantChecker.extract_code_block(output, "cpp")
        has_copy_q = "copy_queue" in code or "q_copy" in code or "copy_q" in code or "copy" in code.lower()
        has_compute_q = "compute_queue" in code or "q_compute" in code or "compute_q" in code or "compute" in code.lower()
        has_event_transfer = bool(re.search(r"depends_on\s*\(\s*(\w+)\s*\)", code))
        has_blocking_wait = "copy_queue.wait()" in code or "q_copy.wait()" in code

        passed = has_copy_q and has_compute_q and has_event_transfer and not has_blocking_wait
        score = 1.0 if passed else 0.0
        return score, {
            "has_copy_q": has_copy_q,
            "has_compute_q": has_compute_q,
            "has_event_transfer": has_event_transfer,
            "has_blocking_wait": has_blocking_wait,
            "passed_invariants": passed
        }

class OpenVinoNpuSubgraphGrader(TaskGrader):
    """Grader for Task 6: OpenVINO / NPU Compiler Subgraph Partitioning Invariant."""

    def __init__(self) -> None:
        super().__init__("task_06_openvino_npu_subgraph")

    def grade(self, output: str) -> Tuple[float, Dict[str, Any]]:
        code = AstInvariantChecker.extract_code_block(output, "python")
        scope: Dict[str, Any] = {}
        try:
            exec(code, scope)
            validate_subgraph_func = scope.get("validate_npu_compatibility")
            if not callable(validate_subgraph_func):
                return 0.0, {"error": "Function validate_npu_compatibility not found", "passed_invariants": False}

            valid_graph = {"nodes": ["MatMul", "Add", "Relu"], "dynamic_ranks": False, "opset": 11}
            invalid_dynamic = {"nodes": ["MatMul", "Add", "Relu"], "dynamic_ranks": True, "opset": 11}
            invalid_op = {"nodes": ["MatMul", "NonZero", "Relu"], "dynamic_ranks": False, "opset": 11}

            if not validate_subgraph_func(valid_graph):
                return 0.0, {"error": "Rejected valid static graph", "passed_invariants": False}
            if validate_subgraph_func(invalid_dynamic):
                return 0.0, {"error": "Accepted unsupported dynamic ranks for NPU", "passed_invariants": False}
            if validate_subgraph_func(invalid_op):
                return 0.0, {"error": "Accepted unsupported op NonZero for NPU", "passed_invariants": False}

            return 1.0, {"passed_invariants": True}
        except Exception as e:
            return 0.0, {"error": str(e), "passed_invariants": False}

class SpeculativeTokenMaskGrader(TaskGrader):
    """Grader for Task 7: Speculative Decoding Vectorized Draft Token Verification Mask."""

    def __init__(self) -> None:
        super().__init__("task_07_speculative_token_mask")

    def grade(self, output: str) -> Tuple[float, Dict[str, Any]]:
        code = AstInvariantChecker.extract_code_block(output, "python")
        scope: Dict[str, Any] = {}
        try:
            exec(code, scope)
            compute_mask_func = scope.get("compute_acceptance_mask")
            if not callable(compute_mask_func):
                return 0.0, {"error": "Function compute_acceptance_mask not found", "passed_invariants": False}

            probs = np.array([0.9, 0.8, 0.4, 0.9, 0.95], dtype=np.float32)
            thresholds = np.array([0.5, 0.5, 0.5, 0.5, 0.5], dtype=np.float32)
            expected_mask = np.array([1, 1, 0, 0, 0], dtype=np.int32)

            actual_mask = compute_mask_func(probs, thresholds)
            if not isinstance(actual_mask, np.ndarray):
                actual_mask = np.array(actual_mask, dtype=np.int32)

            if np.array_equal(actual_mask, expected_mask):
                return 1.0, {"passed_invariants": True}
            else:
                return 0.0, {"error": "Failed cumulative acceptance mask condition", "passed_invariants": False}
        except Exception as e:
            return 0.0, {"error": str(e), "passed_invariants": False}

class SlmBankConflictPadGrader(TaskGrader):
    """Grader for Task 8: Shared Local Memory (SLM) Bank Conflict Padding."""

    def __init__(self) -> None:
        super().__init__("task_08_slm_bank_conflict_pad")

    def grade(self, output: str) -> Tuple[float, Dict[str, Any]]:
        code = AstInvariantChecker.extract_code_block(output, "python")
        scope: Dict[str, Any] = {}
        try:
            exec(code, scope)
            pad_func = scope.get("calculate_padded_slm_stride")
            if not callable(pad_func):
                return 0.0, {"error": "Function calculate_padded_slm_stride not found", "passed_invariants": False}

            test_cases = [
                (16, 16, 17),
                (32, 16, 33),
                (64, 16, 65),
                (15, 16, 15),
            ]
            for width, bank_count, expected_stride in test_cases:
                actual_stride = pad_func(width, bank_count)
                if actual_stride != expected_stride:
                    return 0.0, {
                        "error": f"Failed for width={width}: got {actual_stride}, expected {expected_stride}",
                        "passed_invariants": False
                    }
                if not NumericInvariantChecker.verify_coprime_bank_stride(actual_stride, bank_count):
                    return 0.0, {"error": "Stride is not coprime to bank count", "passed_invariants": False}

            return 1.0, {"passed_invariants": True}
        except Exception as e:
            return 0.0, {"error": str(e), "passed_invariants": False}
