```cpp
// Reference Solution for Task 5: Out-of-Order Queue Inter-Engine Barrier
#include <sycl/sycl.hpp>

void execute_dual_engine_pipeline(
    sycl::queue& copy_queue,
    sycl::queue& compute_queue,
    const float* h_src,
    float* d_buf,
    size_t count
) {
    // 1. Submit async memory copy on dedicated copy queue and capture completion event
    sycl::event copy_event = copy_queue.memcpy(d_buf, h_src, count * sizeof(float));

    // 2. Submit compute kernel on compute engine waiting for copy_event without stalling host CPU
    compute_queue.submit([&](sycl::handler& h) {
        h.depends_on(copy_event);
        h.parallel_for(sycl::range<1>(count), [=](sycl::id<1> i) {
            d_buf[i] = d_buf[i] * 3.14159f;
        });
    });
}
```
