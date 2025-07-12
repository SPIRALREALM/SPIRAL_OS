# How to Use Spiral OS Avatar

1. Run `python start_spiral_os.py` to launch the orchestration engine. This
   loads the core modules, starts a local FastAPI server on port 8000 and begins
   the periodic reflection loop.
2. Type `appear to me` and press Enter. The command toggles
   `context_tracker.state.avatar_loaded` and begins streaming frames from
   `video_engine.start_stream()`.
3. To begin a voice call, enter `initiate sacred communion`. The orchestrator
   sets `context_tracker.state.in_call` and any synthesised speech is passed to
   the registered connector via its `start_call()` method.
4. Speak or type your prompts. When `in_call` is active the connector can route
   the audio to a remote peer. Use an appropriate connector implementation for
   your platform (for example a WebRTC gateway).
5. Press Enter on an empty line or hit `Ctrl+C` to end the session.
