# SpeechNexa

**SpeechNexa — AI Voice Generation & Speech Studio** is a local-first Electron and FastAPI application for speech generation and related audio workflows. It is an [AGPL-3.0-only](LICENSE) derivative of [VoiceStudio](UPSTREAM.md). Speech engines and weights retain their own authors and licenses.

> Migration in progress. The locally verified speech path is English text-to-speech with KittenTTS on an Apple M4 Mac. See [implementation status](docs/IMPLEMENTATION_STATUS.md) for exact tests, publication state, and remaining gaps. Other inherited engines and platforms require separate installation and verification.

## Supported path

- Electron studio with text entry, engine readiness, preset voices, generation progress, cancellation controls, take history, WAV playback and export.
- FastAPI speech generation and audio retrieval on loopback, with SQLite generation history.
- Real KittenTTS inference through `POST /generate`: 24 kHz mono WAV generated, saved, retrieved and decoded in an offline smoke test.
- Shared GPU worker path with bounded execution and memory reservations when dedicated VRAM can be measured. Unknown VRAM remains advisory; no GPU preemption is claimed.
- Optional AudioSeal watermarking uses an already installed checkpoint. Ordinary offline synthesis does not fetch it.

The imported application includes other workflows (cloning, dictation, dubbing, audiobooks, and more engines). Their availability depends on each engine and model installation. This migration has not verified every combination. The inherited [feature catalog](docs/feature-catalog.md) inventories those paths; it is not a SpeechNexa acceptance-test list.

## Local setup

Requirements for the verified source workflow: Python 3.11, [uv](https://docs.astral.sh/uv/), Bun matching `package.json`, and a system able to run the existing KittenTTS ONNX CPU adapter. The smoke test used an Apple M4 Mac with 16 GB RAM. No cloud API key is required.

```bash
git clone https://github.com/Gaurav598/SpeechNexa-AI-Voice-Studio.git
cd SpeechNexa-AI-Voice-Studio
uv sync --locked --python 3.11
bun install --frozen-lockfile
```

Install the small KittenTTS model only after reviewing its [model card](https://huggingface.co/KittenML/kitten-tts-mini-0.8) and the [model licensing notes](docs/MODEL_LICENSING.md). This explicit download goes into your local Hugging Face cache; weights are not stored in this repository.

```bash
uv run python -c 'from huggingface_hub import snapshot_download; snapshot_download("KittenML/kitten-tts-mini-0.8", revision="c02725660cea441db4c383af69f1f26f5cd00947")'
```

Start the backend and Electron studio in separate terminals:

```bash
OMNIVOICE_TTS_BACKEND=kittentts HF_HUB_OFFLINE=1 uv run python backend/main.py
bun run dev:desktop
```

The backend listens on `127.0.0.1:3900` by default. In the studio, enter English text, choose KittenTTS and a preset voice, generate, then play or export the WAV from the take panel. Existing `OMNIVOICE_*` settings remain compatibility aliases while the imported backend is migrated; new project-owned settings use `SPEECHNEXA_*` where implemented.

### API example

```bash
curl --fail-with-body -o speech.wav \
  -F 'text=SpeechNexa generates speech locally.' \
  -F 'engine=kittentts' \
  -F 'preset_voice=expr-voice-2-f' \
  -F 'language=en' \
  http://127.0.0.1:3900/generate
```

The response is a WAV file. Its `X-Audio-Id` header identifies the persisted take, and `X-Job-Id` identifies its job. `GET /history` lists recent takes, `GET /audio/<id>.wav` retrieves the saved bytes, and `GET /jobs/<id>` shows the job state. API docs are available at `/docs` while the backend runs. Loopback binding is the safe default; public exposure needs separate authentication and network review.

## Verify real speech

After installing the model, run the real offline API smoke test. It starts a temporary backend and database, generates speech through FastAPI, checks the waveform and history, verifies byte identical export, and confirms the optional AudioSeal checkpoint was not downloaded:

```bash
uv run python scripts/smoke_real_tts.py \
  --hf-home "${HF_HOME:-$HOME/.cache/huggingface}" \
  --output /tmp/speechnexa-smoke.wav
```

Play the output file with your system audio player. This test uses the real model and is separate from deterministic CI adapters. It requires an installed KittenTTS model and never installs one itself.

For repeated fresh-process API measurements, run `uv run python scripts/benchmark_real_tts.py --hf-home "${HF_HOME:-$HOME/.cache/huggingface}" --output-dir /tmp/speechnexa-benchmark --samples 3`. See [performance notes](docs/performance.md) for what the timing includes.

```bash
HF_HUB_OFFLINE=1 HF_HUB_CACHE=/tmp/speechnexa-empty-cache uv run pytest -q tests/test_watermark_offline_checkpoint.py
bun run --cwd electron typecheck
bun run --cwd electron test
bun run --cwd electron build
bun run --cwd electron build:web
```

## Architecture and scope

The React renderer calls FastAPI. The backend validates requests and engine licenses, selects an installed adapter, coordinates model and worker resources, runs inference, validates and stores audio, and exposes history and retrieval. See [architecture](docs/ARCHITECTURE.md), [inference orchestration](docs/INFERENCE_ORCHESTRATION.md), [API](docs/API.md), and [testing](docs/TESTING.md).

The active desktop and web UI is Electron. Inherited native iOS and Android projects are separate source trees and outside this verified first release. Publishing, stores, Docker releases, and upstream account services are disabled until independently configured and tested.

## Licensing and security

Application source stays AGPL-3.0-only, including its network source-sharing obligations. [UPSTREAM.md](UPSTREAM.md) records provenance; [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [docs/MODEL_LICENSING.md](docs/MODEL_LICENSING.md) describe separate code and model terms. Review applicable terms before commercial use or redistribution. Downloaded model weights, generated audio and personal recordings are excluded from Git.

The default application is local-first. Model installation is explicit; inherited account, analytics and update integrations are disabled or gated for SpeechNexa. See [security notes](docs/SECURITY.md) and [current limitations](docs/IMPLEMENTATION_STATUS.md).
