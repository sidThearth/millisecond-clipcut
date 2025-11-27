# ClipCut MS - Technical Overview & Presentation Guide

## 1. Project Overview
**ClipCut MS** is an AI-powered video segmentation system designed to automatically slice long-form videos into coherent clips based on speech activity and speaker identity.

**Core Flow:**
`Video Input` -> `Audio Analysis (SNR)` -> `Pipeline Selection` -> `AI Processing` -> `Smart Cutting` -> `Clips`

---

## 2. The "Brain": Intelligent Pipeline Selection
The system automatically decides the best processing strategy using the **Pipeline Selector**.

*   **Logic**: It extracts the first 60 seconds of audio and calculates the **Signal-to-Noise Ratio (SNR)**.
*   **Thresholds**:
    *   **High SNR (> 30dB)**: Extremely clean, studio audio. -> Selects **FAST**.
    *   **Moderate/Low SNR (< 30dB)**: Normal or noisy audio. -> Selects **BALANCED** (Default).

---

## 3. The Pipelines (Processing Engines)

### A. FAST Pipeline (Speed Priority)
*   **Best for**: Single speaker, studio quality, rapid results.
*   **Mechanism**: Uses **WebRTC VAD** (Voice Activity Detection) to find speech chunks.
*   **Trade-off**: No Speaker Diarization (cannot tell *who* is speaking).
*   **Speed**: Extremely fast (~0.05 RTF).

### B. BALANCED Pipeline (The Standard)
*   **Best for**: Podcasts, interviews, meetings (Multi-speaker).
*   **Mechanism**:
    1.  **Diarization**: Uses **Pyannote 3.1** to identify speakers (Speaker_00, Speaker_01).
    2.  **ASR**: Uses **WhisperX (Medium)** for transcription.
*   **Trade-off**: Slower than Fast, but provides speaker labels.

### C. PRO Pipeline (Maximum Precision)
*   **Best for**: Noisy environments, academic transcription, precise word-level cuts.
*   **Mechanism**:
    1.  **Diarization**: Pyannote 3.1.
    2.  **ASR**: **WhisperX (Large-v2)** for highest accuracy.
    3.  **Alignment**: Uses **Wav2Vec2** forced alignment to get exact start/end times for every word.

---

## 4. Under the Hood: The AI Models

| Component | Model / Library | Purpose |
| :--- | :--- | :--- |
| **VAD** | **Silero VAD / WebRTC** | Detects *when* someone is speaking (ignores silence). |
| **Diarization** | **Pyannote 3.1** | "Who spoke when?" (Speaker Clustering). |
| **Transcription** | **Faster-Whisper (WhisperX)** | Converts speech to text (CTranslate2 backend). |
| **Alignment** | **Wav2Vec2** | Aligns text to audio waveforms for frame-perfect timestamps. |
| **Cutting** | **FFmpeg (Smart Cut)** | Physically cuts video without re-encoding (Keyframe adjustment). |

---

## 5. Evaluation Metrics (For Benchmarking)

*   **Speedup**: How many times faster than real-time processing is (e.g., 10x).
*   **WER (Word Error Rate)**: Percentage of incorrect words compared to a human transcript.
*   **5-Dup**: Detects "hallucinations" (AI repeating phrases in a loop).

---

## 6. Standard Benchmarks (AMI & TED-LIUM)
To scientifically prove the system's accuracy, we compare it against standard datasets used in research (like the WhisperX paper).

### Why use them?
*   **TED-LIUM 3**: Contains long-form TED talks. It is the gold standard for testing **ASR (Transcription)** accuracy.
*   **AMI Corpus**: Contains meeting recordings with multiple speakers. It is the gold standard for testing **Diarization (Speaker ID)**.

### How to use with ClipCut MS?
Since these are *audio* datasets and ClipCut MS is a *video* tool:
1.  **Convert**: Convert the benchmark audio to a "dummy" video (black screen) using FFmpeg.
    ```bash
    ffmpeg -f lavfi -i color=c=black:s=1280x720:r=5 -i input_audio.wav -shortest -c:v libx264 -c:a copy input_video.mp4
    ```
2.  **Run Benchmark**:
    ```bash
    python -m src.evaluation.benchmark --input input_video.mp4 --reference-text ground_truth.txt
    ```
3.  **Result**: You get a WER/DER score that is directly comparable to academic papers.
