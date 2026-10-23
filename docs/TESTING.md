# Testing

Use an empty Hugging Face cache for deterministic tests so a developer's downloaded models do not mask missing-install behavior:

```bash
HF_HUB_OFFLINE=1 HF_HUB_CACHE=/tmp/speechnexa-empty-hf \
  uv run pytest -q tests/test_watermark_offline_checkpoint.py \
  tests/test_generate_streaming.py tests/test_job_store.py \
  tests/test_gpu_memory_reservations.py tests/test_task_admission.py
python scripts/check_migration_safety.py
python scripts/check_model_licenses.py
bun run --cwd electron typecheck
bun run --cwd electron locale:check
bun run --cwd electron test
bun run --cwd electron build
bun run --cwd electron build:web
```

The real model test is separate from CI and requires an explicitly installed KittenTTS snapshot:

```bash
uv run python scripts/smoke_real_tts.py \
  --hf-home "${HF_HOME:-$HOME/.cache/huggingface}" \
  --output /tmp/speechnexa-smoke.wav
```

It starts a temporary backend, runs actual inference, decodes the output WAV, checks a non-silent 24 kHz mono waveform, retrieves identical bytes, checks history and the durable job, and verifies an empty AudioSeal cache. It needs a local loopback socket. CI uses model-free tests; the smoke is an explicit local acceptance gate. Exact results and limitations are in [implementation status](IMPLEMENTATION_STATUS.md).
