import numpy as np
import subprocess
import os
import json
from typing import Tuple

class PipelineSelector:
    def __init__(self):
        pass

    def select(self, video_path: str) -> str:
        """
        Analyze video audio and return the recommended pipeline: 'fast', 'balanced', or 'pro'.
        """
        print(f"Analyzing {video_path} for pipeline selection...")
        
        # 1. Extract a sample of audio (first 60s)
        audio_sample = self._extract_audio_sample(video_path)
        if not audio_sample:
             print("Could not extract audio. Defaulting to 'balanced'.")
             return "balanced"

        # 2. Calculate SNR
        snr = self._calculate_snr(audio_sample)
        print(f"Estimated SNR: {snr:.2f} dB")

        # 3. Decision Logic
        # Very High SNR (> 30dB) -> Extremely clean -> Fast
        # Else -> Balanced (Default for most cases to ensure Diarization)
        # Low SNR (< 10dB) -> Noisy -> Pro
        
        if snr > 30:
            print("Very High SNR detected (>30dB). Recommending FAST pipeline.")
            return "fast"
        elif snr > 10:
            print("Moderate SNR detected. Recommending BALANCED pipeline.")
            return "balanced"
        else:
            print("Low SNR detected. Recommending PRO pipeline.")
            return "pro"

    def _extract_audio_sample(self, video_path: str, duration: int = 60) -> str:
        """
        Extracts the first `duration` seconds of audio to a temporary wav file.
        Returns path to wav file.
        """
        temp_audio = "temp_analysis.wav"
        try:
            # ffmpeg -i input -t 60 -ac 1 -ar 16000 temp.wav -y
            subprocess.run([
                "ffmpeg", "-i", video_path, "-t", str(duration), 
                "-ac", "1", "-ar", "16000", "-vn", 
                temp_audio, "-y"
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return temp_audio
        except subprocess.CalledProcessError:
            return None

    def _calculate_snr(self, audio_path: str) -> float:
        """
        Estimates SNR using a simple approach:
        Signal = power of speech segments (approx by high energy frames)
        Noise = power of non-speech segments (approx by low energy frames)
        """
        try:
            import scipy.io.wavfile as wav
            rate, data = wav.read(audio_path)
            
            # Normalize
            data = data.astype(np.float32)
            if np.max(np.abs(data)) > 0:
                data = data / np.max(np.abs(data))
            
            # Frame energy
            frame_size = int(rate * 0.02) # 20ms
            if len(data) < frame_size:
                return 0.0
                
            # Calculate energy of frames
            # Reshape to (num_frames, frame_size) - truncate extra samples
            num_frames = len(data) // frame_size
            frames = data[:num_frames * frame_size].reshape(num_frames, frame_size)
            frame_energy = np.sum(frames ** 2, axis=1)
            
            # Simple heuristic: 
            # Top 10% energy frames are "Signal"
            # Bottom 10% energy frames are "Noise" (assuming there is some silence)
            
            # Sort energy
            sorted_energy = np.sort(frame_energy)
            
            noise_power = np.mean(sorted_energy[:int(num_frames * 0.1)])
            signal_power = np.mean(sorted_energy[int(num_frames * 0.9):])
            
            if noise_power <= 0:
                return 100.0 # Infinite SNR
                
            snr = 10 * np.log10(signal_power / noise_power)
            return snr
            
        except Exception as e:
            print(f"Error calculating SNR: {e}")
            return 15.0 # Default to moderate
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)
