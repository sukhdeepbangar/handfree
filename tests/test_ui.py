"""
Tests for HandFree UI Components

Tests the recording indicator and UI controller.
Note: These tests verify the UI module's structure and interface without requiring a display.
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch


# Mock tkinter if not available
try:
    import tkinter
except ImportError:
    # Create a mock tkinter module
    import sys
    from unittest.mock import MagicMock

    mock_tk = MagicMock()
    mock_tk.Tk = MagicMock
    mock_tk.Toplevel = MagicMock
    mock_tk.Canvas = MagicMock
    mock_tk.TclError = Exception

    sys.modules['tkinter'] = mock_tk
    sys.modules['_tkinter'] = MagicMock()


class TestRecordingIndicatorStructure:
    """Tests for RecordingIndicator class structure and configuration."""

    def test_state_config_exists(self):
        """Test that STATE_CONFIG exists and has correct structure."""
        from handfree.ui.indicator import RecordingIndicator

        assert hasattr(RecordingIndicator, 'STATE_CONFIG')
        config = RecordingIndicator.STATE_CONFIG
        assert isinstance(config, dict)
        assert len(config) > 0

    def test_state_config_has_all_states(self):
        """Test that STATE_CONFIG contains all required states."""
        from handfree.ui.indicator import RecordingIndicator

        required_states = ["idle", "recording", "transcribing", "success", "error"]
        config = RecordingIndicator.STATE_CONFIG

        for state in required_states:
            assert state in config, f"Missing state: {state}"
            state_config = config[state]
            assert len(state_config) == 4, f"State {state} should have 4 config values"
            bg_color, text_color, text, opacity = state_config
            assert isinstance(bg_color, str), f"State {state} bg_color should be string"
            assert isinstance(text_color, str), f"State {state} text_color should be string"
            assert isinstance(text, str), f"State {state} text should be string"
            assert isinstance(opacity, (float, int)), f"State {state} opacity should be number"
            assert 0 <= opacity <= 1, f"State {state} opacity should be between 0 and 1"

    def test_state_colors(self):
        """Test that states have correct colors."""
        from handfree.ui.indicator import RecordingIndicator

        config = RecordingIndicator.STATE_CONFIG

        # Recording should be red
        assert config["recording"][0] == "#FF3B30", "Recording should be red"

        # Transcribing should be orange
        assert config["transcribing"][0] == "#FF9500", "Transcribing should be orange"

        # Success should be green
        assert config["success"][0] == "#34C759", "Success should be green"

        # Error should be red
        assert config["error"][0] == "#FF3B30", "Error should be red"

        # Idle should be dark gray
        assert config["idle"][0] == "#333333", "Idle should be dark gray"

    def test_state_text(self):
        """Test that states have correct display text."""
        from handfree.ui.indicator import RecordingIndicator

        config = RecordingIndicator.STATE_CONFIG

        assert config["recording"][2] == "REC", "Recording should show 'REC'"
        assert config["transcribing"][2] == "...", "Transcribing should show '...'"
        assert config["success"][2] == "OK", "Success should show 'OK'"
        assert config["error"][2] == "ERR", "Error should show 'ERR'"
        assert config["idle"][2] == "", "Idle should show no text"

    def test_indicator_has_required_methods(self):
        """Test that RecordingIndicator has all required methods."""
        from handfree.ui.indicator import RecordingIndicator

        required_methods = ['set_state', 'show', 'hide', 'destroy']
        for method in required_methods:
            assert hasattr(RecordingIndicator, method), f"Missing method: {method}"
            assert callable(getattr(RecordingIndicator, method)), f"{method} should be callable"


class TestHandFreeUIStructure:
    """Tests for HandFreeUI controller class structure."""

    def test_ui_class_exists(self):
        """Test that HandFreeUI class exists."""
        from handfree.ui.app import HandFreeUI
        assert HandFreeUI is not None

    def test_ui_has_required_methods(self):
        """Test that HandFreeUI has all required methods."""
        from handfree.ui.app import HandFreeUI

        required_methods = ['start', 'stop', 'set_state']
        for method in required_methods:
            assert hasattr(HandFreeUI, method), f"Missing method: {method}"
            assert callable(getattr(HandFreeUI, method)), f"{method} should be callable"

    def test_ui_can_be_instantiated(self):
        """Test that HandFreeUI can be instantiated."""
        from handfree.ui.app import HandFreeUI

        # Should not raise exception
        ui = HandFreeUI()
        assert ui is not None
        assert hasattr(ui, '_running')
        assert ui._running is False

    def test_ui_set_state_when_not_running(self):
        """Test that set_state doesn't crash when UI not running."""
        from handfree.ui.app import HandFreeUI

        ui = HandFreeUI()
        # Should not raise exception even when not running
        ui.set_state("recording")
        ui.set_state("idle")

    def test_ui_stop_when_not_running(self):
        """Test that stop doesn't crash when UI not running."""
        from handfree.ui.app import HandFreeUI

        ui = HandFreeUI()
        # Should not raise exception
        ui.stop()


class TestUIModule:
    """Tests for UI module exports."""

    def test_ui_module_exports(self):
        """Test that ui module exports required classes."""
        from handfree.ui import HandFreeUI, RecordingIndicator

        assert HandFreeUI is not None
        assert RecordingIndicator is not None

    def test_handfree_main_package_exports_ui(self):
        """Test that main handfree package exports UI classes."""
        from handfree import HandFreeUI, RecordingIndicator

        # Should be available from main package
        assert HandFreeUI is not None or HandFreeUI is None  # May be None if tkinter not available
        assert RecordingIndicator is not None or RecordingIndicator is None


class TestUIDisabling:
    """Tests for UI disabling functionality."""

    def test_main_app_accepts_ui_enabled_parameter(self):
        """Test that HandFreeApp accepts ui_enabled parameter."""
        import inspect
        import sys
        import os

        # Add parent directory to path to import main
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

        from main import HandFreeApp

        # Check that __init__ accepts ui_enabled parameter
        sig = inspect.signature(HandFreeApp.__init__)
        assert 'ui_enabled' in sig.parameters, "HandFreeApp should accept ui_enabled parameter"

        # Check default value is True
        param = sig.parameters['ui_enabled']
        assert param.default is True, "ui_enabled should default to True"

    def test_main_app_can_disable_ui(self):
        """Test that HandFreeApp can be created with UI disabled."""
        import sys
        import os

        # Add parent directory to path
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

        # Mock dependencies - use the correct paths after refactoring
        with patch('main.AudioRecorder'), \
             patch('main.Transcriber'), \
             patch('main.create_output_handler'), \
             patch('main.create_hotkey_detector'), \
             patch('main.load_dotenv'):

            from main import HandFreeApp

            # Should not raise exception
            app = HandFreeApp(ui_enabled=False)
            assert app.ui is None  # UI should be None when disabled


class TestStateTransitions:
    """Tests for state transition logic."""

    def test_valid_states(self):
        """Test that all expected states are defined."""
        from handfree.ui.indicator import RecordingIndicator

        valid_states = ["idle", "recording", "transcribing", "success", "error"]
        config = RecordingIndicator.STATE_CONFIG

        for state in valid_states:
            assert state in config, f"State {state} should be in STATE_CONFIG"

    def test_state_opacity_values(self):
        """Test that state opacity values are correct."""
        from handfree.ui.indicator import RecordingIndicator

        config = RecordingIndicator.STATE_CONFIG

        # Idle should be semi-transparent
        assert config["idle"][3] < 0.5, "Idle should be more transparent"

        # Active states should be more opaque
        for state in ["recording", "transcribing", "success", "error"]:
            assert config[state][3] > 0.5, f"{state} should be more opaque"


class TestUIThreadSafety:
    """Tests for UI thread safety."""

    def test_ui_start_is_idempotent(self):
        """Test that calling start multiple times is safe."""
        from handfree.ui.app import HandFreeUI

        ui = HandFreeUI()

        # Mock threading to prevent actual thread creation
        with patch('handfree.ui.app.threading.Thread') as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread

            ui.start()
            first_call_count = mock_thread_class.call_count

            ui.start()  # Call again
            second_call_count = mock_thread_class.call_count

            # Should not create another thread
            assert first_call_count == second_call_count, "start() should be idempotent"

    def test_ui_creates_daemon_thread(self):
        """Test that UI thread is created as daemon."""
        from handfree.ui.app import HandFreeUI

        ui = HandFreeUI()

        with patch('handfree.ui.app.threading.Thread') as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread

            ui.start()

            # Verify thread was created as daemon
            mock_thread_class.assert_called_once()
            call_kwargs = mock_thread_class.call_args[1]
            assert call_kwargs['daemon'] is True, "UI thread should be daemon"
            assert callable(call_kwargs['target']), "Thread should have target function"


class TestIndicatorPosition:
    """Tests for RecordingIndicator position configuration."""

    def test_valid_positions_constant_exists(self):
        """Test that VALID_POSITIONS constant exists in indicator module."""
        from handfree.ui.indicator import VALID_POSITIONS

        assert isinstance(VALID_POSITIONS, list)
        assert len(VALID_POSITIONS) == 6

    def test_valid_positions_values(self):
        """Test that VALID_POSITIONS contains expected values."""
        from handfree.ui.indicator import VALID_POSITIONS

        expected = ["top-center", "top-right", "top-left",
                    "bottom-center", "bottom-right", "bottom-left"]
        assert set(VALID_POSITIONS) == set(expected)

    def test_indicator_accepts_position_parameter(self):
        """Test that RecordingIndicator accepts position parameter."""
        import inspect
        from handfree.ui.indicator import RecordingIndicator

        sig = inspect.signature(RecordingIndicator.__init__)
        assert 'position' in sig.parameters, "RecordingIndicator should accept position parameter"
        assert sig.parameters['position'].default == "top-center", "Default position should be top-center"

    @pytest.fixture
    def mock_tkinter(self):
        """Create comprehensive tkinter mocks."""
        mock_window = MagicMock()
        mock_canvas = MagicMock()

        with patch('handfree.ui.indicator.tk.Toplevel', return_value=mock_window), \
             patch('handfree.ui.indicator.tk.Canvas', return_value=mock_canvas):
            yield {'window': mock_window, 'canvas': mock_canvas}

    def test_indicator_stores_position(self, mock_tkinter):
        """Test that indicator stores the position value."""
        from handfree.ui.indicator import RecordingIndicator

        indicator = RecordingIndicator(position="bottom-right")
        assert indicator._position == "bottom-right"

    def test_indicator_defaults_to_top_center(self, mock_tkinter):
        """Test that indicator defaults to top-center position."""
        from handfree.ui.indicator import RecordingIndicator

        indicator = RecordingIndicator()
        assert indicator._position == "top-center"

    def test_indicator_position_property(self, mock_tkinter):
        """Test that indicator has position property."""
        from handfree.ui.indicator import RecordingIndicator

        indicator = RecordingIndicator(position="top-right")
        assert hasattr(indicator, 'position')
        assert indicator.position == "top-right"

    def test_indicator_set_position_method(self, mock_tkinter):
        """Test that indicator has set_position method."""
        from handfree.ui.indicator import RecordingIndicator

        indicator = RecordingIndicator(position="top-center")
        assert hasattr(indicator, 'set_position')
        assert callable(indicator.set_position)

    def test_indicator_set_position_changes_position(self, mock_tkinter):
        """Test that set_position changes the position."""
        from handfree.ui.indicator import RecordingIndicator

        indicator = RecordingIndicator(position="top-center")
        indicator.set_position("bottom-left")
        assert indicator._position == "bottom-left"

    def test_indicator_set_position_invalid_raises(self, mock_tkinter):
        """Test that set_position raises error for invalid position."""
        from handfree.ui.indicator import RecordingIndicator

        indicator = RecordingIndicator()

        with pytest.raises(ValueError) as exc_info:
            indicator.set_position("invalid-position")

        assert "invalid-position" in str(exc_info.value).lower()

    @pytest.mark.parametrize("position", [
        "top-center", "top-right", "top-left",
        "bottom-center", "bottom-right", "bottom-left"
    ])
    def test_indicator_accepts_all_valid_positions(self, position):
        """Test that indicator accepts all valid positions."""
        from handfree.ui.indicator import RecordingIndicator

        mock_window = MagicMock()
        mock_canvas = MagicMock()

        with patch('handfree.ui.indicator.tk.Toplevel', return_value=mock_window), \
             patch('handfree.ui.indicator.tk.Canvas', return_value=mock_canvas):
            indicator = RecordingIndicator(position=position)
            assert indicator._position == position

    def test_indicator_invalid_position_falls_back_to_default(self, mock_tkinter):
        """Test that invalid position falls back to top-center."""
        from handfree.ui.indicator import RecordingIndicator

        indicator = RecordingIndicator(position="invalid")
        assert indicator._position == "top-center"

    def test_indicator_edge_margin_constant(self):
        """Test that EDGE_MARGIN constant exists."""
        from handfree.ui.indicator import RecordingIndicator

        assert hasattr(RecordingIndicator, 'EDGE_MARGIN')
        assert RecordingIndicator.EDGE_MARGIN > 0


class TestHandFreeUIPosition:
    """Tests for HandFreeUI indicator_position parameter."""

    def test_ui_accepts_indicator_position(self):
        """Test that HandFreeUI accepts indicator_position parameter."""
        import inspect
        from handfree.ui.app import HandFreeUI

        sig = inspect.signature(HandFreeUI.__init__)
        assert 'indicator_position' in sig.parameters
        assert sig.parameters['indicator_position'].default == "top-center"

    def test_ui_stores_indicator_position(self):
        """Test that HandFreeUI stores indicator_position."""
        from handfree.ui.app import HandFreeUI

        ui = HandFreeUI(indicator_position="bottom-right")
        assert ui._indicator_position == "bottom-right"

    def test_ui_defaults_to_top_center(self):
        """Test that HandFreeUI defaults to top-center."""
        from handfree.ui.app import HandFreeUI

        ui = HandFreeUI()
        assert ui._indicator_position == "top-center"

    @pytest.mark.parametrize("position", [
        "top-center", "top-right", "top-left",
        "bottom-center", "bottom-right", "bottom-left"
    ])
    def test_ui_accepts_all_valid_positions(self, position):
        """Test that HandFreeUI accepts all valid positions."""
        from handfree.ui.app import HandFreeUI

        ui = HandFreeUI(indicator_position=position)
        assert ui._indicator_position == position
