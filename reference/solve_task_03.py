```python
import numpy as np

def dequantize_int4_symmetric(packed_weights: np.ndarray, scales: np.ndarray) -> np.ndarray:
    """Unpacks INT4 symmetric weights (low nibble first, offset 8) with per-channel scaling."""
    total_weights = len(packed_weights) * 2
    unpacked = np.empty(total_weights, dtype=np.float32)

    for i, byte_val in enumerate(packed_weights):
        low_nibble = int(byte_val & 0x0F)
        high_nibble = int((byte_val >> 4) & 0x0F)
        
        idx = i * 2
        unpacked[idx] = float(low_nibble - 8) * float(scales[idx])
        unpacked[idx + 1] = float(high_nibble - 8) * float(scales[idx + 1])

    return unpacked
```
