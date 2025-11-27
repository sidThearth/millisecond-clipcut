from typing import List, Dict, Any
import os
import torch

class DiarizationProcessor:
    def __init__(self, auth_token: str = None):
        self.auth_token = auth_token
        self.pipeline = None
        
        if self.auth_token:
            try:
                from pyannote.audio import Pipeline
                print("Loading pyannote diarization pipeline...")
                self.pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=self.auth_token
                )
                if torch.cuda.is_available():
                    self.pipeline.to(torch.device("cuda"))
                    print("Diarization pipeline moved to CUDA.")
            except Exception as e:
                print(f"Failed to load pyannote pipeline: {e}")
                self.pipeline = None
        else:
            print("No HF token provided. Diarization will be skipped/mocked.")

    def _extract_audio(self, input_path: str) -> str:
        """
        Extracts audio to a temporary WAV file.
        """
        temp_audio = "temp_diarization.wav"
        try:
            import subprocess
            subprocess.run([
                "ffmpeg", "-i", input_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                temp_audio, "-y"
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return temp_audio
        except Exception as e:
            print(f"Failed to extract audio: {e}")
            return None

    def process(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Perform speaker diarization.
        Returns a list of segments with speaker labels.
        """
        if not self.pipeline:
            print("Diarization pipeline not available. Returning empty.")
            return []

        print(f"Running diarization on {audio_path}...")
        
        # Extract audio if needed (simple check or always convert for safety)
        temp_wav = self._extract_audio(audio_path)
        if not temp_wav:
            print("Could not extract audio for diarization.")
            return []
            
        try:
            diarization = self.pipeline(temp_wav)
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })
            print(f"Diarization complete. Found {len(segments)} segments.")
            return segments
        except Exception as e:
            print(f"Error during diarization: {e}")
            return []
        finally:
            if os.path.exists(temp_wav):
                try:
                    os.remove(temp_wav)
                except:
                    pass

    @staticmethod
    def assign_speakers(asr_segments: List[Dict[str, Any]], diarization_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Assign speaker labels to ASR segments based on overlap with diarization segments.
        """
        for seg in asr_segments:
            start = seg["start"]
            end = seg["end"]
            
            # Find overlapping diarization segments
            overlaps = []
            for d_seg in diarization_segments:
                d_start = d_seg["start"]
                d_end = d_seg["end"]
                
                # Calculate overlap
                overlap_start = max(start, d_start)
                overlap_end = min(end, d_end)
                overlap_duration = max(0, overlap_end - overlap_start)
                
                if overlap_duration > 0:
                    overlaps.append((d_seg["speaker"], overlap_duration))
            
            # Assign speaker with max overlap
            if overlaps:
                # Sort by duration desc
                overlaps.sort(key=lambda x: x[1], reverse=True)
                best_speaker = overlaps[0][0]
                seg["speaker"] = best_speaker
            else:
                seg["speaker"] = "UNKNOWN"
                
        return asr_segments
