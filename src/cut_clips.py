import json
import ffmpeg
import os

INPUT_VIDEO = r"C:\Users\Sid\Desktop\video\clipcut-ms\data\test.mp4"   # replace with your actual video file
OUTPUT_DIR = "clips"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# load segments
with open("segments.json", "r") as f:
    segments = json.load(f)

for i, seg in enumerate(segments, start=1):
    start = seg["start"]
    end = seg["end"]
    out_file = os.path.join(OUTPUT_DIR, f"clip_{i:02d}.mp4")
    
    # Use ffmpeg to cut segment
    (
        ffmpeg
        .input(INPUT_VIDEO, ss=start, to=end)
        .output(out_file, c="copy")  # c="copy" = no re-encode (fast)
        .overwrite_output()
        .run()
    )
    print(f"Saved {out_file} [{start:.2f} - {end:.2f}]")
