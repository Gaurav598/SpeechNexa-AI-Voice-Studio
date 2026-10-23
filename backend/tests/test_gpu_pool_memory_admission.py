"""Per-job GPU reservations follow the underlying worker, not its caller."""

from __future__ import annotations

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest


@pytest.mark.asyncio
async def test_known_vram_budget_serializes_jobs_without_rejecting_lone_job(monkeypatch):
    from services import model_manager as mm

    monkeypatch.setattr(mm, "_probe_free_vram_gb", lambda: 6.0, raising=False)
    started = threading.Event()
    release = threading.Event()
    second_ran = threading.Event()
    cleaned = threading.Event()

    def hold():
        started.set()
        assert release.wait(2)

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = asyncio.create_task(mm.run_on_gpu_pool_guarded(
            hold, executor=executor, min_vram_gb=4, timeout=1,
        ))
        try:
            assert await asyncio.to_thread(started.wait, 1)
            with pytest.raises(mm.GpuPoolBusyError, match="memory"):
                await mm.run_on_gpu_pool_guarded(
                    second_ran.set, executor=executor, min_vram_gb=4,
                    queue_timeout=0.05, timeout=1, on_abandon=cleaned.set,
                )
            assert cleaned.is_set()
            assert not second_ran.is_set()
        finally:
            release.set()
            await first

        await mm.run_on_gpu_pool_guarded(
            second_ran.set, executor=executor, min_vram_gb=4, timeout=1,
        )
        assert second_ran.is_set()


@pytest.mark.asyncio
async def test_cancelled_caller_keeps_reservation_until_worker_finishes(monkeypatch):
    from services import model_manager as mm

    monkeypatch.setattr(mm, "_probe_free_vram_gb", lambda: 6.0, raising=False)
    started = threading.Event()
    release = threading.Event()
    cleaned = threading.Event()

    def hold():
        started.set()
        assert release.wait(2)

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = asyncio.create_task(mm.run_on_gpu_pool_guarded(
            hold, executor=executor, min_vram_gb=4,
            timeout=1, on_abandon=cleaned.set,
        ))
        try:
            assert await asyncio.to_thread(started.wait, 1)
            first.cancel()
            assert isinstance((await asyncio.gather(first, return_exceptions=True))[0], asyncio.CancelledError)
            assert not cleaned.is_set()
            with pytest.raises(mm.GpuPoolBusyError, match="memory"):
                await mm.run_on_gpu_pool_guarded(
                    lambda: None, executor=executor, min_vram_gb=4,
                    queue_timeout=0.05, timeout=1,
                )
        finally:
            release.set()
            assert await asyncio.to_thread(cleaned.wait, 1)

        await mm.run_on_gpu_pool_guarded(
            lambda: None, executor=executor, min_vram_gb=4, timeout=1,
        )


@pytest.mark.asyncio
async def test_cancelled_pool_queue_entry_releases_its_reservation(monkeypatch):
    from services import model_manager as mm

    monkeypatch.setattr(mm, "_probe_free_vram_gb", lambda: 6.0, raising=False)
    hog_started = threading.Event()
    release_hog = threading.Event()
    cleaned = threading.Event()

    def hog():
        hog_started.set()
        assert release_hog.wait(2)

    with ThreadPoolExecutor(max_workers=1) as executor:
        hog_future = executor.submit(hog)
        assert hog_started.wait(1)
        queued = asyncio.create_task(mm.run_on_gpu_pool_guarded(
            lambda: None, executor=executor, min_vram_gb=4,
            queue_timeout=1, timeout=1, on_abandon=cleaned.set,
        ))
        try:
            await asyncio.sleep(0.05)
            queued.cancel()
            assert isinstance((await asyncio.gather(queued, return_exceptions=True))[0], asyncio.CancelledError)
            assert cleaned.is_set()
        finally:
            release_hog.set()
            hog_future.result(timeout=1)

        await mm.run_on_gpu_pool_guarded(
            lambda: None, executor=executor, min_vram_gb=4,
            queue_timeout=0.2, timeout=1,
        )
