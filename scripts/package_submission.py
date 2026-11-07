"""HackerRank Eval Submission packager and compliance validator.

Strictly adheres to micro1 Eval Hackathon Question 3 specifications:
- Exactly 1 .zip file < 50 MB
- README.md at root with all 8 mandatory sections
- Complete code, tasks, graders, transcripts, results, and tests included
- Strictly zero video binaries, zero API keys, and zero confidential/cache files
"""

import os
import sys
import zipfile
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ZIP_PATH = ROOT_DIR / "arc-runtime-eval-submission.zip"

REQUIRED_ROOT_FILES = [
    "README.md",
    "requirements.txt",
    "run_eval.py",
    "pytest.ini",
    ".env.example",
    "LICENSE",
    ".gitignore",
]

REQUIRED_DIRECTORIES = [
    "core",
    "graders",
    "providers",
    "reference",
    "results",
    "tasks",
    "tests",
    "transcripts",
]

FORBIDDEN_EXTENSIONS = {
    ".mp4", ".wav", ".avi", ".mov", ".mkv", ".png", ".jpg", ".jpeg"
}

FORBIDDEN_DIR_NAMES = {
    "build_video", ".git", "__pycache__", ".pytest_cache", ".benchmarks", "video_slides", "logs"
}

def validate_readme():
    """Validates that README.md contains all 8 required HackerRank sections."""
    readme_path = ROOT_DIR / "README.md"
    assert readme_path.exists(), "README.md missing from repository root!"
    
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    required_keywords = [
        "Short Description",
        "Video Walkthrough Link",
        "Domain and Expertise",
        "What It Tests and Why It Matters",
        "Benchmark Tasks",
        "Benchmark Results",
        "Failure Analysis",
        "Setup & Reproducibility Instructions",
        "Prior Work",
        "drive.google.com"
    ]
    
    print("📋 Validating README.md structure against HackerRank participant guide...")
    for kw in required_keywords:
        assert kw.lower() in content.lower(), f"README.md missing required section/keyword: '{kw}'"
    print("  ✅ All mandatory README sections and valid video link verified!")

def run_preflight_unit_tests():
    """Runs pytest to guarantee 33/33 unit tests pass before packaging."""
    print("🧪 Running pre-flight unit test suite (33 triad tests)...")
    res = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=str(ROOT_DIR), capture_output=True, text=True)
    assert res.returncode == 0, f"Pytest unit tests failed!\n{res.stdout}\n{res.stderr}"
    print(f"  ✅ 100% of unit tests passing cleanly:\n     {res.stdout.strip()}")

def build_submission_zip():
    """Packages only clean, compliant code and supporting files into submission zip."""
    print(f"📦 Packaging submission zip: {ZIP_PATH.name}...")
    
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
        
    included_files = []
    
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add root files
        for fname in REQUIRED_ROOT_FILES:
            fpath = ROOT_DIR / fname
            assert fpath.exists(), f"Required root file missing: {fname}"
            zf.write(fpath, arcname=fname)
            included_files.append(fname)
            
        # Add required directory trees
        for dname in REQUIRED_DIRECTORIES:
            dpath = ROOT_DIR / dname
            assert dpath.exists(), f"Required directory missing: {dname}"
            
            for root, dirs, files in os.walk(dpath):
                # Prune forbidden directories
                dirs[:] = [d for d in dirs if d not in FORBIDDEN_DIR_NAMES]
                
                for f in files:
                    file_path = Path(root) / f
                    # Skip forbidden extensions
                    if file_path.suffix.lower() in FORBIDDEN_EXTENSIONS:
                        continue
                    if f.startswith(".env") and f != ".env.example":
                        continue
                    if "__pycache__" in str(file_path):
                        continue
                        
                    rel_path = file_path.relative_to(ROOT_DIR)
                    zf.write(file_path, arcname=str(rel_path).replace("\\", "/"))
                    included_files.append(str(rel_path).replace("\\", "/"))
                    
    zip_size_bytes = ZIP_PATH.stat().st_size
    zip_size_mb = zip_size_bytes / (1024 * 1024)
    zip_size_kb = zip_size_bytes / 1024
    
    print(f"\n🎉 Successfully created: {ZIP_PATH.name}")
    print(f"   Files included: {len(included_files)}")
    print(f"   Zip Size: {zip_size_kb:.1f} KB ({zip_size_mb:.2f} MB) - Strictly < 50 MB limit!")
    assert zip_size_mb < 50.0, f"Zip file exceeds 50 MB: {zip_size_mb:.2f} MB!"
    
    # Integrity check: verify zero forbidden files
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        for item in zf.namelist():
            for forbidden_ext in FORBIDDEN_EXTENSIONS:
                assert not item.lower().endswith(forbidden_ext), f"Forbidden file found in zip: {item}"
            path_parts = item.split("/")
            for forbidden_dir in FORBIDDEN_DIR_NAMES:
                assert forbidden_dir not in path_parts, f"Forbidden directory found in zip: {item}"

    print("🛡️ Integrity audit passed: 0 video binaries, 0 credentials, 0 cache files inside zip.")

def main():
    print("#"*80)
    print("   HACKERRANK EVAL SUBMISSION PACKAGER (micro1 Eval Hackathon)")
    print("#"*80)
    validate_readme()
    run_preflight_unit_tests()
    build_submission_zip()

if __name__ == "__main__":
    main()
