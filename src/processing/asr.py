import whisperx
import torch
from typing import Dict, Any

class ASRProcessor:
    def __init__(self, model_size: str = "small", device: str = "cuda", compute_type: str = "int8"):
        self.device = device if torch.cuda.is_available() else "cpu"
        self.compute_type = compute_type
        print(f"Loading WhisperX model: {model_size} on {self.device}...")
        self.model = whisperx.load_model(model_size, device=self.device, compute_type=self.compute_type)
        self.model_a = None
        self.metadata = None

    def transcribe(self, audio_path: str, batch_size: int = 16) -> Dict[str, Any]:
        """
        Transcribe audio and return segments with word-level timestamps.
        """
        print(f"Transcribing {audio_path}...")
        result = self.model.transcribe(audio_path, batch_size=batch_size)
        
        # Align whisper output
        if self.model_a is None:
             self.model_a, self.metadata = whisperx.load_align_model(language_code=result["language"], device=self.device)
        
        print("Aligning...")
        result = whisperx.align(result["segments"], self.model_a, self.metadata, audio_path, self.device, return_char_alignments=False)
        
        return result
