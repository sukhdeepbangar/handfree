"""
Recording Indicator Component

Provides a minimal, always-on-top visual indicator showing the application state.
"""

import tkinter as tk
from typing import Optional


# Valid position values
VALID_POSITIONS = ["top-center", "top-right", "top-left", "bottom-center", "bottom-right", "bottom-left"]


class RecordingIndicator:
    """
    A minimal, always-on-top indicator window showing recording state.

    States:
    - idle: Hidden or very dim (dark gray)
    - recording: Red with "REC" text
    - transcribing: Orange with "..." text
    - success: Green with "OK" text (flashes briefly)
    - error: Red with "ERR" text (flashes briefly)
    """

    # State configuration: (bg_color, text_color, display_text, opacity)
    STATE_CONFIG = {
        "idle": ("#333333", "#FFFFFF", "", 0.3),
        "recording": ("#FF3B30", "#FFFFFF", "REC", 0.95),
        "transcribing": ("#FF9500", "#FFFFFF", "...", 0.95),
        "success": ("#34C759", "#FFFFFF", "OK", 0.95),
        "error": ("#FF3B30", "#FFFFFF", "ERR", 0.95),
    }

    # Margin from screen edges in pixels
    EDGE_MARGIN = 10

    def __init__(
        self,
        width: int = 60,
        height: int = 24,
        root: Optional[tk.Tk] = None,
        position: str = "top-center"
    ):
        """
        Initialize recording indicator.

        Args:
            width: Width of indicator in pixels
            height: Height of indicator in pixels
            root: Optional tkinter root window (for testing)
            position: Position on screen. One of: top-center, top-right, top-left,
                     bottom-center, bottom-right, bottom-left. Default: top-center.
        """
        self.width = width
        self.height = height
        self._current_state = "idle"
        self._flash_after_id = None
        self._position = position if position in VALID_POSITIONS else "top-center"

        # Create window if root not provided (for testing purposes)
        if root is None:
            self.window = tk.Toplevel()
        else:
            self.window = tk.Toplevel(root)

        # Configure window
        self.window.withdraw()  # Start hidden
        self.window.overrideredirect(True)  # No window decorations
        self.window.attributes("-topmost", True)  # Always on top

        # Platform-specific transparency
        try:
            # macOS
            self.window.attributes("-alpha", 0.3)
        except tk.TclError:
            try:
                # Windows
                self.window.attributes("-transparentcolor", "white")
            except tk.TclError:
                # Linux - transparency might not work everywhere
                pass

        # Create canvas for drawing
        self.canvas = tk.Canvas(
            self.window,
            width=width,
            height=height,
            highlightthickness=0,
            bg="white"
        )
        self.canvas.pack()

        # Draw initial state
        self._draw_state()

        # Position window at top-center
        self._position_window()

    def _position_window(self) -> None:
        """Position window based on configured position."""
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Calculate x position based on horizontal alignment
        if "center" in self._position:
            x = (screen_width - self.width) // 2
        elif "right" in self._position:
            x = screen_width - self.width - self.EDGE_MARGIN
        else:  # left
            x = self.EDGE_MARGIN

        # Calculate y position based on vertical alignment
        if self._position.startswith("top"):
            y = self.EDGE_MARGIN
        else:  # bottom
            y = screen_height - self.height - self.EDGE_MARGIN

        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")

    @property
    def position(self) -> str:
        """Current position setting."""
        return self._position

    def set_position(self, position: str) -> None:
        """
        Change the indicator position.

        Args:
            position: One of: top-center, top-right, top-left, bottom-center,
                     bottom-right, bottom-left
        """
        if position not in VALID_POSITIONS:
            raise ValueError(f"Invalid position: {position}. Must be one of {VALID_POSITIONS}")
        self._position = position
        self._position_window()

    def _draw_state(self) -> None:
        """Draw the current state on the canvas."""
        if self._current_state not in self.STATE_CONFIG:
            return

        bg_color, text_color, text, opacity = self.STATE_CONFIG[self._current_state]

        # Clear canvas
        self.canvas.delete("all")

        # Draw rounded rectangle background
        self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill=bg_color,
            outline="",
            width=0
        )

        # Draw text if any
        if text:
            self.canvas.create_text(
                self.width // 2,
                self.height // 2,
                text=text,
                fill=text_color,
                font=("Arial", 10, "bold")
            )

        # Update opacity
        try:
            self.window.attributes("-alpha", opacity)
        except tk.TclError:
            pass

    def set_state(self, state: str) -> None:
        """
        Set the indicator state.

        Args:
            state: One of "idle", "recording", "transcribing", "success", "error"
        """
        if state not in self.STATE_CONFIG:
            raise ValueError(f"Invalid state: {state}. Must be one of {list(self.STATE_CONFIG.keys())}")

        # Cancel any pending flash
        if self._flash_after_id:
            self.window.after_cancel(self._flash_after_id)
            self._flash_after_id = None

        self._current_state = state
        self._draw_state()

        # Show window if not idle, hide if idle
        if state == "idle":
            self.hide()
        else:
            self.show()

        # Flash effect for success/error states
        if state in ("success", "error"):
            # Auto-return to idle after 1.5 seconds
            self._flash_after_id = self.window.after(1500, lambda: self.set_state("idle"))

    def show(self) -> None:
        """Show the indicator window."""
        self.window.deiconify()
        self.window.lift()

    def hide(self) -> None:
        """Hide the indicator window."""
        self.window.withdraw()

    def destroy(self) -> None:
        """Destroy the indicator window."""
        if self._flash_after_id:
            self.window.after_cancel(self._flash_after_id)
        self.window.destroy()
