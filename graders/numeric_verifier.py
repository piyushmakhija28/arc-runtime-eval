"""Numerical, tensor, and modular arithmetic invariant checkers."""

import math
from typing import Any, Sequence
import numpy as np

class NumericInvariantChecker:
    """Verifies numerical tolerances, stride alignment, and bank conflict conditions."""

    @staticmethod
    def compare_tensors(
        actual: np.ndarray, expected: np.ndarray, atol: float = 1e-4, rtol: float = 1e-3
    ) -> bool:
        """Verifies tensor closeness within absolute and relative floating-point tolerances.

        Args:
            actual: Computed output tensor.
            expected: Ground truth target tensor.
            atol: Absolute tolerance bound.
            rtol: Relative tolerance bound.

        Returns:
            bool: True if tensors match shape and numerical bounds.
        """
        if actual.shape != expected.shape:
            return False
        return bool(np.allclose(actual, expected, atol=atol, rtol=rtol))

    @staticmethod
    def verify_pitch_alignment(pitch_bytes: int, alignment_boundary: int = 64) -> bool:
        """Verifies if computed pitch satisfies hardware cache line alignment.

        Args:
            pitch_bytes: Row pitch in bytes.
            alignment_boundary: Required modular boundary, default 64 bytes.

        Returns:
            bool: True if pitch is divisible by alignment_boundary.
        """
        return pitch_bytes > 0 and (pitch_bytes % alignment_boundary == 0)

    @staticmethod
    def verify_coprime_bank_stride(stride_elements: int, bank_count: int = 16) -> bool:
        """Verifies if memory stride avoids power-of-two bank conflict serialization.

        Args:
            stride_elements: Stride between successive rows in shared local memory.
            bank_count: Number of independent memory banks (16 on Intel Xe).

        Returns:
            bool: True if stride and bank_count are coprime (gcd == 1).
        """
        return math.gcd(stride_elements, bank_count) == 1
