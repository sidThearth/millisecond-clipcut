import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg
import textwrap

# Configuration
OUTPUT_FILENAME = "ClipCut_MS_Presentation.pdf"
IMAGE_PATH_ARCH = "uploaded_image_1764259388933.png"
IMAGE_PATH_FLOW = "pipeline_flowchart_1764259771683.png"
IMAGE_PATH_DIAR = "diarization_waveform_1764259808555.png"
IMAGE_PATH_ALIGN = "alignment_diagram_1764259829378.png"
IMAGE_PATH_CUT = "smart_cutting_concept_1764259864218.png"

# Slide Content
slides = [
    {
        "title": "ClipCut MS: AI-Powered Video Segmentation",
        "content": [
            " ",
            " ",
            "Automated Long-Form Video Segmentation System",
            " ",
            "Author: Sid",
            "Date: November 2025"
        ],
        "type": "title"
    },
    {
        "title": "1. Introduction",
        "content": [
            "• The exponential growth of video content creates a need for automated editing tools.",
            "• Manual editing of long-form videos (podcasts, interviews) is time-consuming and expensive.",
            "• ClipCut MS automates the process of slicing videos into coherent clips.",
            "• Leverages state-of-the-art AI for speech analysis and speaker identification."
        ]
    },
    {
        "title": "2. Problem Statement",
        "content": [
            "• **Inefficiency**: Manual extraction of highlights from hour-long videos takes hours.",
            "• **Inconsistency**: Human editors may miss key moments or cut at awkward times.",
            "• **Scalability**: Content creators cannot keep up with the demand for short-form content (Shorts/Reels/TikToks).",
            "• **Goal**: Develop a system that intelligently segments video based on semantic content and speaker turns."
        ]
    },
    {
        "title": "3. Literature Review (1/2)",
        "content": [
            "• **Voice Activity Detection (VAD)**:",
            "  - Traditional energy-based methods vs. Neural VADs (Silero, WebRTC).",
            "  - Neural models offer superior robustness in noisy environments.",
            "• **Speaker Diarization**:",
            "  - Clustering audio segments by speaker identity.",
            "  - Pyannote.audio is the current state-of-the-art for end-to-end diarization."
        ]
    },
    {
        "title": "3. Literature Review (2/2)",
        "content": [
            "• **Automatic Speech Recognition (ASR)**:",
            "  - OpenAI's Whisper has revolutionized ASR accuracy.",
            "  - WhisperX introduces forced alignment for word-level timestamp precision.",
            "• **Video Segmentation**:",
            "  - Existing tools often rely on visual scene changes rather than audio context.",
            "  - ClipCut MS focuses on audio-driven segmentation for speech-heavy content."
        ]
    },
    {
        "title": "4. System Overview",
        "content": [], 
        "image": IMAGE_PATH_FLOW
    },
    {
        "title": "5. Model Architecture",
        "content": [], 
        "image": IMAGE_PATH_ARCH
    },
    {
        "title": "6. Key Components: VAD & Diarization",
        "content": [
            "• **Voice Activity Detection (VAD)**:",
            "  - Filters out silence and non-speech noise.",
            "• **Speaker Diarization (Pyannote 3.1)**:",
            "  - Answers 'Who spoke when?'.",
            "  - Assigns labels (SPEAKER_00, SPEAKER_01) to audio segments."
        ],
        "image": IMAGE_PATH_DIAR,
        "image_pos": [0.1, 0.1, 0.8, 0.4] # Custom position for mixed content
    },
    {
        "title": "7. Key Components: ASR & Alignment",
        "content": [
            "• **Transcription (WhisperX)**:",
            "  - Uses Faster-Whisper (CTranslate2) for speed.",
            "• **Forced Alignment (Wav2Vec2)**:",
            "  - Aligns transcript text with audio waveform.",
            "  - Provides exact start and end timestamps for every word."
        ],
        "image": IMAGE_PATH_ALIGN,
        "image_pos": [0.1, 0.1, 0.8, 0.4]
    },
    {
        "title": "8. Intelligent Pipeline Selection",
        "content": [
            "• System analyzes Signal-to-Noise Ratio (SNR) of the first 60s.",
            "• **Fast Pipeline** (SNR > 30dB):",
            "  - Uses WebRTC VAD. No Diarization. Speed priority.",
            "• **Balanced Pipeline** (10dB < SNR < 30dB):",
            "  - Uses Pyannote Diarization + WhisperX Medium.",
            "• **Pro Pipeline** (SNR < 10dB):",
            "  - Uses WhisperX Large-v2 + Wav2Vec2 Alignment.",
            "  - Maximum precision for noisy audio."
        ]
    },
    {
        "title": "9. Smart Cutting Logic",
        "content": [
             "• **Lossless Cutting**:",
             "  - Uses FFmpeg to cut video streams without re-encoding.",
             "  - Preserves original video quality.",
             "• **Keyframe Adjustment**:",
             "  - Adjusts cut points to nearest keyframes to prevent corruption."
        ],
        "image": IMAGE_PATH_CUT,
        "image_pos": [0.1, 0.1, 0.8, 0.4]
    },
    {
        "title": "10. Evaluation Metrics",
        "content": [
            "• **Speedup**: Ratio of Video Duration to Processing Time.",
            "• **Real-Time Factor (RTF)**: Processing Time / Video Duration.",
            "• **Word Error Rate (WER)**: Levenshtein distance between hypothesis and reference text.",
            "• **5-Dup**: Count of 5-gram repetitions (detects hallucinations).",
            "• **Insertion Error Rate (IER)**: Percentage of extra words added by the model."
        ]
    },
    {
        "title": "11. Results",
        "content": [
            "• **Performance Benchmark (Balanced Pipeline)**:",
            "  - Speedup: ~0.4x (on CPU/Standard GPU)",
            "  - RTF: ~2.6",
            "  - WER: < 10% on clean audio",
            "• **Quality**:",
            "  - 5-Dup metric successfully flags hallucination loops.",
            "  - Smart cutting ensures frame-accurate transitions."
        ]
    },
    {
        "title": "12. Demo Clip",
        "content": [
            " ",
            " ",
            " ",
            "[ INSERT DEMO VIDEO CLIP HERE ]",
            " ",
            " ",
            "Demonstrating: Input -> Processing -> Output Clips"
        ],
        "type": "center"
    },
    {
        "title": "13. Conclusion & Future Work",
        "content": [
            "• **Conclusion**:",
            "  - ClipCut MS successfully automates video segmentation.",
            "  - Hybrid pipeline approach balances speed and accuracy.",
            "• **Future Work**:",
            "  - Integration of Visual Scene Detection.",
            "  - Real-time streaming support.",
            "  - Fine-tuning Whisper models for specific accents."
        ]
    },
    {
        "title": "14. References",
        "content": [
            "1. A. Radford et al., 'Robust Speech Recognition via Large-Scale Weak Supervision', OpenAI, 2022.",
            "2. H. Bredin et al., 'Pyannote.audio: neural building blocks for speaker diarization', ICASSP 2020.",
            "3. Bain et al., 'WhisperX: Time-Accurate Speech Transcription of Long-Form Audio', 2023.",
            "4. IEEE Standard for Software Test Documentation (IEEE Std 829-2008)."
        ],
        "fontsize": 10
    }
]

def create_presentation():
    with PdfPages(OUTPUT_FILENAME) as pdf:
        for i, slide in enumerate(slides):
            fig = plt.figure(figsize=(16, 9)) # 16:9 Aspect Ratio
            
            # Background
            fig.patch.set_facecolor('white')
            
            # Title
            plt.text(0.05, 0.90, slide['title'], fontsize=24, fontweight='bold', color='#003366')
            
            # Content
            y_pos = 0.80
            
            # Check for mixed content (Text + Image)
            if 'image' in slide and 'content' in slide and slide['content']:
                 # Render Text
                fontsize = slide.get('fontsize', 16)
                for line in slide['content']:
                    wrapped_lines = textwrap.wrap(line, width=90)
                    for wrapped_line in wrapped_lines:
                        plt.text(0.05, y_pos, wrapped_line, fontsize=fontsize, ha='left')
                        y_pos -= 0.05
                
                # Render Image at custom position
                try:
                    img = mpimg.imread(slide['image'])
                    pos = slide.get('image_pos', [0.1, 0.1, 0.8, 0.4]) # Default bottom half
                    ax_img = fig.add_axes(pos)
                    ax_img.imshow(img)
                    ax_img.axis('off')
                except Exception as e:
                    plt.text(0.5, 0.3, f"Error loading image: {e}", fontsize=14, ha='center')

            # Check for Image Only
            elif 'image' in slide:
                try:
                    img = mpimg.imread(slide['image'])
                    ax_img = fig.add_axes([0.1, 0.1, 0.8, 0.7]) # Full slide body
                    ax_img.imshow(img)
                    ax_img.axis('off')
                except Exception as e:
                    plt.text(0.5, 0.5, f"Error loading image: {e}", fontsize=14, ha='center')
            
            # Text Only
            else:
                fontsize = slide.get('fontsize', 16)
                align = 'center' if slide.get('type') == 'center' or slide.get('type') == 'title' else 'left'
                x_pos = 0.5 if align == 'center' else 0.05
                
                for line in slide['content']:
                    wrapped_lines = textwrap.wrap(line, width=90)
                    for wrapped_line in wrapped_lines:
                        plt.text(x_pos, y_pos, wrapped_line, fontsize=fontsize, ha=align)
                        y_pos -= 0.05

            # Footer
            plt.text(0.95, 0.02, f"Page {i+1}", fontsize=10, ha='right', color='gray')
            plt.text(0.05, 0.02, "ClipCut MS - IEEE Format Presentation", fontsize=10, ha='left', color='gray')
            
            plt.axis('off')
            pdf.savefig(fig)
            plt.close()

    print(f"Presentation saved to {OUTPUT_FILENAME}")

if __name__ == "__main__":
    create_presentation()
