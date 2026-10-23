"""Measured VRAM reservations follow real GPU-pool work until its thread exits."""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from services import model_manager as mm


async def _until(predicate, timeout=2.0):
    deadline = asyncio.get_running_loop().time() + timeout
    while not predicate():
        assert asyncio.get_running_loop().time() < deadline
        await asyncio.sleep(0.01)


@pytest.mark.asyncio
async def test_overlapping_jobs_wait_for_measured_memory(monkeypatch):
    monkeypatch.setattr(mm, "_probe_free_vram_gb", lambda: 6.0)
    ex = ThreadPoolExecutor(max_workers=2)
    first_started = threading.Event()
    release_first = threading.Event()
    second_started = threading.Event()

    def first():
        first_started.set()
        release_first.wait(3)
        return "first"

    def second():
        second_started.set()
        return "second"

    try:
        a = asyncio.create_task(mm.run_on_gpu_pool_guarded(
            first, executor=ex, timeout=3, queue_timeout=3, min_vram_gb=4))
        await _until(first_started.is_set)
        b = asyncio.create_task(mm.run_on_gpu_pool_guarded(
            second, executor=ex, timeout=3, queue_timeout=3, min_vram_gb=4))
        await _until(lambda: mm.gpu_pool_stats(ex)["memory_waiting"] == 1)
        assert not second_started.is_set()
        assert mm.gpu_pool_stats(ex)["memory_reserved_gb"] == 4
        release_first.set()
        assert await asyncio.wait_for(a, 3) == "first"
        assert await asyncio.wait_for(b, 3) == "second"
        assert mm.gpu_pool_stats(ex)["memory_reserved_gb"] == 0
    finally:
        release_first.set()
        ex.shutdown(wait=True)


@pytest.mark.asyncio
async def test_cancelled_waiter_releases_fifo_place(monkeypatch):
    monkeypatch.setattr(mm, "_probe_free_vram_gb", lambda: 6.0)
    ex = ThreadPoolExecutor(max_workers=2)
    release_first = threading.Event()
    started = threading.Event()
    smaller_started = threading.Event()
    try:
        first = asyncio.create_task(mm.run_on_gpu_pool_guarded(
            lambda: (started.set(), release_first.wait(3)),
            executor=ex, timeout=3, queue_timeout=3, min_vram_gb=4))
        await _until(started.is_set)
        second = asyncio.create_task(mm.run_on_gpu_pool_guarded(
            lambda: "large", executor=ex, timeout=3, queue_timeout=3,
            min_vram_gb=4))
        await _until(lambda: mm.gpu_pool_stats(ex)["memory_waiting"] == 1)
        third = asyncio.create_task(mm.run_on_gpu_pool_guarded(
            lambda: smaller_started.set(), executor=ex, timeout=3,
            queue_timeout=3, min_vram_gb=2))
        await _until(lambda: mm.gpu_pool_stats(ex)["memory_waiting"] == 2)
        assert not smaller_started.is_set()  # FIFO, despite 2 GB headroom.
        second.cancel()
        with pytest.raises(asyncio.CancelledError):
            await second
        await _until(smaller_started.is_set)
        await third
        assert mm.gpu_pool_stats(ex)["memory_waiting"] == 0
        release_first.set()
        await first
    finally:
        release_first.set()
        ex.shutdown(wait=True)


@pytest.mark.asyncio
async def test_running_thread_keeps_lease_after_caller_cancel(monkeypatch):
    monkeypatch.setattr(mm, "_probe_free_vram_gb", lambda: 6.0)
    ex = ThreadPoolExecutor(max_workers=2)
    release_first = threading.Event()
    started = threading.Event()
    cleanup = threading.Event()
    next_started = threading.Event()
    try:
        first = asyncio.create_task(mm.run_on_gpu_pool_guarded(
            lambda: (started.set(), release_first.wait(3)), executor=ex,
            timeout=3, queue_timeout=3, min_vram_gb=4,
            on_abandon=cleanup.set))
        await _until(started.is_set)
        first.cancel()
        with pytest.raises(asyncio.CancelledError):
            await first
        assert mm.gpu_pool_stats(ex)["memory_reserved_gb"] == 4
        assert not cleanup.is_set()
        second = asyncio.create_task(mm.run_on_gpu_pool_guarded(
            lambda: next_started.set(), executor=ex, timeout=3,
            queue_timeout=3, min_vram_gb=4))
        await _until(lambda: mm.gpu_pool_stats(ex)["memory_waiting"] == 1)
        assert not next_started.is_set()
        release_first.set()
        await _until(cleanup.is_set)
        await second
        assert mm.gpu_pool_stats(ex)["memory_reserved_gb"] == 0
    finally:
        release_first.set()
        ex.shutdown(wait=True)


@pytest.mark.asyncio
async def test_unknown_memory_does_not_block_supported_jobs(monkeypatch):
    monkeypatch.setattr(mm, "_probe_free_vram_gb", lambda: None)
    ex = ThreadPoolExecutor(max_workers=1)
    try:
        result = await mm.run_on_gpu_pool_guarded(
            lambda: "cpu path", executor=ex, timeout=3, queue_timeout=3,
            min_vram_gb=8)
        assert result == "cpu path"
        assert mm.gpu_pool_stats(ex)["memory_reserved_gb"] == 0
    finally:
        ex.shutdown(wait=True)


@pytest.mark.asyncio
async def test_worker_queue_timeout_releases_unstarted_lease(monkeypatch):
    monkeypatch.setattr(mm, "_probe_free_vram_gb", lambda: 6.0)
    ex = ThreadPoolExecutor(max_workers=1)
    blocker_started = threading.Event()
    unblock = threading.Event()
    ran = threading.Event()
    cleaned = threading.Event()
    try:
        ex.submit(lambda: (blocker_started.set(), unblock.wait(3)))
        await _until(blocker_started.is_set)
        with pytest.raises(mm.GpuPoolBusyError):
            await mm.run_on_gpu_pool_guarded(
                ran.set, executor=ex, timeout=3, queue_timeout=0.05,
                min_vram_gb=4, on_abandon=cleaned.set)
        assert cleaned.is_set()
        assert mm.gpu_pool_stats(ex)["memory_reserved_gb"] == 0
        unblock.set()
        await asyncio.sleep(0.05)
        assert not ran.is_set()
    finally:
        unblock.set()
        ex.shutdown(wait=True)


@pytest.mark.asyncio
async def test_submit_failure_releases_lease_and_inputs(monkeypatch):
    monkeypatch.setattr(mm, "_probe_free_vram_gb", lambda: 6.0)
    ex = ThreadPoolExecutor(max_workers=1)
    ex.shutdown(wait=True)
    cleaned = []
    with pytest.raises(RuntimeError, match="shutdown"):
        await mm.run_on_gpu_pool_guarded(
            lambda: None, executor=ex, timeout=3, queue_timeout=3,
            min_vram_gb=4, on_abandon=lambda: cleaned.append(True))
    assert cleaned == [True]
    assert mm.gpu_pool_stats(ex)["memory_reserved_gb"] == 0
