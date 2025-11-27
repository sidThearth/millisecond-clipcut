import argparse
import os
import json
from src.pipelines.fast import FastPipeline
from src.pipelines.balanced import BalancedPipeline
from src.pipelines.pro import ProPipeline
from src.cutting.smart_cut import SmartCutter

def main():
    parser = argparse.ArgumentParser(description="ClipCut-MS: 3-Tier Video Processing Pipeline")
    parser.add_argument("--input", required=True, help="Input video file path")
    parser.add_argument("--pipeline", choices=["fast", "balanced", "pro", "auto"], default="fast", help="Pipeline tier to use")
    parser.add_argument("--output", default="output_clips", help="Output directory for clips")
    parser.add_argument("--hf-token", help="Hugging Face Auth Token for Diarization (pyannote)", default=None)
    
    args = parser.parse_args()
    
    video_path = args.input
    pipeline_type = args.pipeline
    output_dir = args.output
    
    print(f"=== ClipCut-MS ===")
    print(f"Input: {video_path}")
    
    # Auto-Selection
    if pipeline_type == "auto":
        from src.processing.selector import PipelineSelector
        selector = PipelineSelector()
        pipeline_type = selector.select(video_path)
        print(f"Auto-Selected Pipeline: {pipeline_type.upper()}")
    
    print(f"Pipeline: {pipeline_type.upper()}")
    print(f"Output: {output_dir}")
    
    # Select Pipeline
    if pipeline_type == "fast":
        pipeline = FastPipeline()
    elif pipeline_type == "balanced":
        pipeline = BalancedPipeline(hf_token=args.hf_token)
    elif pipeline_type == "pro":
        pipeline = ProPipeline(hf_token=args.hf_token)
    else:
        raise ValueError("Invalid pipeline type")
        
    # Process Video
    try:
        segments = pipeline.process(video_path, output_dir)
        print(f"Found {len(segments)} segments.")
        
        # Save segments to JSON
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "segments.json"), "w") as f:
            json.dump(segments, f, indent=2)
            
        # Cut Clips
        cutter = SmartCutter(output_dir)
        cutter.cut_segments(video_path, segments)
        
        print("Done!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
