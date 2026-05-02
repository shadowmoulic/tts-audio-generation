import torchaudio as ta
import torch
from chatterbox.tts_turbo import ChatterboxTurboTTS

# Automatically detect device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load the Turbo model
model = ChatterboxTurboTTS.from_pretrained(device=device)

# Generate with Paralinguistic Tags
text = "Hi there, Sarah here from MochaFone calling you back [chuckle], have you got one minute to chat about the billing issue?"

print("Generating audio...")
# Generate audio (without a reference clip it uses a default voice)
wav = model.generate(text)

output_file = "test-turbo-cpu.wav"
ta.save(output_file, wav, model.sr)
print(f"Audio saved to {output_file}")
