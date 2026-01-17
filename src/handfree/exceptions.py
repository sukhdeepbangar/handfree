"""
Custom Exceptions for HandFree application.

This module defines the exception hierarchy used throughout the application.
"""


class HandFreeError(Exception):
    """Base exception for all HandFree errors."""
    pass


class ConfigurationError(HandFreeError):
    """Error in application configuration."""
    pass


class MuteDetectionError(HandFreeError):
    """Error detecting mute state from AirPods."""
    pass


class AudioRecordingError(HandFreeError):
    """Error recording audio from microphone."""
    pass


class TranscriptionError(HandFreeError):
    """Error transcribing audio via API."""
    pass


class OutputError(HandFreeError):
    """Error outputting text to clipboard or active application."""
    pass


class PermissionError(HandFreeError):
    """Error related to missing system permissions."""
    pass
