"""
HandFree - Speech-to-Text

A macOS Python application that uses the Fn/Globe key
to trigger fast speech-to-text transcription via Groq Whisper API.
"""

from handfree.audio_recorder import AudioRecorder
from handfree.config import Config
from handfree.exceptions import (
    HandFreeError,
    ConfigurationError,
    MuteDetectionError,
    AudioRecordingError,
    TranscriptionError,
    OutputError,
)
from handfree.mute_detector import MuteDetector
from handfree.hotkey_detector import HotkeyDetector
from handfree.output_handler import OutputHandler, get_clipboard_content
from handfree.transcriber import Transcriber

__version__ = "0.1.0"

__all__ = [
    "AudioRecorder",
    "Config",
    "HandFreeError",
    "ConfigurationError",
    "MuteDetectionError",
    "AudioRecordingError",
    "TranscriptionError",
    "OutputError",
    "MuteDetector",
    "HotkeyDetector",
    "OutputHandler",
    "get_clipboard_content",
    "Transcriber",
]
