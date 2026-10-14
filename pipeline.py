from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import textwrap
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCENE_CLASS = "GoogleADKFullInfo"
FPS = 30
WIDTH, HEIGHT = 1920, 1080
SAMPLE_RATE = 48000
FRAME = 1 / FPS

AUDIO_DIR = ROOT / "audio"
TIMING_PATH = AUDIO_DIR / "timing.json"
STORYBOARD_PATH = ROOT / "storyboard.json"
DESCRIPTION_PATH = ROOT / "youtube_description.txt"
RENDERED_VIDEO = ROOT / "media" / "videos" / "scene" / f"{HEIGHT}p{FPS}" / f"{SCENE_CLASS}.mp4"

OUT_DIR = ROOT / "output"
QA_DIR = OUT_DIR / "qa"
NARRATION_WAV = OUT_DIR / "narration.wav"
FINAL_MP4 = OUT_DIR / "google-adk-full-guide.mp4"
FINAL_SRT = OUT_DIR / "google-adk-full-guide.en-IN.srt"

SRT_LINE_CHARS = 42
SRT_MAX_LINES = 2
STILL_OFFSET = 1.0


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print("$ " + " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=True, text=True, encoding="utf-8", errors="replace", **kwargs)


def beat_schedule() -> list[dict]:
    """Beats in storyboard order with absolute start/end times from measured audio."""
    timing = {row["id"]: row for row in load_json(TIMING_PATH)["lines"]}
    schedule = []
    clock = 0.0
    for chapter in load_json(STORYBOARD_PATH)["chapters"]:
        for index, beat in enumerate(chapter["beats"]):
            row = timing[beat["id"]]
            schedule.append(
                {
                    "id": beat["id"],
                    "chapter": int(chapter["number"]),
                    "chapter_title": chapter["title"],
                    "chapter_start": index == 0,
                    "text": row["text"],
                    "file": row["file"],
                    "start": clock,
                    "end": clock + float(row["duration"]),
                }
            )
            clock += float(row["duration"])
    return schedule


def step_render() -> None:
    if not shutil.which("manim"):
        raise SystemExit("manim is not on PATH")
    run(
        [
            "manim", "render", "-qh", "--fps", str(FPS), "--disable_caching", "--flush_cache", "--progress_bar", "none",
            "scene.py", SCENE_CLASS,
        ],
        cwd=ROOT,
    )
    if not RENDERED_VIDEO.exists():
        raise SystemExit(f"render finished but {RENDERED_VIDEO} is missing")
    print(f"rendered {RENDERED_VIDEO.relative_to(ROOT)}")


def step_stitch(schedule: list[dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    params = None
    with wave.open(str(NARRATION_WAV), "wb") as out:
        for beat in schedule:
            with wave.open(str(AUDIO_DIR / beat["file"]), "rb") as src:
                current = (src.getnchannels(), src.getsampwidth(), src.getframerate())
                if current[2] != SAMPLE_RATE:
                    raise SystemExit(f"{beat['file']} is {current[2]} Hz, expected {SAMPLE_RATE}")
                if params is None:
                    params = current
                    out.setnchannels(current[0])
                    out.setsampwidth(current[1])
                    out.setframerate(current[2])
                elif current != params:
                    raise SystemExit(f"{beat['file']} format {current} differs from {params}")
                out.writeframes(src.readframes(src.getnframes()))
    with wave.open(str(NARRATION_WAV), "rb") as check:
        seconds = check.getnframes() / check.getframerate()
    print(f"stitched {len(schedule)} clips into {NARRATION_WAV.relative_to(ROOT)} ({seconds:.3f}s)")


def step_mux() -> None:
    if not RENDERED_VIDEO.exists():
        raise SystemExit(f"missing rendered video {RENDERED_VIDEO}; run the render step first")
    if not NARRATION_WAV.exists():
        raise SystemExit(f"missing {NARRATION_WAV}; run the stitch step first")
    run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(RENDERED_VIDEO), "-i", str(NARRATION_WAV),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", str(SAMPLE_RATE),
            "-movflags", "+faststart",
            str(FINAL_MP4),
        ]
    )
    print(f"muxed {FINAL_MP4.relative_to(ROOT)}")


def srt_timestamp(seconds: float) -> str:
    millis = max(0, round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def wrap(text: str) -> list[str]:
    return textwrap.wrap(text, width=SRT_LINE_CHARS, break_long_words=False, break_on_hyphens=False)


def split_balanced(words: list[str], parts: int) -> list[list[str]]:
    total = sum(len(w) + 1 for w in words)
    groups: list[list[str]] = [[] for _ in range(parts)]
    seen = 0
    for word in words:
        index = min(parts - 1, int(seen * parts / total))
        groups[index].append(word)
        seen += len(word) + 1
    return [g for g in groups if g]


def beat_cues(beat: dict) -> list[tuple[float, float, list[str]]]:
    words = beat["text"].split()
    parts = -(-len(wrap(beat["text"])) // SRT_MAX_LINES)
    while True:
        chunks = [wrap(" ".join(group)) for group in split_balanced(words, parts)]
        if all(len(chunk) <= SRT_MAX_LINES for chunk in chunks):
            break
        parts += 1
    weights = [sum(len(line.split()) for line in chunk) for chunk in chunks]
    total = sum(weights)
    span = beat["end"] - beat["start"]
    cues = []
    cursor = beat["start"]
    for chunk, weight in zip(chunks, weights):
        end = cursor + span * weight / total
        cues.append((cursor, end, chunk))
        cursor = end
    return cues


def step_srt(schedule: list[dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    blocks = []
    for beat in schedule:
        for start, end, chunk in beat_cues(beat):
            blocks.append(f"{len(blocks) + 1}\n{srt_timestamp(start)} --> {srt_timestamp(end)}\n" + "\n".join(chunk) + "\n")
    FINAL_SRT.write_text("\n".join(blocks), encoding="utf-8")
    print(f"wrote {len(blocks)} cues to {FINAL_SRT.relative_to(ROOT)}")


def probe(path: Path) -> dict:
    result = run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        capture_output=True,
    )
    return json.loads(result.stdout)


def parse_srt_time(value: str) -> float:
    hours, minutes, rest = value.split(":")
    secs, millis = rest.split(",")
    return int(hours) * 3600 + int(minutes) * 60 + int(secs) + int(millis) / 1000


def parse_srt(path: Path) -> list[tuple[float, float, str]]:
    cues = []
    for block in path.read_text(encoding="utf-8").strip().split("\n\n"):
        lines = block.splitlines()
        start, end = (parse_srt_time(part.strip()) for part in lines[1].split("-->"))
        cues.append((start, end, " ".join(lines[2:])))
    return cues


def integrated_loudness(path: Path) -> float | None:
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-map", "0:a:0", "-filter:a", "ebur128", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    matches = re.findall(r"I:\s+(-?\d+(?:\.\d+)?) LUFS", result.stderr)
    return float(matches[-1]) if matches else None


def mmss(seconds: float) -> str:
    return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"


def step_qa(schedule: list[dict]) -> bool:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    expected = schedule[-1]["end"]
    checks: list[dict] = []

    def check(name: str, ok: bool | None, detail: str) -> None:
        status = "INFO" if ok is None else ("PASS" if ok else "FAIL")
        checks.append({"check": name, "status": status, "detail": detail})

    info = probe(FINAL_MP4)
    video = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
    audio = next((s for s in info["streams"] if s["codec_type"] == "audio"), {})

    check("resolution", (video.get("width"), video.get("height")) == (WIDTH, HEIGHT), f"{video.get('width')}x{video.get('height')}")
    check("frame rate", video.get("r_frame_rate") == f"{FPS}/1", str(video.get("r_frame_rate")))
    check("video codec", video.get("codec_name") == "h264" and video.get("pix_fmt") == "yuv420p", f"{video.get('codec_name')} {video.get('pix_fmt')}")
    check("audio codec", audio.get("codec_name") == "aac" and audio.get("sample_rate") == str(SAMPLE_RATE), f"{audio.get('codec_name')} {audio.get('sample_rate')} Hz")

    video_duration = float(video.get("duration", 0))
    audio_duration = float(audio.get("duration", 0))
    check("video duration", abs(video_duration - expected) <= FRAME, f"{video_duration:.3f}s vs narration {expected:.3f}s")
    check("audio duration", abs(audio_duration - expected) <= FRAME, f"{audio_duration:.3f}s vs narration {expected:.3f}s")
    check("audio/video drift", abs(video_duration - audio_duration) <= FRAME, f"{video_duration - audio_duration:+.3f}s")

    cues = parse_srt(FINAL_SRT)
    ordered = all(start < end for start, end, _ in cues)
    no_overlap = all(cues[i][1] <= cues[i + 1][0] for i in range(len(cues) - 1))
    check("srt cues ordered", ordered, f"{len(cues)} cues")
    check("srt cues non-overlapping", no_overlap, "each cue ends before the next starts" if no_overlap else "overlap found")
    check("srt within video", cues[-1][1] <= video_duration + FRAME, f"last cue ends {cues[-1][1]:.3f}s")
    srt_text = " ".join(text for _, _, text in cues)
    narration_text = " ".join(beat["text"] for beat in schedule)
    check("srt matches narration", srt_text.split() == narration_text.split(), "word-for-word")

    lufs = integrated_loudness(FINAL_MP4)
    check("integrated loudness", None, f"{lufs} LUFS (YouTube normalises to about -14)" if lufs is not None else "not measured")

    description = DESCRIPTION_PATH.read_text(encoding="utf-8")
    listed = re.findall(r"^(\d{2}:\d{2}) (.+)$", description, re.M)
    actual = [(mmss(beat["start"]), beat["chapter_title"]) for beat in schedule if beat["chapter_start"]]
    check("youtube chapters", listed == actual, "; ".join(f"{t} {title}" for t, title in actual))
    total_minutes, total_seconds = divmod(int(round(video_duration)), 60)
    stated = re.search(r"(\d+) minutes (\d+) seconds", description)
    stated_pair = (int(stated.group(1)), int(stated.group(2))) if stated else None
    check("youtube stated length", stated_pair == (total_minutes, total_seconds), f"description says {stated_pair}, file is {total_minutes}m {total_seconds}s")

    stills = []
    for beat in schedule:
        if not beat["chapter_start"]:
            continue
        still = QA_DIR / f"chapter-{beat['chapter']:02d}.png"
        run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{beat['start'] + STILL_OFFSET:.3f}",
             "-i", str(FINAL_MP4), "-frames:v", "1", str(still)]
        )
        stills.append(still.name)
    check("chapter stills", len(stills) == len(actual), f"{len(stills)} PNGs in {QA_DIR.relative_to(ROOT)}")

    passed = all(c["status"] != "FAIL" for c in checks)
    report = {
        "result": "PASS" if passed else "FAIL",
        "video": FINAL_MP4.name,
        "captions": FINAL_SRT.name,
        "expected_duration": round(expected, 3),
        "checks": checks,
        "stills": stills,
    }
    (QA_DIR / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    rows = "\n".join(f"| {c['check']} | {c['status']} | {c['detail']} |" for c in checks)
    (QA_DIR / "report.md").write_text(
        f"# QA report: {report['result']}\n\n"
        f"- Video: `{FINAL_MP4.name}`\n- Captions: `{FINAL_SRT.name}`\n- Expected duration: {expected:.3f}s\n\n"
        f"| Check | Status | Detail |\n|---|---|---|\n{rows}\n\n"
        "## Chapter stills\n\n" + "\n".join(f"![{name}]({name})" for name in stills) + "\n",
        encoding="utf-8",
    )
    for c in checks:
        print(f"  [{c['status']}] {c['check']}: {c['detail']}")
    print(f"QA {report['result']} -> {(QA_DIR / 'report.md').relative_to(ROOT)}")
    return passed


def main() -> int:
    parser = argparse.ArgumentParser(description="Render, mux, caption, and QA the ADK explainer.")
    for step in ("render", "stitch", "mux", "srt", "qa"):
        parser.add_argument(f"--skip-{step}", action="store_true", help=f"skip the {step} step")
    args = parser.parse_args()

    schedule = beat_schedule()
    if not args.skip_render:
        step_render()
    if not args.skip_stitch:
        step_stitch(schedule)
    if not args.skip_mux:
        step_mux()
    if not args.skip_srt:
        step_srt(schedule)
    if not args.skip_qa:
        return 0 if step_qa(schedule) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
