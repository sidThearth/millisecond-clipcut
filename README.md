# ClipCut MS 🎬✂️

**ClipCut MS** is an advanced, millisecond-accurate video processing system designed to automatically slice, transcribe, and analyze videos with state-of-the-art precision. It leverages **WhisperX** for forced alignment and **Pyannote** for speaker diarization to create perfectly timed video clips.

![UI Screenshot](https://via.placeholder.com/800x400?text=ClipCut+MS+Web+Interface)

## 🚀 Key Features

*   **3-Tier Processing Pipelines**:
    *   **⚡ FAST**: Optimized for speed. Uses Whisper Small + Diarization. (~0.08x RTF)
    *   **⚖️ BALANCED**: The gold standard. Uses Whisper Medium + Diarization. (~0.15x RTF)
    *   **🧠 PRO**: Maximum accuracy. Uses Whisper Large-v2 + Forced Alignment. (~0.30x RTF)
*   **🗣️ Mandatory Speaker Diarization**: Every pipeline automatically detects and labels speakers (e.g., "SPEAKER_01").
*   **✂️ Smart Cutting**: Automatically slices videos into sentence-level clips, ensuring no cut-off words.
*   **📊 Built-in Benchmarking**: Calculate **WER** (Word Error Rate), **Precision**, and **Recall** against ground truth transcripts.
*   **🌐 Dual Interface**: Full-featured **Web UI** (FastAPI + React/Vanilla JS) and powerful **CLI**.

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
Open your browser at `http://localhost:5173` (or the port shown in terminal).

### 2. Command Line Interface (CLI)
Process a video directly from the terminal:

```bash
python -m src.main --input data/video.mp4 --pipeline balanced --hf-token YOUR_HF_TOKEN
```

**Options:**
*   `--pipeline`: `fast`, `balanced`, `pro`, or `auto` (auto-selects based on audio noise).
*   `--output`: Directory to save clips (default: `output_clips`).

### 3. Benchmarking Tool
Evaluate the system's performance against a ground truth transcript:

```bash
python -m src.evaluation.benchmark --input data/test.mp4 --reference-text data/transcript.txt --pipeline pro
```
**Metrics Output:**
*   **Speedup / RTF**: Processing speed.
*   **WER**: Word Error Rate.
*   **Precision**: Accuracy of detected words.
*   **Recall**: Percentage of words correctly found.

## 🏗️ Technical Architecture

*   **ASR**: OpenAI Whisper (via WhisperX for alignment).
*   **Diarization**: Pyannote Audio 3.1.
*   **VAD**: WebRTCVAD / Pyannote VAD.
*   **Backend**: FastAPI.
*   **Frontend**: Vite + Vanilla JS/CSS.

## 📄 License
MIT License.
