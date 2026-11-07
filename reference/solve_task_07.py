```python
import numpy as np

def compute_acceptance_mask(target_probs: np.ndarray, thresholds: np.ndarray) -> np.ndarray:
    """Computes vectorized speculative decoding acceptance mask with prefix-scan dependency."""
    individual_accept = (target_probs >= thresholds).astype(np.int32)
    return np.cumprod(individual_accept, dtype=np.int32)
```
