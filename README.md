# Coqui Studio | AI Voice Narrative

A professional AI voice generation studio using **Coqui XTTS v2** for high-quality voice cloning and **Groq (Llama 3)** for emotional text optimization.

## Features
- **Zero-Shot Voice Cloning**: Upload a 6-second sample to clone any voice.
- **AI Emotional Intelligence**: Uses Groq to automatically add dramatic pauses, breathiness, and emotional cues to your scripts.
- **High-Fidelity Audio**: Generates 24kHz studio-quality wav files.
- **Built-in Reference**: Includes a default high-quality female American voice.

## Setup
1. Install dependencies:
   ```bash
   pip install fastapi uvicorn TTS groq torch pydantic python-multipart
   ```
2. Start the server:
   ```bash
   python app.py
   ```
3. Open `http://localhost:8000` in your browser.

## Tech Stack
- **Backend**: FastAPI, Coqui TTS, Groq API
- **Frontend**: Vanilla JS, HTML5, CSS3 (Glassmorphism)
- **Model**: XTTS v2
