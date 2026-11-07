# Google Vids Master Storyboard & Script: `arc-runtime-eval`

Use this script in **Google Vids** ([vids.google.com](https://vids.google.com)) to generate your official walkthrough video featuring your custom **AI Avatar (`@me`) and cloned voice**.

---

## 🎯 1. Google Vids "Help Me Create" Prompt (Paste this into Google Vids)

> Create a 4.5-minute technical walkthrough video for my micro1 Eval Hackathon submission: "arc-runtime-eval: Frontier Hardware Runtime Invariant Benchmark". The video has 6 scenes with dark glassmorphic engineering slides. Include my AI presenter avatar (@me) speaking with my voice in each scene. Cover the real-world impact of accelerator memory bugs, the 8 practitioner tasks with deterministic AST graders, empirical Intel Arc GPU silicon telemetry, failure transcripts of GPT-4o and Claude 3.5 Sonnet, the benchmark results table with 0% Pass^k consistency, and the killer hot take that AI lacks grounded execution harnesses rather than capability.

---

## 🎬 2. Scene-by-Scene Script & Slide Mapping (Total Duration: 4m 35s ≤ 5m)

### Scene 1: Title & The Real-World Hardware Runtime Gap (0:00 - 0:45)
- **Visual Asset:** Use `video_slides/slide_1.png`
- **Avatar Position:** Bottom-Right (`@me`)
- **Avatar Voiceover Script:**
  > "Welcome to the evaluation walkthrough of arc-runtime-eval, our submission for the micro1 Eval Hackathon: Find What AI Can't Do Yet. In production systems engineering and local GPU deployments, developers increasingly turn to large language models to generate device bindings and accelerated runtime kernels across heterogeneous hardware, such as Intel Arc graphics processing units and neural processing units. While frontier models convincingly produce code for standard CUDA, they exhibit catastrophic blind spots when handling low-level runtime execution. A missed memory barrier or unaligned stride does not just crash—it causes silent numerical corruption in neural activations, or triggers silent 100x execution fallback to the CPU."

---

### Scene 2: The 8 Tasks & Deterministic Scorer Rigor (0:45 - 1:40)
- **Visual Asset:** Use `video_slides/slide_2.png`
- **Avatar Position:** Bottom-Right (`@me`)
- **Avatar Voiceover Script:**
  > "To measure this gap rigorously, we designed eight practitioner-level benchmark tasks covering critical accelerator invariants: from asynchronous Unified Shared Memory event barriers in SYCL, to Xe Matrix systolic cache pitch alignment, dynamic INT4 nibble unpacking order, physical paged attention cache strides, out-of-order queue cross-engine barriers, OpenVINO NPU subgraph static validation, vectorized speculative decoding prefix-scan masks, and shared local memory bank conflict padding. Every task is scored deterministically using code-based AST invariant visitors and modular arithmetic, completely verified through thirty-three triad unit tests in pytest with zero false passes and zero false fails."

---

### Scene 3: Physical Silicon Telemetry on Intel Arc Xe GPU (1:40 - 2:25)
- **Visual Asset:** Use `video_slides/slide_3.png`
- **Avatar Position:** Bottom-Right (`@me`)
- **Avatar Voiceover Script:**
  > "Our benchmark is grounded in empirical hardware performance measured directly on our local Intel Arc Xe-LPG GPU. We measured sustained decode throughput of 14.39 tokens per second, with a rapid 302 millisecond time-to-first-token. Furthermore, to solve the out-of-memory barrier on consumer edge accelerators, our FlashStream weight manager streams all forty-eight Transformer layers of a massive 17.28 gigabyte Qwen 30B Mixture-of-Experts model, with sub-millisecond layer stream latency, while maintaining a peak resident memory delta strictly under thirty megabytes. This proves that high-parameter edge deployment is architecturally viable when invariants are respected."

---

### Scene 4: Failure Transcripts Walkthrough: GPT-4o & Claude (2:25 - 3:20)
- **Visual Asset:** Use `video_slides/slide_4.png`
- **Avatar Position:** Bottom-Right (`@me`)
- **Avatar Voiceover Script:**
  > "Here is where frontier models systematically hallucinate. On Task 2, Intel Arc Xe Matrix Arrays require 2D sub-tiles to be loaded via 64-byte aligned pitch strides. Every frontier model, including GPT-4o and Claude 3.5 Sonnet, naively calculates width times element size, yielding 508 bytes for 127 integer weights, completely failing the hardware cacheline pitch. Similarly, on Task 1, models port their sequential CUDA stream assumptions onto SYCL out-of-order queues, omitting the explicit non-blocking event barrier, h.depends_on. This causes the compute kernel to race against asynchronous DMA memory copies, producing non-reproducible race conditions in production."

---

### Scene 5: Benchmark Evaluation Summary & Consistency Collapse (3:20 - 4:05)
- **Visual Asset:** Use `video_slides/slide_5.png`
- **Avatar Position:** Bottom-Right (`@me`)
- **Avatar Voiceover Script:**
  > "When we evaluate frontier models across twenty-four total trials, a profound limitation emerges. While Claude 3.5 Sonnet achieves a 25% single-pass rate, and GPT-4o and Gemini Pro achieve 12.5% by solving static rank filtering, their multi-trial consistency across all eight tasks drops to absolute zero percent. Zero percent Pass to the k proves that frontier models cannot be trusted with autonomous hardware compilation zero-shot. Every trial failure is packaged into our offline deterministic replay harness, allowing judges to reproduce all findings in 1.5 seconds without paid API credentials."

---

### Scene 6: The Killer Hot Take & The Vibe Coding Manifesto (4:05 - 4:45)
- **Visual Asset:** Use `video_slides/slide_6.png`
- **Avatar Position:** Bottom-Right (`@me`)
- **Avatar Voiceover Script:**
  > "Our headline takeaway is the killer hot take: AI does not lack capability—it lacks grounded execution harnesses. When frontier models are paired with AST invariant gates and hardware groundings, they can hill-climb to 100% correct solutions. Finally, to share a moment of radical honesty: I am not a traditional low-level systems engineer, and I have been unemployed for three months with zero budget. Every invariant, benchmark, and telemetry curve here was engineered through disciplined vibe coding paired with Gemini 3.8 Flash inside Google Antigravity. Thank you for reviewing arc-runtime-eval."

---

## 📤 3. Export & Submission Link Guide (HackerRank)

1. **In Google Vids**: Click **Share** (top right) or **Export to Google Drive**.
2. **In Google Drive**:
   - Right click the generated video ➡️ **Share** ➡️ **General Access**.
   - Change from *"Restricted"* to **"Anyone with the link can view"**.
   - Click **Copy Link**.
3. **In HackerRank**: Paste this Google Drive link into the **Video Walkthrough Link** field.
4. **In README.md**: Replace `https://youtu.be/arc-runtime-eval-walkthrough` on line 20 with this Google Drive link.
