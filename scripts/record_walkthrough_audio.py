"""Interactive audio recorder for arc-runtime-eval walkthrough video.

Allows the user (Piyush) to record each of the 6 scenes using their own voice
via the built-in laptop microphone, automatically assembling the 1080p MP4 walkthrough
with dynamic broadcast subtitles and executive speaker bubble.
"""

import os
from pathlib import Path
import subprocess
import time
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT_DIR / "build_video"
BUILD_DIR.mkdir(parents=True, exist_ok=True)

AVATAR_PATH = Path(os.environ["TEMP"]) / "piyush_avatar.png"
OUTPUT_VIDEO = ROOT_DIR / "arc_runtime_eval_walkthrough.mp4"
OUTPUT_SRT = ROOT_DIR / "arc_runtime_eval_captions.srt"

WIDTH, HEIGHT = 1920, 1080
MIC_DEVICE = "audio=Microphone Array (Intel® Smart Sound Technology for Digital Microphones)"

SCENES = [
    {
        "id": 1,
        "title": "Scene 1: The Hook & Real-World Problem",
        "sentences": [
            "Hey everyone! Welcome to the evaluation walkthrough of arc-runtime-eval.",
            "Today, I want to show you a critical blindspot in frontier AI: hardware runtime invariants.",
            "In modern edge AI, we rely on LLMs to write low-level GPU code—and the code compiles cleanly.",
            "But the moment you execute it on actual hardware, it completely breaks.",
            "A missed memory barrier or pitch stride silently corrupts your memory, crashes device queues, or causes a massive 100x CPU fallback."
        ]
    },
    {
        "id": 2,
        "title": "Scene 2: The 8 Tasks & Deterministic Graders",
        "sentences": [
            "To measure this gap rigorously, we built eight practitioner-level benchmark tasks on real Intel Arc accelerators.",
            "We test everything from asynchronous SYCL USM event barriers to Xe Matrix 2D systolic cache pitch alignments.",
            "Every single solution is scored deterministically using code AST visitors and exact hardware pitch arithmetic.",
            "Our grading suite is formally verified through thirty-three triad unit tests in pytest with zero false passes."
        ]
    },
    {
        "id": 3,
        "title": "Scene 3: Hardware Grounding on Intel Arc GPU",
        "sentences": [
            "Our benchmark is grounded in empirical hardware performance measured right here on our local Intel Arc GPU.",
            "We clocked sustained decode throughput at 14.39 tokens per second, with a rapid 302 millisecond time-to-first-token.",
            "Even better, our FlashStream weight manager streams all forty-eight layers of a massive seventeen gigabyte Qwen model.",
            "With sub-millisecond layer swapping, FlashStream keeps peak RAM delta strictly under thirty megabytes, eliminating Out-Of-Memory crashes."
        ]
    },
    {
        "id": 4,
        "title": "Scene 4: Where Frontier Models Hallucinate",
        "sentences": [
            "Now, let's look at where frontier models consistently fail. On Task 2, Intel Xe Matrix Arrays load 2D sub-tiles via 64-byte aligned strides.",
            "Every single frontier model—including GPT-4o and Claude 3.5 Sonnet—naively calculates width times element size, completely missing the cacheline pitch!",
            "On Task 1, models port CUDA stream assumptions onto out-of-order SYCL queues, omitting explicit host synchronization barriers.",
            "This causes compute kernels to race against DMA memory copies, producing silent race conditions in production."
        ]
    },
    {
        "id": 5,
        "title": "Scene 5: Results & Consistency Metric",
        "sentences": [
            "When we evaluate models across twenty-four repeated trials, a profound limitation emerges.",
            "While Claude 3.5 Sonnet achieves a 25% single-pass rate, and GPT-4o gets 12.5% by solving static rank filtering,",
            "their multi-trial consistency across all eight tasks drops to absolute zero percent! Zero percent Pass to the k proves zero-shot code is unsafe.",
            "Every trial failure is packaged into our offline deterministic replay harness, reproducible in under two seconds."
        ]
    },
    {
        "id": 6,
        "title": "Scene 6: The Killer Hot Take & Personal Manifesto",
        "sentences": [
            "Our headline takeaway is the killer hot take: AI does not lack capability, it lacks grounded execution harnesses.",
            "When frontier models are paired with AST invariant gates and hardware groundings, they can hill-climb to 100% correct code.",
            "Finally, to share a moment of radical honesty: I am not a traditional systems engineer, and I have been unemployed for three months with zero budget.",
            "Every invariant and benchmark here was engineered through disciplined vibe coding with Gemini inside Google Antigravity. Thank you!"
        ]
    }
]

def format_srt_time(seconds: float) -> str:
    """Formats float seconds into SRT timestamp HH:MM:SS,mmm."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def record_scene_audio(scene_idx: int, scene_data: dict) -> Path:
    """Prompts user to speak and records audio for the scene via microphone."""
    wav_path = BUILD_DIR / f"user_audio_scene_{scene_idx}.wav"
    
    print("\n" + "="*80)
    print(f"  🎙️  {scene_data['title'].upper()}")
    print("="*80)
    print("\nPlease read this script naturally and conversationally:\n")
    for s in scene_data['sentences']:
        print(f"  👉  \"{s}\"\n")
    
    input("Press [ENTER] to START recording (speak clearly into your microphone)...")
    print("\n🔴 RECORDING IN PROGRESS... Speak now! (Press [ENTER] when finished)")
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "dshow",
        "-i", MIC_DEVICE,
        "-ac", "1",
        "-ar", "44100",
        str(wav_path)
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    input()
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
    
    print(f"✅ Saved scene audio: {wav_path.name}")
    return wav_path

def main():
    """Main interactive audio recording and video assembly pipeline."""
    from scripts.generate_walkthrough_video import (
        render_base_slide, draw_broadcast_subtitles, get_audio_duration
    )
    
    print("\n" + "#"*80)
    print("   🎙️  PIYUSH MAKHIJA - LIVE VOICE WALKTHROUGH RECORDER")
    print("   Records your authentic voice and automatically compiles 1080p video")
    print("#"*80)
    
    clip_files = []
    srt_entries = []
    global_time = 0.0
    srt_counter = 1
    
    for scene in SCENES:
        scene_idx = scene["id"]
        wav_path = record_scene_audio(scene_idx, scene)
        dur = get_audio_duration(wav_path)
        
        # Subtitle summary text for the scene
        sub_text = " ".join(scene["sentences"][:2])
        base_img = render_base_slide(scene_idx)
        draw_broadcast_subtitles(base_img, sub_text)
        
        frame_path = BUILD_DIR / f"user_frame_scene_{scene_idx}.png"
        base_img.save(frame_path)
        
        clip_path = BUILD_DIR / f"user_clip_scene_{scene_idx}.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(frame_path),
            "-i", str(wav_path),
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(dur + 0.3),
            "-shortest",
            str(clip_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        clip_files.append(clip_path)
        
        start_srt = format_srt_time(global_time)
        end_srt = format_srt_time(global_time + dur + 0.3)
        srt_entries.append(f"{srt_counter}\n{start_srt} --> {end_srt}\n{sub_text}\n")
        
        srt_counter += 1
        global_time += (dur + 0.3)
    
    print(f"\nTotal video duration: {global_time:.2f} seconds ({global_time/60:.2f} minutes)")
    
    with open(OUTPUT_SRT, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries) + "\n")
        
    concat_list = BUILD_DIR / "concat_user_clips.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for clip in clip_files:
            f.write(f"file '{clip.name}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy",
        str(OUTPUT_VIDEO)
    ]
    subprocess.run(cmd, capture_output=True, check=True, cwd=str(BUILD_DIR))
    print(f"\n🎉 Successfully compiled YOUR 100% AUTHENTIC VOICE walkthrough video: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    main()
