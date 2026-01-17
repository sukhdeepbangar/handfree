"""
Configuration Module
Loads and validates settings from environment variables.
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration from environment variables."""

    # Required
    groq_api_key: str

    # Optional with defaults
    language: Optional[str] = None  # Auto-detect if not set
    type_delay: float = 0.0
    sample_rate: int = 16000
    use_paste: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        """
        Load configuration from environment variables.

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

        return cls(
            groq_api_key=groq_api_key,
            language=os.environ.get("HANDFREE_LANGUAGE"),
            type_delay=float(os.environ.get("HANDFREE_TYPE_DELAY", "0")),
            sample_rate=int(os.environ.get("HANDFREE_SAMPLE_RATE", "16000")),
            use_paste=os.environ.get("HANDFREE_USE_PASTE", "").lower() in ("true", "1", "yes"),
        )

    def validate(self) -> None:
        """
        Validate configuration values.

        Raises:
            ValueError: If configuration values are invalid.
        """
        if self.type_delay < 0:
            raise ValueError("HANDFREE_TYPE_DELAY must be non-negative")

        if self.sample_rate <= 0:
            raise ValueError("HANDFREE_SAMPLE_RATE must be positive")

        valid_sample_rates = [8000, 16000, 22050, 44100, 48000]
        if self.sample_rate not in valid_sample_rates:
            print(f"Warning: Unusual sample rate {self.sample_rate}. "
                  f"Common values are: {valid_sample_rates}")
