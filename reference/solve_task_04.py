```python
def calculate_kv_offset(
    token_idx: int,
    head_idx: int,
    dim_idx: int,
    block_table: list,
    page_size: int,
    num_heads: int,
    head_dim: int
) -> int:
    """Calculates flat physical memory offset in a paged KV cache table."""
    logical_page_idx = token_idx // page_size
    slot_in_page = token_idx % page_size
    physical_page_id = block_table[logical_page_idx]

    page_stride = page_size * num_heads * head_dim
    token_stride = num_heads * head_dim
    head_stride = head_dim

    return (
        physical_page_id * page_stride
        + slot_in_page * token_stride
        + head_idx * head_stride
        + dim_idx
    )
```
