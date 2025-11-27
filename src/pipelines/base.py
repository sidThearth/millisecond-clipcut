from abc import ABC, abstractmethod
from typing import List, Dict, Any
import os

class VideoPipeline(ABC):
    """
    Abstract base class for all video processing pipelines.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    @abstractmethod
    def process(self, video_path: str, output_dir: str) -> List[Dict[str, Any]]:
        """
        Process the video and return a list of segments.
        
        Args:
            video_path: Path to the input video file.
            output_dir: Directory to save intermediate files or final clips.
            
        Returns:
            List of segments, where each segment is a dict with 'start', 'end', 'text', etc.
        """
        pass

    def validate_input(self, video_path: str) -> bool:
        """
        Basic validation of input video.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        return True
