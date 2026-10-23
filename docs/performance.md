# Performance measurements

The imported VoiceStudio performance guide is retained as [historical reference](archive/voicestudio-performance.md); its measurements and tuning advice have not been revalidated for SpeechNexa.

Run the real offline benchmark only after explicitly installing the KittenTTS snapshot:

```bash
uv run python scripts/benchmark_real_tts.py \
  --hf-home "${HF_HOME:-$HOME/.cache/huggingface}" \
  --output-dir /tmp/speechnexa-benchmark --samples 3
```

Each sample starts a fresh backend and times one `POST /generate`. The reported API latency includes request-time model loading, inference, encoding and persistence but excludes backend startup. The script also reports audio duration and API latency per audio second. That ratio is **not** inference-only real-time factor; inference-only RTF would require a separate measurement of the model call divided by generated audio duration. Samples are real WAV files and can be played or inspected.

On an Apple M4 MacBook Air with 16 GB RAM, one offline KittenTTS API smoke on 2026-10-23 produced 3.939 seconds of 24 kHz mono audio in 4.218 seconds of API time. This is one observation, not a controlled comparison or cross-platform claim. GPU acceleration was not used by this ONNX CPU adapter. Queue, cancellation and engine-specific throughput need separate workload measurements.
