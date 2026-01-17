"""
Output Handler Module
Copies transcription to clipboard and types into active application.
"""

import subprocess
from typing import Optional

import pyperclip

from handfree.exceptions import OutputError


class OutputHandler:
    """Handles output of transcribed text to clipboard and active app."""

    def __init__(self, type_delay: float = 0.0):
        """
        Initialize output handler.

        Args:
            type_delay: Delay between keystrokes in seconds (0 = fastest)
        """
        self.type_delay = type_delay

    def copy_to_clipboard(self, text: str) -> None:
        """
        Copy text to system clipboard.

        Args:
            text: Text to copy to clipboard

        Raises:
            OutputError: If clipboard operation fails
        """
        if not text:
            return

        try:
            pyperclip.copy(text)
        except Exception as e:
            raise OutputError(f"Failed to copy to clipboard: {e}")

    def type_text(self, text: str) -> None:
        """
        Type text into active application using AppleScript.

        This method is more reliable than pyautogui on macOS.

        Args:
            text: Text to type into the active application

        Raises:
            OutputError: If typing operation fails
        """
        if not text:
            return

        # Escape special characters for AppleScript
        # Handle backslash first, then quotes
        escaped = text.replace('\\', '\\\\').replace('"', '\\"')

        # Use AppleScript to type the text
        script = f'tell application "System Events" to keystroke "{escaped}"'

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                check=True,
                capture_output=True,
                timeout=10
            )
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode() if e.stderr else str(e)
            raise OutputError(f"Failed to type text: {stderr}")
        except subprocess.TimeoutExpired:
            raise OutputError("Typing operation timed out")
        except FileNotFoundError:
            raise OutputError("osascript not found - this module requires macOS")

    def type_text_via_paste(self, text: str) -> None:
        """
        Alternative method: copy to clipboard and paste.

        This can be more reliable for special characters.

        Args:
            text: Text to paste into the active application

        Raises:
            OutputError: If operation fails
        """
        if not text:
            return

        # Copy to clipboard
        self.copy_to_clipboard(text)

        # Simulate Cmd+V to paste
        script = 'tell application "System Events" to keystroke "v" using command down'

        try:
            subprocess.run(
                ['osascript', '-e', script],
                check=True,
                capture_output=True,
                timeout=10
            )
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode() if e.stderr else str(e)
            raise OutputError(f"Failed to paste text: {stderr}")
        except subprocess.TimeoutExpired:
            raise OutputError("Paste operation timed out")

    def output(self, text: str, use_paste: bool = False) -> None:
        """
        Copy text to clipboard AND type into active app.

        Args:
            text: Transcribed text to output
            use_paste: If True, use clipboard paste instead of keystroke typing

        Raises:
            OutputError: If output operation fails
        """
        if not text:
            return

        # Always copy to clipboard first (as backup)
        self.copy_to_clipboard(text)

        # Then type or paste into active app
        if use_paste:
            # Just paste - clipboard already has the text
            script = 'tell application "System Events" to keystroke "v" using command down'
            try:
                subprocess.run(
                    ['osascript', '-e', script],
                    check=True,
                    capture_output=True,
                    timeout=10
                )
            except Exception as e:
                raise OutputError(f"Failed to paste: {e}")
        else:
            self.type_text(text)


def get_clipboard_content() -> str:
    """
    Get current clipboard content.

    Returns:
        Current clipboard text content

    Raises:
        OutputError: If clipboard read fails
    """
    try:
        return pyperclip.paste()
    except Exception as e:
        raise OutputError(f"Failed to read clipboard: {e}")
