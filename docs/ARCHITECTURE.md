# Architecture

The supported desktop and web interface lives in `electron/`. React sends requests to the loopback FastAPI service in `backend/main.py`. The backend selects an installed speech adapter, coordinates a bounded worker pool, validates the resulting WAV, then saves it under the application data directory and registers it in SQLite. `GET /audio/{id}.wav` and `GET /history` expose saved takes.

```text
Electron renderer → FastAPI /generate → engine adapter
                           │                 │
                           ├→ GPU pool and memory admission
                           ├→ audio validation and optional installed watermark
                           └→ SQLite jobs/history + WAV outputs
```

The imported repository also contains native iOS and Android projects, additional engines and workflows. The first migration acceptance test covers KittenTTS text-to-speech on this macOS host. Other engines and operating systems need their own verification; see [implementation status](IMPLEMENTATION_STATUS.md).

The upstream `omnivoice` Python package name and `OMNIVOICE_*` settings remain where imports and existing user data require compatibility. SpeechNexa is the active product identity. The root `package.json` remains the version source.
