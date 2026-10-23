# Local API

FastAPI serves `/docs` on the local backend while running. The verified text-to-speech request is multipart `POST /generate` with `text`, `engine=kittentts`, `preset_voice=expr-voice-2-f` and `language=en`. It returns a complete WAV body for the classic path. The `X-Audio-Id` header identifies the stored take; `X-Job-Id` identifies its persisted job.

```bash
curl --fail-with-body -D /tmp/speechnexa-headers.txt -o /tmp/speechnexa.wav \
  -F 'text=SpeechNexa generates speech locally.' \
  -F 'engine=kittentts' -F 'preset_voice=expr-voice-2-f' -F 'language=en' \
  http://127.0.0.1:3900/generate
```

Read `GET /history`, `GET /audio/{audio_id}.wav`, `GET /jobs/{job_id}` and `GET /jobs/{job_id}/events?after_seq=0` to inspect takes and job metadata. `GET /health` checks backend reachability. Streaming generation uses the same `/generate` route with the imported NDJSON request option; its terminal frame and `X-Job-Id` should be checked before treating the take as complete.

The classic endpoint is synchronous: an HTTP timeout or disconnected client can end the request before it returns audio. Jobs record the actual request lifecycle and support restart diagnosis, but do not make a generation request resumable after a process crash. The service is intended for local loopback; do not expose it publicly without separate authentication and network review.
