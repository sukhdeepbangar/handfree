"""Tests to validate audio fixtures are properly loaded (via Git LFS)."""

import pytest
from pathlib import Path
from scipy.io import wavfile


@pytest.mark.integration
class TestAudioFixturesValidation:
    """Verify audio fixtures are real WAV files, not LFS pointer files."""

    def test_hello_world_is_valid_wav(self, audio_fixtures_dir):
        """hello_world.wav should be a valid WAV file."""
        wav_path = audio_fixtures_dir / "hello_world.wav"
        if not wav_path.exists():
            pytest.skip("hello_world.wav not found")

        # Check file starts with RIFF header (not LFS pointer text)
        content = wav_path.read_bytes()
        assert content[:4] == b'RIFF', (
            "File does not have RIFF header. "
            "This may indicate Git LFS is not properly configured. "
            "Run: git lfs pull"
        )

        # Verify it can be read as WAV
        rate, data = wavfile.read(str(wav_path))
        assert rate == 16000, f"Expected 16kHz sample rate, got {rate}"
        assert len(data) > 0, "WAV file has no audio data"

    def test_silence_is_valid_wav(self, audio_fixtures_dir):
        """silence.wav should be a valid WAV file."""
        wav_path = audio_fixtures_dir / "silence.wav"
        if not wav_path.exists():
            pytest.skip("silence.wav not found")

        content = wav_path.read_bytes()
        assert content[:4] == b'RIFF', (
            "File does not have RIFF header. "
            "Run: git lfs pull"
        )

        rate, data = wavfile.read(str(wav_path))
        assert rate == 16000

    def test_all_manifest_fixtures_are_valid(self, audio_fixtures_dir, fixture_manifest):
        """All fixtures listed in manifest.json should be valid WAV files."""
        if not fixture_manifest.get("fixtures"):
            pytest.skip("No fixtures in manifest")

        for fixture in fixture_manifest["fixtures"]:
            filename = fixture["filename"]
            wav_path = audio_fixtures_dir / filename

            if not wav_path.exists():
                continue  # Skip missing fixtures

            content = wav_path.read_bytes()
            assert content[:4] == b'RIFF', (
                f"{filename} is not a valid WAV file. "
                "If using Git LFS, run: git lfs pull"
            )

            rate, data = wavfile.read(str(wav_path))
            expected_rate = fixture.get("sample_rate", 16000)
            assert rate == expected_rate, (
                f"{filename}: Expected {expected_rate}Hz, got {rate}Hz"
            )

    def test_fixture_durations_match_manifest(self, audio_fixtures_dir, fixture_manifest):
        """Audio file durations should approximately match manifest declarations."""
        if not fixture_manifest.get("fixtures"):
            pytest.skip("No fixtures in manifest")

        for fixture in fixture_manifest["fixtures"]:
            filename = fixture["filename"]
            wav_path = audio_fixtures_dir / filename

            if not wav_path.exists():
                continue

            rate, data = wavfile.read(str(wav_path))
            actual_duration = len(data) / rate
            expected_duration = fixture.get("duration_sec", 0)

            # Allow 0.5 second tolerance
            assert abs(actual_duration - expected_duration) < 0.5, (
                f"{filename}: Expected ~{expected_duration}s, got {actual_duration:.2f}s"
            )


@pytest.mark.integration
class TestGitLFSPointerDetection:
    """Detect if files are Git LFS pointers instead of real content."""

    LFS_POINTER_PREFIX = b"version https://git-lfs.github.com"

    def test_wav_files_are_not_lfs_pointers(self, audio_fixtures_dir):
        """Ensure .wav files are actual audio, not Git LFS pointer text."""
        wav_files = list(audio_fixtures_dir.glob("*.wav"))
        if not wav_files:
            pytest.skip("No .wav files found")

        for wav_file in wav_files:
            content = wav_file.read_bytes()

            # LFS pointer files start with "version https://git-lfs.github.com"
            is_lfs_pointer = content.startswith(self.LFS_POINTER_PREFIX)
            assert not is_lfs_pointer, (
                f"{wav_file.name} is a Git LFS pointer file, not actual audio. "
                "Please run 'git lfs pull' to download the actual files."
            )
