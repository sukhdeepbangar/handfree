#!/usr/bin/env python
"""Generate test audio fixtures programmatically.

This module creates audio fixtures for testing without requiring external tools.
Fixtures can be generated using:
- Silence: Pure zero samples
- Noise: Low-level white noise
- Tone: Simple sine wave (fallback for TTS)
- TTS: macOS text-to-speech (if available)
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy.io import wavfile

FIXTURES_DIR = Path(__file__).parent / "audio"
SAMPLE_RATE = 16000


def generate_silence(filename: str, duration_sec: float) -> Path:
    """Generate silent audio.

    Args:
        filename: Output filename.
        duration_sec: Duration in seconds.

    Returns:
        Path to generated file.
    """
    output = FIXTURES_DIR / filename
    samples = int(SAMPLE_RATE * duration_sec)
    audio = np.zeros(samples, dtype=np.int16)
    wavfile.write(str(output), SAMPLE_RATE, audio)
    print(f"Generated: {output}")
    return output


def generate_noise(filename: str, duration_sec: float, level: float = 0.05) -> Path:
    """Generate white noise.

    Args:
        filename: Output filename.
        duration_sec: Duration in seconds.
        level: Noise level (0.0-1.0).

    Returns:
        Path to generated file.
    """
    output = FIXTURES_DIR / filename
    samples = int(SAMPLE_RATE * duration_sec)
    audio = (np.random.randn(samples) * 32767 * level).astype(np.int16)
    wavfile.write(str(output), SAMPLE_RATE, audio)
    print(f"Generated: {output}")
    return output


def generate_tone(filename: str, duration_sec: float, frequency: float = 440.0) -> Path:
    """Generate a simple tone (sine wave).

    Args:
        filename: Output filename.
        duration_sec: Duration in seconds.
        frequency: Tone frequency in Hz.

    Returns:
        Path to generated file.
    """
    output = FIXTURES_DIR / filename
    samples = int(SAMPLE_RATE * duration_sec)
    t = np.linspace(0, duration_sec, samples, dtype=np.float32)
    audio = (np.sin(2 * np.pi * frequency * t) * 16000).astype(np.int16)
    wavfile.write(str(output), SAMPLE_RATE, audio)
    print(f"Generated: {output}")
    return output


def generate_tts(filename: str, text: str, voice: str = "Alex") -> Path | None:
    """Generate audio using macOS TTS.

    Args:
        filename: Output filename.
        text: Text to speak.
        voice: macOS voice name.

    Returns:
        Path to generated file, or None if TTS unavailable.
    """
    if sys.platform != "darwin":
        print(f"TTS not available on {sys.platform}")
        return None

    output = FIXTURES_DIR / filename

    try:
        with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as tmp:
            tmp_path = tmp.name

        # Generate speech using macOS 'say' command
        subprocess.run(
            ["say", "-v", voice, "-o", tmp_path, text],
            check=True,
            capture_output=True
        )

        # Convert to 16kHz mono WAV using ffmpeg
        subprocess.run([
            "ffmpeg", "-y", "-i", tmp_path,
            "-ar", str(SAMPLE_RATE), "-ac", "1",
            str(output)
        ], check=True, capture_output=True)

        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)

        print(f"Generated: {output}")
        return output

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"TTS generation failed: {e}")
        return None


def generate_all(force: bool = False):
    """Generate all standard fixtures.

    Args:
        force: If True, regenerate all fixtures. If False, skip existing files.
    """
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Generating Audio Fixtures ===\n")

    # Generate programmatic fixtures
    if force or not (FIXTURES_DIR / "silence.wav").exists():
        print("Generating silence.wav...")
        generate_silence("silence.wav", 3.0)
    else:
        print("Skipping silence.wav (already exists)")

    if force or not (FIXTURES_DIR / "noise.wav").exists():
        print("Generating noise.wav...")
        generate_noise("noise.wav", 3.0, 0.05)
    else:
        print("Skipping noise.wav (already exists)")

    # Try TTS, fall back to tones if unavailable
    if force or not (FIXTURES_DIR / "hello_world.wav").exists():
        print("\nGenerating hello_world.wav...")
        if not generate_tts("hello_world.wav", "Hello world"):
            print("Falling back to tone...")
            generate_tone("hello_world.wav", 2.0, 440.0)
    else:
        print("Skipping hello_world.wav (already exists)")

    if force or not (FIXTURES_DIR / "short_phrase.wav").exists():
        print("\nGenerating short_phrase.wav...")
        if not generate_tts("short_phrase.wav", "This is a test"):
            print("Falling back to tone...")
            generate_tone("short_phrase.wav", 3.0, 880.0)
    else:
        print("Skipping short_phrase.wav (already exists)")

    print("\n=== Done ===")
    print(f"Fixtures directory: {FIXTURES_DIR}")


if __name__ == "__main__":
    generate_all()
