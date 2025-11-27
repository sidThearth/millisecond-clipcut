import time
import os
import subprocess
import argparse
import json
from typing import Dict, Any, List
from src.pipelines.balanced import BalancedPipeline
from src.pipelines.pro import ProPipeline
from src.utils.media import get_video_duration

def calculate_wer(reference: str, hypothesis: str) -> float:
    try:
        import jiwer
        return jiwer.wer(reference, hypothesis)
    except ImportError:
        print("jiwer not installed. Skipping WER.")
        return -1.0

def calculate_der(reference_rttm: str, hypothesis_rttm: str) -> float:
    try:
        from pyannote.metrics.diarization import DiarizationErrorRate
        from pyannote.core import Segment, Annotation
        # This is a simplified placeholder. Real DER calc requires parsing RTTM files into Annotations.
        # For now, we will just check if the library exists.
        return 0.0 
    except ImportError:
        print("pyannote.metrics not installed. Skipping DER.")
        return -1.0

def run_benchmark(video_path: str, pipeline_type: str = "balanced", hf_token: str = None, reference_text: str = None):
    print(f"=== Benchmarking {pipeline_type.upper()} Pipeline ===")
    print(f"Input: {video_path}")
    
    # Check if input is audio and convert to temp video if needed
    temp_video = None
    if video_path.lower().endswith(('.wav', '.mp3', '.flac', '.m4a')):
        print("Audio file detected. Converting to temporary video for processing...")
        temp_video = f"temp_benchmark_{int(time.time())}.mp4"
        try:
            # Create black video with audio
            subprocess.run([
                "ffmpeg", "-f", "lavfi", "-i", "color=c=black:s=1280x720:r=5",
                "-i", video_path, "-shortest", "-c:v", "libx264", "-preset", "ultrafast",
                "-c:a", "aac", temp_video, "-y"
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            video_path = temp_video
            print(f"Created temporary video: {temp_video}")
        except Exception as e:
            print(f"Failed to convert audio to video: {e}")
            return

    # 1. Measure Duration
    duration = get_video_duration(video_path)
    print(f"Video Duration: {duration:.2f}s")

    # 2. Init Pipeline
    if pipeline_type == "balanced":
        pipeline = BalancedPipeline(hf_token=hf_token)
    elif pipeline_type == "pro":
        pipeline = ProPipeline(hf_token=hf_token)
    else:
        raise ValueError("Only balanced and pro supported for benchmark")

    # 3. Run & Time
    start_time = time.time()
    output_dir = f"benchmark_output_{int(start_time)}"
    os.makedirs(output_dir, exist_ok=True)
    
    segments = pipeline.process(video_path, output_dir)
    end_time = time.time()
    
    processing_time = end_time - start_time
    rtf = processing_time / duration if duration > 0 else 0
    speedup = duration / processing_time if processing_time > 0 else 0
    
    print("\n=== Results ===")
    print(f"Processing Time: {processing_time:.2f}s")
    print(f"Speedup: {speedup:.2f}x (Higher is better)")
    print(f"Real-Time Factor (RTF): {rtf:.4f} (Lower is better)")
    print(f"Segments Found: {len(segments)}")
    
    # 5-Dup (Hallucination Check)
    all_text = " ".join([s.get("text", "").strip() for s in segments])
    words = all_text.split()
    if len(words) >= 5:
        ngrams = zip(*[words[i:] for i in range(5)])
        ngram_counts = {}
        for ng in ngrams:
            ngram_counts[ng] = ngram_counts.get(ng, 0) + 1
        num_dups = sum(count - 1 for count in ngram_counts.values() if count > 1)
    else:
        num_dups = 0

    # Metrics Dictionary
    metrics = {
        "Speedup": f"{speedup:.1f}x",
        "RTF": f"{rtf:.3f}",
        "5-Dup": num_dups,
        "WER": "N/A",
        "IER": "N/A"
    }

    # 4. WER & IER (Optional)
    if reference_text:
        # Check if it's a file path
        if os.path.exists(reference_text):
            try:
                with open(reference_text, "r", encoding="utf-8") as f:
                    reference_text = f.read().strip()
                print(f"Loaded reference text from file ({len(reference_text)} chars).")
            except Exception as e:
                print(f"Failed to read reference file: {e}")
        
        try:
            import jiwer
            out = jiwer.process_words(reference_text, all_text)
            metrics["WER"] = f"{out.wer * 100:.1f}"
            # IER = Insertions / N
            # jiwer output has 'insertions' count
            # We need N (number of words in reference)
            N = len(reference_text.split())
            if N > 0:
                ier = out.insertions / N
                metrics["IER"] = f"{ier * 100:.1f}"
        except ImportError:
            print("jiwer not installed. Cannot calculate WER/IER.")
        except Exception as e:
            print(f"Error calculating WER/IER: {e}")

    # Print Table
    print("\n" + "="*65)
    print(f"{'Metric':<15} | {'Value':<15} | {'Description':<30}")
    print("-" * 65)
    print(f"{'Speedup':<15} | {metrics['Speedup']:<15} | {'Higher is better'}")
    print(f"{'RTF':<15} | {metrics['RTF']:<15} | {'Lower is better'}")
    print(f"{'5-Dup':<15} | {metrics['5-Dup']:<15} | {'Hallucinations (Lower is better)'}")
    print(f"{'WER (%)':<15} | {metrics['WER']:<15} | {'Word Error Rate (Lower is better)'}")
    print(f"{(metrics['IER']):<15} | {'Insertion Error Rate'}")
    print("="*65 + "\n")

    # Cleanup temp video
    if temp_video and os.path.exists(temp_video):
        os.remove(temp_video)
        print("Cleaned up temporary video.")
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input video")
    parser.add_argument("--pipeline", default="balanced", choices=["balanced", "pro"])
    parser.add_argument("--hf-token", help="Hugging Face Token")
    parser.add_argument("--reference-text", help="Ground truth text for WER")
    
    args = parser.parse_args()
    
    run_benchmark(args.input, args.pipeline, args.hf_token, args.reference_text)
