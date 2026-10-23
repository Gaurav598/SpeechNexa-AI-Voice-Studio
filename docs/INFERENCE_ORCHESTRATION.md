# Inference orchestration

`backend/services/model_manager.py` owns the bounded GPU executor. `run_on_gpu_pool_guarded` applies queue and execution timeouts, cancellation cleanup and the existing pool recovery path. The added `_GpuMemoryReservations` admits jobs in FIFO order when CUDA reports free dedicated VRAM and a requested reservation fits. `backend/services/gpu_gateway.py` forwards the resource request. On MPS or unknown VRAM, dedicated capacity is not reliably measurable, so the memory reservation is advisory and the worker count remains the hard concurrency bound. This is scheduling, not GPU preemption.

The active `POST /generate` route creates a `speech_generate` row after validation and prewarming. Guarded transitions in `backend/core/job_store.py` move it through `pending → running → post_processing → done`; failure and cancellation are terminal. Output metadata is committed with `done` only after WAV validation. Startup recovery marks interrupted active jobs failed. A response carries `X-Job-Id` for `GET /jobs/{id}`.

The API still returns a whole WAV for classic generation and NDJSON for the existing stream option. Prewarming and model installation occur before the generation job ID exists. Persistent metadata makes status and error history inspectable; queued work is not replayed after a restart. The per-job event tail is bounded in SQLite.

Offline generation uses installed models. Optional AudioSeal embedding runs only when its checkpoint is already cached or explicitly installed; missing optional watermark data never triggers an implicit checkpoint download. Synthetic audio continues through the existing `mark_synthetic` entry point.
