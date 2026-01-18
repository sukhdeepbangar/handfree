# Prompt for Next Claude Session

Hi Claude! I'm working on HandFree, a speech-to-text app for macOS.

**Please read SESSION_CONTEXT.md first** - it has all the background.

## What I Need Help With

I want to plan and implement these features:

### 1. **Ollama Integration for Text Cleanup**
- Install Ollama locally on Mac
- Use llama3.2:1b model
- Clean up disfluencies (um, uh, like, false starts, corrections)
- Keep text processing private (local only)

### 2. **Voice Activity Detection (VAD)**
- Detect when speech starts/stops
- Only send real speech to API (not silence)
- Fix the "thank you" hallucination problem
- Use SileroVAD or WebRTC VAD

### 3. **Always-Listening Mode**
- No button press needed
- Continuous monitoring with VAD
- Auto-record when speech detected
- Auto-transcribe when silence detected
- Filter out hallucinations and noise
- Only type meaningful text

## Task for This Session

**Please help me create a detailed implementation plan:**
- Break down into phases
- Identify files to modify
- List specific code changes needed
- Highlight potential issues
- Suggest testing approach

After planning, we'll implement in a follow-up session.

## Current Project State
- App is working with Fn key trigger
- Using Groq Whisper API
- Files: main.py, src/handfree/*.py
- See SESSION_CONTEXT.md for full details
