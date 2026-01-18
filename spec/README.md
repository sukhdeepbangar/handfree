# HandFree Specifications

Design documentation for HandFree, a speech-to-text application for macOS with AirPods/hotkey triggers.

## Quick Links

| Document | Status | Description |
|----------|--------|-------------|
| [spec.md](./spec.md) | **Implemented** | Core architecture and module specifications |
| [cross_platform_ui_spec.md](./cross_platform_ui_spec.md) | Planned | Cross-platform support & UI framework |
| [ui_improvements_spec.md](./ui_improvements_spec.md) | Partial | UI/UX enhancements |
| [subprocess_indicator_spec.md](./subprocess_indicator_spec.md) | **Implemented** | Focus-preserving recording indicator |

---

## Core Architecture

| Spec | Code | Purpose |
|------|------|---------|
| [spec.md](./spec.md) | [src/handfree/](../src/handfree/) | System architecture, state machine, module interfaces |

**Covers:**
- System architecture diagram
- State machine (IDLE → RECORDING → TRANSCRIBING)
- Module specifications:
  - `mute_detector.py` - AirPods mute/unmute detection
  - `audio_recorder.py` - Microphone audio capture
  - `transcriber.py` - Groq Whisper API client
  - `local_transcriber.py` - whisper.cpp local transcription (future)
  - `output_handler.py` - Clipboard & auto-typing
  - `main.py` - Application entry point
- Dependencies and configuration
- Performance targets
- Security considerations

---

## Transcription

| Spec | Code | Purpose |
|------|------|---------|
| [spec.md#module-3](./spec.md) | [transcriber.py](../src/handfree/transcriber.py) | Groq Whisper API (cloud) |
| [spec.md#module-3b](./spec.md) | — | whisper.cpp local transcription (future) |

**Cloud (Groq):** Fast, accurate, requires internet and API key
**Local (whisper.cpp):** Private, offline, no API costs (planned)

See also: [whisper_cpp_plan.md](../plan/whisper_cpp_plan.md)

---

## User Interface

| Spec | Code | Purpose |
|------|------|---------|
| [cross_platform_ui_spec.md](./cross_platform_ui_spec.md) | [src/handfree/ui/](../src/handfree/ui/) | Recording indicator, history panel, tkinter UI |
| [ui_improvements_spec.md](./ui_improvements_spec.md) | — | Animated bars, menu bar icon, paste-based output |
| [subprocess_indicator_spec.md](./subprocess_indicator_spec.md) | [subprocess_indicator.py](../src/handfree/ui/subprocess_indicator.py) | Focus-preserving indicator via subprocess |

**Key Features:**
- Recording indicator (top-center, always-on-top)
- Transcription history panel with SQLite storage
- Menu bar icon for app visibility
- Focus preservation during recording

---

## Cross-Platform Support

| Spec | Code | Purpose |
|------|------|---------|
| [cross_platform_ui_spec.md](./cross_platform_ui_spec.md) | [src/handfree/platform/](../src/handfree/platform/) | Platform abstraction layer |

**Platforms:**
| Platform | Hotkey | Status |
|----------|--------|--------|
| macOS | Fn/Globe key | **Implemented** |
| Windows | Ctrl+Shift+Space | Planned |
| Linux | Ctrl+Shift+Space | Planned |

---

## Implementation Plans

Related implementation plans in [../plan/](../plan/):

| Plan | Spec | Purpose |
|------|------|---------|
| [implementation_plan.md](../plan/implementation_plan.md) | [spec.md](./spec.md) | Core app implementation steps |
| [whisper_cpp_plan.md](../plan/whisper_cpp_plan.md) | [spec.md](./spec.md) | Local transcription integration |
| [cross_platform_ui_plan.md](../plan/cross_platform_ui_plan.md) | [cross_platform_ui_spec.md](./cross_platform_ui_spec.md) | Cross-platform & UI implementation |
| [ui_improvements_plan.md](../plan/ui_improvements_plan.md) | [ui_improvements_spec.md](./ui_improvements_spec.md) | UI enhancements implementation |
| [focus_preservation_fix_plan.md](../plan/focus_preservation_fix_plan.md) | [subprocess_indicator_spec.md](./subprocess_indicator_spec.md) | Focus stealing fix |

---

## Status Legend

| Status | Meaning |
|--------|---------|
| **Implemented** | Feature is complete and in production |
| Partial | Some components implemented |
| Planned | Specified but not yet implemented |
| Draft | Specification in progress |

---

## Contributing

When adding new specifications:

1. Create a new `.md` file in this directory
2. Follow the existing format (Requirements, Architecture, Interface sections)
3. Update this README.md with the new spec
4. Create a corresponding implementation plan in `../plan/`
