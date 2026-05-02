import torch
import torchaudio
try:
    from chatterbox.tts_turbo import ChatterboxTurboTTS
    print("ChatterboxTurboTTS imported successfully")
except ImportError as e:
    print(f"Error importing ChatterboxTurboTTS: {e}")

try:
    from chatterbox.tts import ChatterboxTTS
    print("ChatterboxTTS imported successfully")
except ImportError as e:
    print(f"Error importing ChatterboxTTS: {e}")

print(f"Torch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Current device: {torch.cuda.get_device_name(0)}")
