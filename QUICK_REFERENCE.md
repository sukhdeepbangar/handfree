# HandFree - Quick Reference

## Current Status
- ✅ Working: Fn key → Record → Transcribe → Type
- ⚠️ Issue: Silent audio → "thank you" hallucination
- 🎯 Goal: Always-listening + text cleanup

## Management Commands
```bash
./handfree.sh status    # Check if running
./handfree.sh start     # Start app
./handfree.sh stop      # Stop app
./handfree.sh logs      # View logs
./handfree.sh restart   # Restart
```

## Next Features to Implement
1. **Ollama text cleanup** (remove um, uh, false starts)
2. **VAD** (Voice Activity Detection - detect speech vs silence)
3. **Always-listening mode** (no button needed)

## Key Files
- `main.py` - Main application
- `src/handfree/transcriber.py` - Groq Whisper integration
- `src/handfree/audio_recorder.py` - Audio capture
- `SESSION_CONTEXT.md` - Full project context
- `NEXT_SESSION_PROMPT.md` - Planning prompt

## API Limits (Groq Free Tier)
- Whisper: 2,000 requests/day ✅ Plenty
- Llama: 30,000 tokens/min ✅ Plenty

## Ollama Setup (For Next Session)
```bash
brew install ollama
ollama serve &
ollama pull llama3.2:1b
pip install ollama
```

## Architecture Vision
```
Always listening → VAD detects speech → Record → Whisper API
  → Ollama cleanup (local) → Filter hallucinations → Type
```
