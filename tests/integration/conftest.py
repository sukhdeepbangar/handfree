"""Integration test fixtures."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def audio_fixtures_dir() -> Path:
    """Path to audio fixtures directory."""
    return Path(__file__).parent.parent / "fixtures" / "audio"


@pytest.fixture
def fixture_manifest(audio_fixtures_dir):
    """Load fixture manifest."""
    manifest_path = audio_fixtures_dir / "manifest.json"
    if manifest_path.exists():
        return json.loads(manifest_path.read_text())
    return {"fixtures": []}


@pytest.fixture
def get_fixture_path(audio_fixtures_dir):
    """Get a fixture file path by name."""
    def _get(filename: str) -> Path:
        return audio_fixtures_dir / filename
    return _get
