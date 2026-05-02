import os
# Must be set before importing/initializing TTS
os.environ["COQUI_TOS_AGREED"] = "1"

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from TTS.api import TTS
import uuid
import logging
import shutil
import torch
from typing import Optional

# Optimize for CPU if no GPU is available
if not torch.cuda.is_available():
    torch.set_num_threads(os.cpu_count() or 4)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = None

def get_model():
    global model
    if model is None:
        logger.info(f"Loading Coqui XTTS v2 on {device}... This may take a while on first run.")
        # XTTS v2 is a powerful multilingual model
        # gpu=True/False is set based on torch.cuda.is_available()
        model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=(device=="cuda"))
        logger.info("Coqui TTS model loaded successfully.")
    return model

# Groq client - Use environment variable for security
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
groq_client = Groq(api_key=GROQ_API_KEY)

class TextRequest(BaseModel):
    text: str
    api_key: Optional[str] = None

class GenerateRequest(BaseModel):
    text: str
    audio_prompt: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    logger.info("Server starting up. API is now active. Coqui model will load on first generation request.")

@app.post("/api/fix-tags")
async def fix_tags(request: TextRequest):
    try:
        # Use provided key or fallback to env
        key = request.api_key or GROQ_API_KEY
        if not key or key == "your_groq_api_key_here":
            raise Exception("No valid Groq API Key found. Please provide one in the UI.")
            
        local_groq = Groq(api_key=key)
        
        logger.info("Optimizing text for Coqui TTS...")
        prompt = (
            "You are a master scriptwriter for high-end AI narration. Your goal is to transform the input text "
            "into a deeply emotional, expressive, and natural-sounding script for a female American voice. \n\n"
            "STYLING RULES:\n"
            "1. Use ellipses (...) for dramatic pauses and breathy transitions.\n"
            "2. Use exclamation marks (!) sparingly but effectively for excitement.\n"
            "3. Use dashes (—) to show sudden shifts in thought or emphasis.\n"
            "4. Make it sound conversational, warm, and intimate. \n"
            "5. If there are tags like [laugh] or [sigh], replace them with descriptive text cues like 'haha...' or a heavy breath '...hmmm...'.\n\n"
            "Do NOT change the core meaning, but DO make it feel alive and emotional. Return ONLY the final text.\n\n"
            f"Input Text: {request.text}"
        )
        
        completion = local_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        fixed_text = completion.choices[0].message.content.strip()
        logger.info("Text optimized successfully.")
        return {"fixed_text": fixed_text}
    except Exception as e:
        logger.error(f"Error optimizing text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
async def generate_audio(request: GenerateRequest):
    try:
        logger.info(f"Generating Coqui audio for text: {request.text[:50]}...")
        tts_model = get_model()
        
        filename = f"output_{uuid.uuid4().hex[:8]}.wav"
        output_path = os.path.join("static", "audio", filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        audio_prompt_path = None
        if request.audio_prompt:
            audio_prompt_path = os.path.join("static", "uploads", request.audio_prompt)
            if not os.path.exists(audio_prompt_path):
                logger.warning(f"Audio prompt {audio_prompt_path} not found, using default voice.")
                audio_prompt_path = None

        # Coqui XTTS v2 requires a reference voice for cloning. 
        # If none provided, we'll use a sample if available, or error out.
        if not audio_prompt_path:
             # Default to the newly downloaded female American voice
             default_ref = "female_ref.wav"
             if os.path.exists(default_ref):
                 audio_prompt_path = default_ref
             else:
                 # Note: XTTS v2 MUST have a speaker_wav for the tts() method
                 logger.error("No reference voice provided and female_ref.wav not found.")
                 raise Exception("Please upload a reference voice or ensure female_ref.wav exists in the folder.")

        # Generate using Coqui API
        # language='en' is default, can be made dynamic later
        tts_model.tts_to_file(
            text=request.text,
            speaker_wav=audio_prompt_path,
            language="en",
            file_path=output_path
        )
        
        logger.info(f"Audio generated: {filename}")
        return {"audio_url": f"/audio/{filename}"}
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"Error generating audio:\n{error_detail}")
        raise HTTPException(status_code=500, detail=f"{str(e)}")

@app.post("/api/upload")
async def upload_audio(file: UploadFile = File(...)):
    try:
        filename = f"ref_{uuid.uuid4().hex[:8]}_{file.filename}"
        upload_path = os.path.join("static", "uploads", filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Reference audio uploaded: {filename}")
        return {"filename": filename}
    except Exception as e:
        logger.error(f"Error uploading audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/save")
async def save_text(request: TextRequest):
    try:
        filename = f"script_{uuid.uuid4().hex[:8]}.txt"
        filepath = os.path.join("saved_scripts", filename)
        os.makedirs("saved_scripts", exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(request.text)
            
        logger.info(f"Script saved to {filepath}")
        return {"message": "Saved successfully", "filename": filename}
    except Exception as e:
        logger.error(f"Error saving text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Static files
os.makedirs("static", exist_ok=True)
os.makedirs("static/audio", exist_ok=True)
app.mount("/audio", StaticFiles(directory="static/audio"), name="audio")
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
