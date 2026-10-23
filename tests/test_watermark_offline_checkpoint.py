"""An optional watermark must not turn offline speech into a model download."""

from __future__ import annotations

import importlib

import torch


def test_uncached_audioseal_never_loads_on_synthetic_audio(monkeypatch):
    watermark = importlib.import_module("services.watermark")
    calls: list[str] = []
    monkeypatch.setattr(watermark, "is_enabled", lambda: True)
    monkeypatch.setattr(watermark, "_check_available", lambda: True)
    monkeypatch.setattr(watermark, "_generator_checkpoint_cached", lambda: False)
    monkeypatch.setattr(watermark, "_generator", None)
    monkeypatch.setattr(
        watermark, "_get_generator", lambda: calls.append("download attempted")
    )

    source = torch.ones(24000)
    assert watermark.will_mark() is False
    assert watermark.embed_watermark(source, 24000) is source
    assert calls == []
