from src.pipelines.base import VideoPipeline
from src.processing.asr import ASRProcessor
from src.processing.vad import VADProcessor
from typing import List, Dict, Any
import os

class FastPipeline(VideoPipeline):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.asr = ASRProcessor(model_size="small", compute_type="int8")
        self.vad = VADProcessor(method="webrtcvad")

    def process(self, video_path: str, output_dir: str) -> List[Dict[str, Any]]:
        self.validate_input(video_path)
        
        # 1. Extract audio (simplified, assuming audio file exists or extracted)
        audio_path = video_path 
        
        # 2. VAD (Optional for Fast Path)
        # In Fast path, we trust Whisper timestamps mostly, but VAD can help filter non-speech
        
        # 3. ASR
        try:
            result = self.asr.transcribe(audio_path)
            segments = result["segments"]
        except Exception as e:
            print(f"Error in Fast Pipeline ASR: {e}")
            # Fallback or re-raise
            return []
        
        # 4. Return segments
        return segments
