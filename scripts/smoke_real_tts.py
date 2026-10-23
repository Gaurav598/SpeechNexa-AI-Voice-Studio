"""Offline, real KittenTTS API smoke test. No model weights are downloaded.

Run with the project venv after installing KittenML/kitten-tts-mini-0.8:
    .venv/bin/python scripts/smoke_real_tts.py \
        --hf-home /path/to/existing/huggingface/cache \
        --output /tmp/speechnexa-smoke.wav
"""

from __future__ import annotations

import argparse
from io import BytesIO
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time

import httpx
import numpy as np
import soundfile as sf
from huggingface_hub import hf_hub_download


ROOT = Path(__file__).resolve().parents[1]
MODEL = "KittenML/kitten-tts-mini-0.8"
TEXT = "SpeechNexa generates real speech locally."


def _port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _model_ready(hf_home: Path) -> str:
    os.environ["HF_HOME"] = str(hf_home)
    os.environ["HF_HUB_OFFLINE"] = "1"
    cache = str(hf_home / "hub")
    config = Path(hf_hub_download(MODEL, "config.json", cache_dir=cache, local_files_only=True))
    import json

    metadata = json.loads(config.read_text())
    for name in (metadata["model_file"], metadata["voices"]):
        hf_hub_download(MODEL, name, cache_dir=cache, local_files_only=True)
    return config.parent.name


def run(hf_home: Path, output: Path) -> dict:
    revision = _model_ready(hf_home)
    with tempfile.TemporaryDirectory(prefix="speechnexa-smoke-") as tmp:
        root = Path(tmp)
        data_dir = root / "data"
        watermark_cache = root / "audioseal-cache"
        watermark_cache.mkdir()
        log_path = root / "backend.log"
        port = _port()
        env = os.environ.copy()
        env.update(
            {
                "HF_HOME": str(hf_home),
                "HF_HUB_OFFLINE": "1",
                "HF_HUB_DISABLE_TELEMETRY": "1",
                "AUDIOSEAL_CACHE_DIR": str(watermark_cache),
                "OMNIVOICE_DATA_DIR": str(data_dir),
                "OMNIVOICE_TTS_BACKEND": "kittentts",
                "OMNIVOICE_PORT": str(port),
                "PYTHONPATH": str(ROOT / "backend"),
            }
        )
        with log_path.open("w+") as log:
            process = subprocess.Popen(
                [sys.executable, str(ROOT / "backend" / "main.py")],
                cwd=ROOT,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
            try:
                with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=120) as client:
                    deadline = time.monotonic() + 120
                    while time.monotonic() < deadline:
                        if process.poll() is not None:
                            raise RuntimeError(f"backend exited with {process.returncode}")
                        try:
                            if client.get("/health", timeout=2).status_code == 200:
                                break
                        except httpx.HTTPError:
                            pass
                        time.sleep(0.5)
                    else:
                        raise TimeoutError("FastAPI did not become healthy in 120 seconds")

                    started = time.monotonic()
                    response = client.post(
                        "/generate",
                        files={
                            "text": (None, TEXT),
                            "engine": (None, "kittentts"),
                            "preset_voice": (None, "expr-voice-2-f"),
                            "language": (None, "en"),
                        },
                    )
                    response.raise_for_status()
                    latency = time.monotonic() - started
                    audio_id = response.headers["x-audio-id"]
                    job_id = response.headers["x-job-id"]
                    waveform, rate = sf.read(BytesIO(response.content), always_2d=True)
                    duration = len(waveform) / rate
                    rms = float(np.sqrt(np.mean(waveform * waveform)))
                    if rate != 24000 or waveform.shape[1] != 1 or duration < 0.1 or rms < 0.001:
                        raise AssertionError("invalid or silent KittenTTS WAV")
                    if not response.content.startswith(b"RIFF"):
                        raise AssertionError("response is not a WAV file")

                    history = client.get("/history")
                    history.raise_for_status()
                    if not any(row["id"] == audio_id for row in history.json()):
                        raise AssertionError("generated take missing from history")
                    fetched = client.get(f"/audio/{audio_id}.wav")
                    fetched.raise_for_status()
                    if fetched.content != response.content:
                        raise AssertionError("retrieved WAV differs from generated WAV")
                    job = client.get(f"/jobs/{job_id}")
                    job.raise_for_status()
                    if job.json().get("status") != "done":
                        raise AssertionError("generation job was not durably completed")
                    saved = data_dir / "outputs" / f"{audio_id}.wav"
                    if saved.read_bytes() != response.content:
                        raise AssertionError("stored WAV differs from generated WAV")
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(response.content)
            finally:
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                log.flush()

        with sqlite3.connect(data_dir / "omnivoice.db") as conn:
            persisted = conn.execute(
                "SELECT audio_path FROM generation_history WHERE id=?", (audio_id,)
            ).fetchone()
            persisted_job = conn.execute(
                "SELECT status FROM jobs WHERE id=?", (job_id,)
            ).fetchone()
        if persisted != (f"{audio_id}.wav",):
            raise AssertionError("generation history was not durably registered")
        if persisted_job != ("done",):
            raise AssertionError("generation job was not durably completed")
        if any(watermark_cache.rglob("*")):
            raise AssertionError("AudioSeal wrote to its empty cache during offline generation")
        logs = log_path.read_text(errors="replace")
        if "Downloading:" in logs or "generator_base.pth" in logs:
            raise AssertionError("an unexpected checkpoint download was attempted")
        return {
            "engine": "kittentts",
            "model": MODEL,
            "revision": revision,
            "audio_id": audio_id,
            "job_id": job_id,
            "sample_rate": rate,
            "duration_s": round(duration, 3),
            "rms": round(rms, 4),
            "api_latency_s": round(latency, 3),
            "output": str(output),
            "audioseal_download": False,
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hf-home", type=Path, required=True, help="existing HF cache")
    parser.add_argument("--output", type=Path, required=True, help="WAV export path")
    args = parser.parse_args()
    import json

    print(json.dumps(run(args.hf_home, args.output), indent=2))
