"""Task IDs are one-shot keys across the live queue and persisted history."""

import asyncio

import pytest

from core import db, job_store
from core.tasks import TaskManager


@pytest.mark.asyncio
async def test_duplicate_task_id_runs_once_and_keeps_event_history(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "jobs.db"))
    db.init_db()
    manager = TaskManager()
    calls = []

    async def work():
        calls.append("first")

    async def replacement():
        calls.append("replacement")

    assert await manager.add_task("same", "dub_generate", work) is True
    job_store.append_event("same", 'data: {"type":"progress"}\n\n')
    assert await manager.add_task("same", "dub_generate", replacement) is False
    assert manager.queue.qsize() == 1

    worker = asyncio.create_task(manager.worker())
    try:
        await asyncio.wait_for(manager.queue.join(), 2)
    finally:
        worker.cancel()
        await asyncio.gather(worker, return_exceptions=True)

    assert calls == ["first"]
    assert job_store.get("same")["status"] == "done"
    assert len(job_store.events_since("same")) == 1

    restarted_manager = TaskManager()
    assert await restarted_manager.add_task("same", "dub_generate", replacement) is False
    assert restarted_manager.queue.qsize() == 0
    assert job_store.get("same")["status"] == "done"
    assert len(job_store.events_since("same")) == 1
