# ClipCut MS 🎬✂️

**ClipCut MS** is an advanced, millisecond-accurate video processing system designed to automatically slice, transcribe, and analyze videos with state-of-the-art precision. It leverages **WhisperX** for forced alignment and **Pyannote** for speaker diarization to create perfectly timed video clips.

![UI Screenshot](https://via.placeholder.com/800x400?text=ClipCut+MS+Web+Interface)

## 🚀 Key Features

### 1. 🧠 Intelligent Pipelines
*   **⚡ FAST**: Optimized for speed. Uses Whisper Small + Diarization. (~0.08x RTF)
*   **⚖️ BALANCED**: The gold standard. Uses Whisper Medium + Diarization. (~0.15x RTF)
*   **💎 PRO**: Maximum accuracy. Uses Whisper Large-v2 + Forced Alignment. (~0.30x RTF)
    *   *Auto-Selection Logic*: The system analyzes audio SNR. If the file is noisy (<12dB) or contains keywords like "interview", "debate", or "music", it automatically forces **PRO** mode.

### 2. 🔄 Auto-Sync & Normalization
*   **Problem**: Many videos have Variable Frame Rates (VFR) causing audio drift.
*   **Solution**: The system automatically **normalizes** every input video to a constant 30 FPS and 44.1kHz audio before processing. This guarantees perfect lip-sync alignment.

### 3. ✂️ High-Quality Cutting Engine
*   **Frame-Perfect Cuts**: We do not use "stream copying" (which is fast but glitchy).
*   **Full Re-encoding**: Every clip is re-rendered frame-by-frame using `libx264` (CRF 18) to ensure smooth playback with no stuttering at the start or end.

### 4. 📊 Built-in Benchmarking
Evaluate the system's performance against a ground truth transcript using our built-in tool.

**Understanding the Metrics:**
*   **WER (Word Error Rate)**: The "Messiness Score". How much editing is needed? (Lower is better).
    *   Formula: `(Wrong Words + Missing Words + Extra Words) / Total Truth Words`
*   **Precision**: "Trustworthiness". Out of the words the AI wrote, how many were actually correct?
    *   Formula: `Correct Words / Total AI Output`
*   **Recall**: "Completeness". Out of the words in the transcript, how many did the AI find?
    *   Formula: `Correct Words / Total Truth Words`

**Example:**
*   *Truth*: "The cat sat."
*   *AI*: "The dog sat down."
*   *Result*: **WER: 66%** (Bad), **Precision: 50%**, **Recall: 66%**.

## 🛠️ Installation

### Prerequisites
*   **Python 3.8+**
*   **FFmpeg** (Must be added to system PATH)
*   **Hugging Face Token** (Required for Pyannote Diarization)

### Setup
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/sidThearth/millisecond-clipcut.git
    cd millisecond-clipcut
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up the Web UI (Frontend)**:
    ```bash
    cd web
    npm install
    ```

## 💻 Usage

### 1. Web Interface (Recommended)
Run the backend and frontend servers:

**Backend:**
```bash
python -m api.server
```

**Frontend:**
```bash
cd web
npm run dev
```
Open your browser at `http://localhost:5173`. You can now see your **Input Video**, **Analysis Stats**, and **Generated Clips** all in one place.

### 2. Command Line Interface (CLI)
Process a video directly from the terminal:

```bash
python -m src.main --input data/video.mp4 --pipeline balanced --hf-token YOUR_HF_TOKEN
```

### 3. Benchmarking Tool
Run the benchmark script to get WER, Precision, and Recall:

```bash
python -m src.evaluation.benchmark --input data/test.mp4 --reference-text data/transcript.txt --pipeline pro
```

## 🏗️ Technical Architecture

*   **ASR**: OpenAI Whisper (via WhisperX for alignment).
*   **Diarization**: Pyannote Audio 3.1.
*   **VAD**: WebRTCVAD / Pyannote VAD.
*   **Backend**: FastAPI.
*   **Frontend**: Vite + Vanilla JS/CSS.

## 📄 License
MIT License.
