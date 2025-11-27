from src.pipelines.base import VideoPipeline
from src.processing.asr import ASRProcessor
from src.processing.vad import VADProcessor
from src.processing.diarization import DiarizationProcessor
from src.processing.alignment import AlignmentProcessor
from typing import List, Dict, Any

class ProPipeline(VideoPipeline):
    def __init__(self, hf_token: str = None):
        self.vad = VADProcessor(method="pyannote")
        self.asr = ASRProcessor(model_size="large-v2", compute_type="int8")
        self.diarization = DiarizationProcessor(auth_token=hf_token)
        self.alignment = AlignmentProcessor(method="aeneas")

    def process(self, video_path: str, output_dir: str) -> List[Dict[str, Any]]:
        self.validate_input(video_path)
        audio_path = video_path
        
        try:
            print("--- Pro Pipeline ---")
            
            # 1. ASR
            print("Running ASR...")
            result = self.asr.transcribe(audio_path)
            segments = result["segments"]
            
            # 2. Diarization
            print("Running Diarization...")
            speaker_segments = self.diarization.process(audio_path)
            
            # 3. Merge Speakers
            if speaker_segments:
                print("Merging speaker labels...")
                segments = self.diarization.assign_speakers(segments, speaker_segments)
                
            # 4. Forced Alignment (Placeholder for now)
            # segments = self.alignment.align(audio_path, segments)
            
            return segments
        except Exception as e:
            print(f"Error in Pro Pipeline: {e}")
            import traceback
            traceback.print_exc()
            return []
