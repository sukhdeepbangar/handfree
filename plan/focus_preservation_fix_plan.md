# Focus Preservation Fix Plan

**Issue:** When pressing Fn key to record, focus is stolen from the active text area, causing transcript to not be pasted in the correct location.

**Root Cause:** The current focus prevention code in `indicator.py` uses `wm_attributes('-modified', 0)` which is incorrect. The `-modified` attribute controls the document modification indicator (dot in close button), NOT focus behavior.

**Date:** 2026-01-18
**Status:** ✅ COMPLETE

---

## Investigation Summary

### Current Implementation (Broken)

File: `src/handfree/ui/indicator.py` lines 132-156

```python
def _setup_focus_prevention(self) -> None:
    try:
        if self._platform == "macos":
            # WRONG: -modified is for document modification indicator
            self.window.wm_attributes('-modified', 0)
        # ...
```

### Why It Doesn't Work

1. `-modified` attribute controls the "unsaved changes" dot in the window's close button
2. It has NO effect on focus stealing behavior
3. The indicator window still becomes the key window when shown

### Correct Solution

Use PyObjC to access the underlying NSWindow and configure it properly:

```python
from AppKit import NSWindow, NSFloatingWindowLevel
from objc import objc_object
from ctypes import c_void_p

# Get NSWindow from tkinter window
nswindow = objc_object(c_void_p=window.winfo_id())

# Prevent window from becoming key (receiving keyboard input)
nswindow.setCanBecomeKey_(False)

# Prevent window from becoming main (the "active" window)
nswindow.setCanBecomeMain_(False)

# Optional: Set to floating panel level
nswindow.setLevel_(NSFloatingWindowLevel)
```

---

## Implementation Plan

### Phase 1: Fix macOS Focus Prevention

#### Step 1.1: Update `_setup_focus_prevention()` method

**File:** `src/handfree/ui/indicator.py`

**Tasks:**
- [ ] Add PyObjC imports at top of file (conditional for macOS)
- [ ] Replace incorrect `-modified` code with proper NSWindow configuration
- [ ] Add error handling for cases where PyObjC is not available
- [ ] Add fallback behavior if NSWindow access fails

**Code Changes:**

```python
# At top of file, add conditional import
import sys
if sys.platform == "darwin":
    try:
        from AppKit import NSFloatingWindowLevel
        from objc import objc_object
        from ctypes import c_void_p
        PYOBJC_AVAILABLE = True
    except ImportError:
        PYOBJC_AVAILABLE = False
else:
    PYOBJC_AVAILABLE = False


# Replace _setup_focus_prevention method
def _setup_focus_prevention(self) -> None:
    """Configure platform-specific settings to prevent stealing focus."""
    try:
        if self._platform == "macos":
            self._setup_macos_focus_prevention()
        elif self._platform == "linux":
            # Linux: Set window type to prevent focus
            try:
                self.window.attributes('-type', 'notification')
            except tk.TclError:
                try:
                    self.window.attributes('-type', 'splash')
                except tk.TclError:
                    pass
        # Windows: overrideredirect(True) is usually sufficient
    except Exception:
        # If focus prevention fails, continue anyway
        pass


def _setup_macos_focus_prevention(self) -> None:
    """Configure macOS-specific window properties to prevent focus stealing."""
    if not PYOBJC_AVAILABLE:
        return

    try:
        # Force window to be created and mapped
        self.window.update_idletasks()

        # Get the native window ID
        window_id = self.window.winfo_id()
        if not window_id:
            return

        # Access the NSWindow via PyObjC
        nswindow = objc_object(c_void_p=window_id)

        # Prevent window from becoming key window (no keyboard focus)
        if hasattr(nswindow, 'setCanBecomeKey_'):
            nswindow.setCanBecomeKey_(False)

        # Prevent window from becoming main window
        if hasattr(nswindow, 'setCanBecomeMain_'):
            nswindow.setCanBecomeMain_(False)

        # Set window level to floating (above normal windows)
        if hasattr(nswindow, 'setLevel_'):
            nswindow.setLevel_(NSFloatingWindowLevel)

        # Make window non-activating
        if hasattr(nswindow, 'setCollectionBehavior_'):
            # NSWindowCollectionBehaviorCanJoinAllSpaces | NSWindowCollectionBehaviorStationary
            nswindow.setCollectionBehavior_(1 << 0 | 1 << 4)

    except Exception:
        # Silently fail - focus prevention is best-effort
        pass
```

#### Step 1.2: Update show() method

**File:** `src/handfree/ui/indicator.py`

**Tasks:**
- [ ] Ensure focus prevention is applied before showing window
- [ ] Re-apply NSWindow settings after deiconify (some settings may reset)

**Code Changes:**

```python
def show(self) -> None:
    """Show the indicator window without stealing focus."""
    # Re-apply focus prevention before showing (settings may have reset)
    if self._platform == "macos":
        self._setup_macos_focus_prevention()

    self.window.deiconify()

    # Don't call lift() on macOS as it can steal focus
    if self._platform != "macos":
        self.window.lift()
```

---

### Phase 2: Alternative Approach (If Phase 1 Fails)

If direct NSWindow manipulation doesn't work reliably, implement a pure Cocoa solution:

#### Step 2.1: Create native macOS indicator using PyObjC

**File:** `src/handfree/ui/macos_indicator.py` (NEW)

**Tasks:**
- [ ] Create NSPanel-based indicator (NSPanel can be non-activating)
- [ ] Implement same interface as RecordingIndicator
- [ ] Use factory function to return appropriate implementation

**Code Outline:**

```python
"""
Native macOS Recording Indicator using NSPanel.

NSPanel with NSNonactivatingPanelMask prevents focus stealing.
"""

from AppKit import (
    NSPanel, NSView, NSColor, NSFont, NSMakeRect,
    NSWindowStyleMaskBorderless, NSFloatingWindowLevel,
    NSNonactivatingPanelMask, NSBackingStoreBuffered
)
from Foundation import NSObject


class MacOSNativeIndicator:
    """Native macOS indicator using NSPanel."""

    def __init__(self, width=60, height=24, position="top-center"):
        # Create non-activating panel
        style = NSWindowStyleMaskBorderless | NSNonactivatingPanelMask
        self.panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, width, height),
            style,
            NSBackingStoreBuffered,
            False
        )

        # Configure panel
        self.panel.setLevel_(NSFloatingWindowLevel)
        self.panel.setCanBecomeKey_(False)
        self.panel.setCanBecomeMain_(False)
        self.panel.setHidesOnDeactivate_(False)
        self.panel.setAlphaValue_(0.95)

        # ... rest of implementation
```

---

### Phase 3: Testing

#### Step 3.1: Update existing tests

**File:** `tests/test_focus_preservation.py`

**Tasks:**
- [ ] Update test for macOS focus prevention to check for PyObjC usage
- [ ] Add test for NSWindow configuration (mocked)
- [ ] Add integration test for full recording flow

**Test Cases:**

```python
def test_macos_focus_prevention_uses_pyobjc():
    """Verify macOS focus prevention uses PyObjC NSWindow configuration."""
    # ...

def test_indicator_does_not_become_key_window():
    """Verify indicator window cannot become key window on macOS."""
    # ...

def test_show_reapplies_focus_prevention():
    """Verify show() re-applies focus prevention settings."""
    # ...
```

#### Step 3.2: Manual testing checklist

**Apps to test:**
- [ ] TextEdit - cursor in document
- [ ] VS Code - cursor in editor
- [ ] Terminal - command line input
- [ ] Safari/Chrome - text field in browser
- [ ] Slack/Discord - message input
- [ ] Notes app

**Test procedure for each app:**
1. Open app and place cursor in text input
2. Press and hold Fn key
3. Verify: Cursor remains in text input (not stolen)
4. Verify: Recording indicator appears
5. Speak some text
6. Release Fn key
7. Verify: Transcript appears at cursor position
8. Verify: Original app still has focus

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/handfree/ui/indicator.py` | Fix `_setup_focus_prevention()`, add PyObjC imports, update `show()` |
| `tests/test_focus_preservation.py` | Update tests for new implementation |

## Files to Create (Phase 2 only)

| File | Purpose |
|------|---------|
| `src/handfree/ui/macos_indicator.py` | Native NSPanel-based indicator (fallback) |

---

## Dependencies

No new dependencies required. PyObjC is already a dependency for macOS:
- `pyobjc-framework-Cocoa` (already installed)
- `pyobjc-framework-Quartz` (already installed)

The `AppKit` and `objc` modules are part of pyobjc-framework-Cocoa.

---

## Rollback Plan

If the fix causes issues:
1. Revert `_setup_focus_prevention()` to previous implementation
2. Keep `overrideredirect(True)` and `-topmost` (partial focus prevention)
3. Document known limitation in README

---

## Success Criteria

- [ ] Focus remains in text area when Fn key is pressed
- [ ] Recording indicator appears without stealing focus
- [ ] Cursor position is preserved during recording
- [ ] Transcribed text appears at correct cursor location
- [ ] Works in Terminal, TextEdit, VS Code, browser text fields
- [ ] All existing tests pass
- [ ] No regression in other functionality
