```python
def validate_npu_compatibility(subgraph_spec: dict) -> bool:
    """Validates if OpenVINO subgraph meets strict static constraints for Intel NPU."""
    if subgraph_spec.get("dynamic_ranks", False):
        return False

    supported_npu_ops = {
        "MatMul", "Add", "Subtract", "Multiply", "Relu", "Gelu", 
        "LayerNorm", "Softmax", "Reshape", "Transpose", "Convolution"
    }

    nodes = subgraph_spec.get("nodes", [])
    for op in nodes:
        if op not in supported_npu_ops:
            return False

    return True
```
