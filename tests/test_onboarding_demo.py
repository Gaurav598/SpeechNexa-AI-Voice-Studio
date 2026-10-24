"""Legacy demo audio must not be installed or overwrite existing user data."""

import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

import core.onboarding as onboarding  # noqa: E402


def _database(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE voice_profiles (id TEXT PRIMARY KEY, name TEXT, "
        "ref_audio_path TEXT, ref_text TEXT DEFAULT '', description TEXT DEFAULT '', "
        "is_demo INTEGER DEFAULT 0)"
    )
    conn.commit()
    return conn


def _prepare_legacy_seed(monkeypatch, db_path: Path, voices_dir: Path, clip: Path) -> None:
    """Supply a valid legacy seed fixture so an accidental reseed would run."""
    monkeypatch.setattr(onboarding, "get_db", lambda: sqlite3.connect(db_path), raising=False)
    monkeypatch.setattr(onboarding, "VOICES_DIR", str(voices_dir), raising=False)
    monkeypatch.setattr(onboarding, "_DEMO_AUDIO", str(clip), raising=False)
    monkeypatch.setattr(onboarding, "DEMO_PROFILE_ID", "demo0001", raising=False)
    clip.write_bytes(b"historical demo recording")


def test_first_run_does_not_install_legacy_demo(tmp_path, monkeypatch):
    db_path = tmp_path / "profiles.db"
    _database(db_path).close()
    voices_dir = tmp_path / "voices"
    _prepare_legacy_seed(monkeypatch, db_path, voices_dir, tmp_path / "demo.wav")

    onboarding.seed_sample_project()

    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM voice_profiles").fetchone()[0] == 0
    assert not voices_dir.exists()


def test_existing_demo_profile_and_recording_are_untouched(tmp_path, monkeypatch):
    db_path = tmp_path / "profiles.db"
    conn = _database(db_path)
    conn.execute(
        "INSERT INTO voice_profiles (id, name, ref_audio_path, ref_text, description, is_demo) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("demo0001", "User's saved demo", "demo0001.wav", "User transcript", "User note", 1),
    )
    conn.commit()
    conn.close()
    voices_dir = tmp_path / "voices"
    voices_dir.mkdir()
    user_audio = voices_dir / "demo0001.wav"
    user_audio.write_bytes(b"user audio")
    _prepare_legacy_seed(monkeypatch, db_path, voices_dir, tmp_path / "demo.wav")

    onboarding.seed_sample_project()

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT name, ref_audio_path, ref_text, description, is_demo "
            "FROM voice_profiles WHERE id='demo0001'"
        ).fetchone()
    assert row == ("User's saved demo", "demo0001.wav", "User transcript", "User note", 1)
    assert user_audio.read_bytes() == b"user audio"
