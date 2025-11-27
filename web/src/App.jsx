import { useState, useEffect } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000';

function App() {
    const [file, setFile] = useState(null);
    const [pipeline, setPipeline] = useState('auto');
    const [hfToken, setHfToken] = useState('');
    const [taskId, setTaskId] = useState(null);
    const [status, setStatus] = useState(null);
    const [taskData, setTaskData] = useState(null);
    const [clips, setClips] = useState([]);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        if (e.target.files) {
            setFile(e.target.files[0]);
        }
    };

    const startProcessing = async () => {
        if (!file) return;
        setError(null);
        setStatus('uploading');

        try {
            // 1. Upload
            const formData = new FormData();
            formData.append('file', file);

            const uploadRes = await fetch(`${API_URL}/upload`, {
                method: 'POST',
                body: formData,
            });

            if (!uploadRes.ok) throw new Error('Upload failed');
            const { filename } = await uploadRes.json();

            // 2. Start Process
            const processRes = await fetch(`${API_URL}/process`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    video_filename: filename,
                    pipeline: pipeline,
                    hf_token: hfToken || null
                }),
            });

            if (!processRes.ok) throw new Error('Processing start failed');
            const { task_id } = await processRes.json();
            setTaskId(task_id);
            setStatus('queued');

        } catch (err) {
            setError(err.message);
            setStatus('failed');
        }
    };

    // Poll status
    useEffect(() => {
        if (!taskId || status === 'completed' || status === 'failed') return;

        const interval = setInterval(async () => {
            try {
                const res = await fetch(`${API_URL}/status/${taskId}`);
                const data = await res.json();
                setStatus(data.status);
                setTaskData(data);

                if (data.status === 'completed') {
                    fetchClips(taskId);
                } else if (data.status === 'failed') {
                    setError(data.error);
                }
            } catch (err) {
                console.error("Polling error", err);
            }
        }, 2000);

        return () => clearInterval(interval);
    }, [taskId, status]);

    const fetchClips = async (id) => {
        try {
            const res = await fetch(`${API_URL}/clips/${id}`);
            const data = await res.json();
            setClips(data.clips);
        } catch (err) {
            console.error("Fetch clips error", err);
        }
    };

    return (
        <div className="container">
            <h1>ClipCut MS</h1>
            <p>AI-Powered Video Segmentation Pipeline</p>

            {!taskId && (
                <div className="card">
                    <div className="upload-zone">
                        <input type="file" accept="video/*" onChange={handleFileChange} id="file-upload" hidden />
                        <label htmlFor="file-upload" style={{ cursor: 'pointer' }}>
                            {file ? `Selected: ${file.name}` : "Click to Select Video"}
                        </label>
                    </div>

                    <div className="controls">
                        <select value={pipeline} onChange={(e) => setPipeline(e.target.value)}>
                            <option value="auto">Auto-Detect (Smart)</option>
                            <option value="fast">Fast (WebRTC VAD)</option>
                            <option value="balanced">Balanced (Pyannote)</option>
                            <option value="pro">Pro (Forced Alignment)</option>
                        </select>

                        <input
                            type="text"
                            placeholder="HF Token (Optional)"
                            value={hfToken}
                            onChange={(e) => setHfToken(e.target.value)}
                        />
                    </div>

                    <button
                        className="primary"
                        onClick={startProcessing}
                        disabled={!file}
                    >
                        Start Processing
                    </button>
                </div>
            )}

            {taskId && (
                <div className="card">
                    <div className={`status-badge status-${status}`}>
                        Status: {status?.toUpperCase()}
                    </div>
                    {error && <p style={{ color: '#f87171' }}>{error}</p>}

                    {status !== 'completed' && status !== 'failed' && (
                        <p>Processing your video... This may take a while.</p>
                    )}
                </div>
            )}

            {status === 'completed' && taskData && (
                <div className="card" style={{ marginBottom: '2rem' }}>
                    <h3>Analysis Results</h3>
                    <div style={{ display: 'flex', gap: '2rem', justifyContent: 'center' }}>
                        <p><strong>Pipeline:</strong> {taskData.pipeline_used?.toUpperCase()}</p>
                        <p><strong>Speakers:</strong> {taskData.num_speakers}</p>
                    </div>
                </div>
            )}

            {clips.length > 0 && (
                <div className="grid">
                    {clips.map((clip) => (
                        <div key={clip} className="clip-card">
                            <video controls src={`${API_URL}/download/${taskId}/${clip}`} />
                            <p>{clip}</p>
                            <a href={`${API_URL}/download/${taskId}/${clip}`} download>
                                <button>Download</button>
                            </a>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

export default App
