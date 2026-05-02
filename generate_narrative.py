import torchaudio as ta
import torch
import os
from chatterbox.tts_turbo import ChatterboxTurboTTS

# Automatically detect device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load the Turbo model
print("Loading model...")
model = ChatterboxTurboTTS.from_pretrained(device=device)

# Read text from file
input_file = "narrative_with_tags.txt"
with open(input_file, "r", encoding="utf-8") as f:
    text = f.read()

print("Generating audio for narrative...")
# Generate audio (uses the default voice included with the model)
wav = model.generate(text)

output_file = "valentines_narrative.wav"
ta.save(output_file, wav, model.sr)
print(f"Audio successfully generated and saved to {output_file}")
