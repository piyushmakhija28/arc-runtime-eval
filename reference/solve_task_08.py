```python
import math

def calculate_padded_slm_stride(tile_width: int, bank_count: int = 16) -> int:
    """Calculates bank-conflict-free row stride in Intel Xe Shared Local Memory."""
    if math.gcd(tile_width, bank_count) > 1:
        return tile_width + 1
    return tile_width
```
