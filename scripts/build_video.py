"""Mux actual browser footage with original local TTS narration. Output is exactly 105 s."""

import json
import re
import subprocess
import wave
from pathlib import Path

import imageio_ffmpeg


def main():
    root = Path(__file__).resolve().parents[1]
    segments = json.loads((root / "demos/narration-segments.json").read_text())
    meta = json.loads((root / "demos/capture-metadata.json").read_text())
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(),
        "-y",
        "-ss",
        str(meta["trim_start_seconds"]),
        "-i",
        str(root / "demos/matchweave-screen-recording.webm"),
    ]
    filters = []
    for i, segment in enumerate(segments):
        audio = root / "runtime/narration" / f"segment-{i:02d}.wav"
        with wave.open(str(audio)) as wav:
            duration = wav.getnframes() / wav.getframerate()
        tempo = max(1, duration / (segment["duration"] - 0.15))
        command += ["-i", str(audio)]
        filters.append(
            f"[{i + 1}:a]atempo={tempo:.6f},apad,atrim=duration={segment['duration']},asetpts=PTS-STARTPTS[a{i}]"
        )
    filters.append("".join(f"[a{i}]" for i in range(len(segments))) + f"concat=n={len(segments)}:v=0:a=1[a]")
    output = root / "demos/matchweave-demo.mp4"
    command += [
        "-filter_complex",
        ";".join(filters),
        "-map",
        "0:v:0",
        "-map",
        "[a]",
        "-t",
        "105",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "22",
        "-pix_fmt",
        "yuv420p",
        "-r",
        "30",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(command, check=True, capture_output=True)
    probe = subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(output)], check=False, capture_output=True, text=True
    )
    duration = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", probe.stderr)
    if not duration:
        raise RuntimeError("Cannot verify final video duration")
    hours, minutes, seconds = map(float, duration.groups())
    total = hours * 3600 + minutes * 60 + seconds
    assert 104.9 <= total <= 105.1 and total < 120
    report = {
        "file": str(output.relative_to(root)),
        "duration_seconds": total,
        "bytes": output.stat().st_size,
        "video": "Actual working browser recording, H.264, 1600x900, 30 fps",
        "audio": "Original narration synthesized locally using Windows System.Speech; no music",
        "public_url": None,
        "portal_submitted": False,
    }
    (root / "docs/reports/video.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

    def stamp(t):
        return f"00:{int(t) // 60:02d}:{int(t) % 60:02d},000"

    (root / "demos/captions.srt").write_text(
        "\n\n".join(
            f"{i + 1}\n{stamp(s['start'])} --> {stamp(s['start'] + s['duration'])}\n{s['text']}"
            for i, s in enumerate(segments)
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
