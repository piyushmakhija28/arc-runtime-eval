```python
def calculate_xmx_pitch(width: int, element_size_bytes: int, alignment_bytes: int = 64) -> int:
    """Calculates row pitch aligned to 64-byte hardware cache boundaries."""
    raw_row_bytes = width * element_size_bytes
    return ((raw_row_bytes + alignment_bytes - 1) // alignment_bytes) * alignment_bytes
```
