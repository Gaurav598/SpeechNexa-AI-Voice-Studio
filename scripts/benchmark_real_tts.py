"""Measure the real offline KittenTTS API path in fresh backend processes.

Each sample uses the same isolated smoke test, so it includes request-time
model loading, inference, encoding and persistence, but excludes server startup.
This is an API latency measure; it is not an inference-only real-time factor.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from smoke_real_tts import run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hf-home", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.samples <= 20:
        parser.error("--samples must be between 1 and 20")

    results = []
    for index in range(args.samples):
        sample = run(args.hf_home, args.output_dir / f"sample-{index + 1}.wav")
        sample["api_latency_per_audio_second"] = round(
            sample["api_latency_s"] / sample["duration_s"], 3
        )
        results.append(sample)
    latencies = sorted(item["api_latency_s"] for item in results)
    print(json.dumps({
        "measurement": "fresh-process request latency; backend startup excluded",
        "samples": results,
        "median_api_latency_s": latencies[len(latencies) // 2],
    }, indent=2))


if __name__ == "__main__":
    main()
