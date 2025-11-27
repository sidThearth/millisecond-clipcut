import ffmpeg
import os
import subprocess
import json
from typing import List, Dict, Any

class SmartCutter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _get_keyframes(self, video_path: str) -> List[float]:
        """
        Get timestamps of all I-frames (keyframes).
        """
        try:
            # ffprobe to get keyframe timestamps
            cmd = [
                "ffprobe",
                "-select_streams", "v",
                "-skip_frame", "nokey",
                "-show_entries", "frame=pkt_pts_time",
                "-of", "csv=print_section=0",
                video_path
            ]
            
            # Run ffprobe
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8")
            keyframes = []
            for line in output.splitlines():
                if line.strip():
                    try:
                        keyframes.append(float(line.strip()))
                    except ValueError:
                        pass
            return sorted(keyframes)
        except Exception as e:
            print(f"Warning: Could not extract keyframes ({e}). Falling back to full re-encode.")
            return []

    def cut_segments(self, video_path: str, segments: List[Dict[str, Any]]):
        """
        Cut video into segments using smart cutting (micro re-encoding).
        """
        print(f"Analyzing keyframes for {video_path}...")
        keyframes = self._get_keyframes(video_path)
        print(f"Found {len(keyframes)} keyframes.")
        
        for i, seg in enumerate(segments):
            start = seg["start"]
            end = seg["end"]
            text = seg.get("text", "").strip()
            out_file = os.path.join(self.output_dir, f"clip_{i:03d}.mp4")
            
            print(f"Processing clip {i}: {start:.2f}-{end:.2f}")
            
            # Strategy:
            # Find keyframes strictly inside (start, end)
            relevant_keys = [k for k in keyframes if start < k < end]
            
            # We need at least 2 keyframes to have a "Body" to copy?
            # Actually, even 1 keyframe inside allows us to copy from that keyframe to... wait.
            # Copying requires starting at a keyframe.
            # So Body must start at K1 and end at K2 (or end of video if we copy to end, but here we cut).
            # If we have K1, K2 inside:
            # Head: start -> K1 (Re-encode)
            # Body: K1 -> K2 (Copy)
            # Tail: K2 -> end (Re-encode)
            
            # If we only have 1 keyframe K1 inside:
            # Head: start -> K1 (Re-encode)
            # Tail: K1 -> end (Re-encode) -> This is basically full re-encode split in two, not much gain.
            # Actually, if K1 is inside, we can copy from K1 to... where?
            # Copying must end at a frame.
            
            # For simplicity and robustness:
            # We only use Smart Cut if we can copy a significant chunk.
            # Let's say we need at least 2 keyframes to define a body.
            
            if len(relevant_keys) >= 2:
                k_first = relevant_keys[0]
                k_last = relevant_keys[-1]
                
                # Check if body is worth copying (e.g. > 1 second)
                if k_last - k_first > 1.0:
                    print(f"  Strategy: Smart Cut (Head: {start:.2f}-{k_first:.2f}, Body: {k_first:.2f}-{k_last:.2f}, Tail: {k_last:.2f}-{end:.2f})")
                    self._smart_cut(video_path, out_file, start, end, k_first, k_last)
                    continue

            # Fallback
            print(f"  Strategy: Full Re-encode")
            self._reencode_cut(video_path, out_file, start, end)

    def _reencode_cut(self, video_path, out_file, start, end):
        try:
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ss", str(start),
                "-to", str(end),
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-c:a", "aac", "-b:a", "128k",
                os.path.abspath(out_file),
                "-y"
            ]
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Error cutting clip: {e.stderr.decode('utf8') if e.stderr else e}")
        except Exception as e:
            print(f"Error cutting clip: {e}")

    def _smart_cut(self, video_path, out_file, start, end, k_first, k_last):
        head_file = out_file.replace(".mp4", "_head.mp4")
        body_file = out_file.replace(".mp4", "_body.mp4")
        tail_file = out_file.replace(".mp4", "_tail.mp4")
        list_file = out_file.replace(".mp4", "_list.txt")
        
        try:
            # Head (Re-encode)
            subprocess.run([
                "ffmpeg", "-i", video_path, "-ss", str(start), "-to", str(k_first),
                "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "aac", "-b:a", "128k",
                head_file, "-y"
            ], check=True, capture_output=True)
            
            # Body (Copy)
            subprocess.run([
                "ffmpeg", "-ss", str(k_first), "-i", video_path, "-t", str(k_last - k_first),
                "-c", "copy",
                body_file, "-y"
            ], check=True, capture_output=True)
            
            # Tail (Re-encode)
            subprocess.run([
                "ffmpeg", "-i", video_path, "-ss", str(k_last), "-to", str(end),
                "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "aac", "-b:a", "128k",
                tail_file, "-y"
            ], check=True, capture_output=True)
            
            # Concat
            with open(list_file, "w") as f:
                f.write(f"file '{os.path.abspath(head_file)}'\n")
                f.write(f"file '{os.path.abspath(body_file)}'\n")
                f.write(f"file '{os.path.abspath(tail_file)}'\n")
            
            subprocess.run([
                "ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file,
                "-c", "copy", out_file, "-y"
            ], check=True, capture_output=True)
            
        except subprocess.CalledProcessError as e:
            print(f"Smart cut failed ({e.stderr.decode('utf8') if e.stderr else e}), falling back to full re-encode.")
            self._reencode_cut(video_path, out_file, start, end)
        except Exception as e:
             print(f"Smart cut failed ({e}), falling back to full re-encode.")
             self._reencode_cut(video_path, out_file, start, end)
        finally:
            # Cleanup
            for f in [head_file, body_file, tail_file, list_file]:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except:
                        pass
