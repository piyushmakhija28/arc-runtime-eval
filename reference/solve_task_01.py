```cpp
// Reference Solution for Task 1: SYCL USM Asynchronous Barrier Invariant
#include <sycl/sycl.hpp>

void submit_workload(sycl::queue& q, const float* h_weights, float* d_weights, size_t count) {
    // Asynchronously copy data from host to device and capture event
    sycl::event copy_event = q.memcpy(d_weights, h_weights, count * sizeof(float));

    // Submit compute kernel with explicit event dependency barrier
    q.submit([&](sycl::handler& h) {
        h.depends_on(copy_event);
        h.parallel_for(sycl::range<1>(count), [=](sycl::id<1> idx) {
            d_weights[idx] = d_weights[idx] * 2.0f;
        });
    });
}
```
