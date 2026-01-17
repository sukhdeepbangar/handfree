"""
Test Project Initialization

Verifies that all dependencies are installed correctly and can be imported.
"""

import pytest


class TestDependencies:
    """Test that all required dependencies can be imported."""

    def test_import_avfoundation(self):
        """Test AVFoundation framework imports."""
        from AVFoundation import AVAudioSession, AVAudioApplication
        assert AVAudioSession is not None
        assert AVAudioApplication is not None

    def test_import_cocoa(self):
        """Test Cocoa framework imports."""
        from Foundation import NSNotificationCenter, NSRunLoop, NSDefaultRunLoopMode
        assert NSNotificationCenter is not None
        assert NSRunLoop is not None
        assert NSDefaultRunLoopMode is not None

    def test_import_sounddevice(self):
        """Test sounddevice imports."""
        import sounddevice as sd
        assert sd is not None
        # Verify we can query devices
        devices = sd.query_devices()
        assert devices is not None

    def test_import_numpy(self):
        """Test numpy imports."""
        import numpy as np
        assert np is not None

    def test_import_scipy(self):
        """Test scipy imports."""
        from scipy.io import wavfile
        assert wavfile is not None

    def test_import_groq(self):
        """Test groq imports."""
        from groq import Groq
        assert Groq is not None

    def test_import_pyperclip(self):
        """Test pyperclip imports."""
        import pyperclip
        assert pyperclip is not None

    def test_import_pyautogui(self):
        """Test pyautogui imports."""
        import pyautogui
        assert pyautogui is not None

    def test_import_dotenv(self):
        """Test python-dotenv imports."""
        from dotenv import load_dotenv
        assert load_dotenv is not None


class TestEnvironment:
    """Test environment configuration."""

    def test_env_file_exists(self):
        """Test that .env file exists."""
        import os
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        assert os.path.exists(env_path), ".env file should exist"

    def test_env_example_exists(self):
        """Test that .env.example file exists."""
        import os
        env_example_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.example')
        assert os.path.exists(env_example_path), ".env.example file should exist"

    def test_load_dotenv(self):
        """Test that dotenv can load environment variables."""
        from dotenv import load_dotenv
        import os

        # Load .env file
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path)

        # Check that GROQ_API_KEY is set (even if it's just a placeholder)
        api_key = os.getenv('GROQ_API_KEY')
        assert api_key is not None, "GROQ_API_KEY should be set in .env file"


class TestRequirements:
    """Test requirements.txt file."""

    def test_requirements_file_exists(self):
        """Test that requirements.txt exists."""
        import os
        req_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'requirements.txt')
        assert os.path.exists(req_path), "requirements.txt should exist"

    def test_requirements_not_empty(self):
        """Test that requirements.txt is not empty."""
        import os
        req_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'requirements.txt')
        with open(req_path, 'r') as f:
            content = f.read()
        assert len(content) > 0, "requirements.txt should not be empty"
        assert 'groq' in content.lower(), "requirements.txt should include groq"
        assert 'sounddevice' in content.lower(), "requirements.txt should include sounddevice"
