"""
Configuration Module
Loads and validates settings from environment variables.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List

from dotenv import load_dotenv


# Valid UI position values
VALID_UI_POSITIONS = ["top-center", "top-right", "top-left", "bottom-center", "bottom-right", "bottom-left"]


@dataclass
class Config:
    """Application configuration from environment variables."""

    # Required
    groq_api_key: str

    # Optional with defaults - Audio/Transcription
    language: Optional[str] = None  # Auto-detect if not set
    type_delay: float = 0.0
    sample_rate: int = 16000
    use_paste: bool = False

    # Optional with defaults - UI
    ui_enabled: bool = True
    ui_position: str = "top-center"
    history_enabled: bool = True
    history_max_entries: int = 1000

    # Optional - Custom hotkey (e.g., "ctrl+shift+r")
    custom_hotkey: Optional[str] = None

    @classmethod
    def from_env(cls) -> "Config":
        """
        Load configuration from environment variables.

        Environment Variables:
            GROQ_API_KEY: Required. Groq API key for transcription.
            HANDFREE_LANGUAGE: Optional. Language code for transcription (auto-detect if not set).
            HANDFREE_TYPE_DELAY: Optional. Delay between keystrokes in seconds (default: 0).
            HANDFREE_SAMPLE_RATE: Optional. Audio sample rate in Hz (default: 16000).
            HANDFREE_USE_PASTE: Optional. Use clipboard paste instead of typing (default: false).
            HANDFREE_UI_ENABLED: Optional. Enable visual UI indicator (default: true).
            HANDFREE_UI_POSITION: Optional. Indicator position: top-center, top-right, top-left,
                                  bottom-center, bottom-right, bottom-left (default: top-center).
            HANDFREE_HISTORY_ENABLED: Optional. Enable transcription history (default: true).
            HANDFREE_HISTORY_MAX: Optional. Maximum history entries (default: 1000).
            HANDFREE_HOTKEY: Optional. Custom hotkey (e.g., "ctrl+shift+r"). Platform default if not set.

        Returns:
            Config instance with loaded values.

        Raises:
            ValueError: If required configuration is missing.
        """
        load_dotenv()

        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is required.\n"
                "Set it in your .env file or export it:\n"
                "  export GROQ_API_KEY=your_key_here"
            )

        # Parse boolean environment variables
        def parse_bool(value: str, default: bool) -> bool:
            if not value:
                return default
            return value.lower() in ("true", "1", "yes")

        return cls(
            groq_api_key=groq_api_key,
            language=os.environ.get("HANDFREE_LANGUAGE"),
            type_delay=float(os.environ.get("HANDFREE_TYPE_DELAY", "0")),
            sample_rate=int(os.environ.get("HANDFREE_SAMPLE_RATE", "16000")),
            use_paste=parse_bool(os.environ.get("HANDFREE_USE_PASTE", ""), False),
            ui_enabled=parse_bool(os.environ.get("HANDFREE_UI_ENABLED", "true"), True),
            ui_position=os.environ.get("HANDFREE_UI_POSITION", "top-center").lower(),
            history_enabled=parse_bool(os.environ.get("HANDFREE_HISTORY_ENABLED", "true"), True),
            history_max_entries=int(os.environ.get("HANDFREE_HISTORY_MAX", "1000")),
            custom_hotkey=os.environ.get("HANDFREE_HOTKEY"),
        )

    def validate(self) -> List[str]:
        """
        Validate configuration values.

        Returns:
            List of warning messages (empty if no warnings).

        Raises:
            ValueError: If configuration values are invalid.
        """
        warnings = []

        if self.type_delay < 0:
            raise ValueError("HANDFREE_TYPE_DELAY must be non-negative")

        if self.sample_rate <= 0:
            raise ValueError("HANDFREE_SAMPLE_RATE must be positive")

        valid_sample_rates = [8000, 16000, 22050, 44100, 48000]
        if self.sample_rate not in valid_sample_rates:
            warnings.append(
                f"Unusual sample rate {self.sample_rate}. "
                f"Common values are: {valid_sample_rates}"
            )

        if self.ui_position not in VALID_UI_POSITIONS:
            raise ValueError(
                f"HANDFREE_UI_POSITION must be one of: {', '.join(VALID_UI_POSITIONS)}. "
                f"Got: {self.ui_position}"
            )

        if self.history_max_entries <= 0:
            raise ValueError("HANDFREE_HISTORY_MAX must be positive")

        if self.history_max_entries > 100000:
            warnings.append(
                f"Large history max ({self.history_max_entries}) may impact performance"
            )

        return warnings
