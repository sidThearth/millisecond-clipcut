import whisperx
import json

# load WhisperX model
model = whisperx.load_model("small", device="cpu", compute_type="int8")
# change to "cuda" if GPU available

audio_file = r"C:\Users\Sid\Desktop\video\clipcut-ms\data\test.mp4"

print("Transcribing...")
result = model.transcribe(audio_file, batch_size=16)

print("\n=== Transcription Segments ===")
segments = result["segments"]   # <--- define segments here

for seg in segments:
    print(f"[{seg['start']:.2f} - {seg['end']:.2f}] {seg['text']}")

# save clean JSON
with open("segments.json", "w") as f:
    json.dump(segments, f, indent=2)

print("✅ Saved transcription to segments.json")
