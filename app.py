"""
Professional Audio Transcription Tool - Streamlit UI
Enterprise-grade web interface with system auto-detection
Ready for GitHub deployment
"""

import streamlit as st
from pathlib import Path
import time
from utils import (
    get_audio_files,
    convert_mp4_to_mp3,
    transcribe_audio,
    get_file_size,
    check_gpu_available,
    validate_ffmpeg,
    get_system_info
)

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Professional Audio Transcriber",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== PROFESSIONAL CSS ====================
st.markdown("""
<style>
    /* Dark professional theme */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #151b2f 0%, #0a0e27 100%);
        border-right: 1px solid #2a3f5f;
    }
    
    /* Header styling */
    .header-title {
        text-align: center;
        padding: 2.5rem 2rem;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(30, 64, 175, 0.2);
        border: 1px solid rgba(59, 130, 246, 0.5);
    }
    
    .header-title h1 {
        color: white;
        font-size: 2.8em;
        margin: 0;
        font-weight: 700;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    .header-title p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1em;
        margin: 0.5rem 0 0 0;
        font-weight: 300;
    }
    
    /* System info card */
    .system-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%);
        padding: 1.5rem;
        border-radius: 14px;
        border: 1px solid rgba(59, 130, 246, 0.3);
        margin: 1.5rem 0;
    }
    
    .system-card h3 {
        color: #3b82f6;
        font-size: 1.1em;
        margin-top: 0;
        font-weight: 600;
    }
    
    .system-stat {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        color: rgba(255, 255, 255, 0.85);
        font-size: 0.95em;
        border-bottom: 1px solid rgba(59, 130, 246, 0.15);
    }
    
    .system-stat:last-child {
        border-bottom: none;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        font-size: 1.1em;
        font-weight: 600;
        padding: 1.2rem 2rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 6px 20px rgba(30, 64, 175, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(30, 64, 175, 0.4);
    }
    
    /* Status boxes */
    .status-success {
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid #22c55e;
        border-radius: 10px;
        padding: 1.2rem;
        color: #22c55e;
        margin: 1rem 0;
    }
    
    .status-error {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid #ef4444;
        border-radius: 10px;
        padding: 1.2rem;
        color: #ef4444;
        margin: 1rem 0;
    }
    
    .status-warning {
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid #f59e0b;
        border-radius: 10px;
        padding: 1.2rem;
        color: #f59e0b;
        margin: 1rem 0;
    }
    
    .status-info {
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid #3b82f6;
        border-radius: 10px;
        padding: 1.2rem;
        color: #93c5fd;
        margin: 1rem 0;
    }
    
    /* Transcript box */
    .transcript-box {
        background: #0a0e27;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #2a3f5f;
        max-height: 500px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        color: #e0e7ff;
        line-height: 1.8;
        font-size: 0.95em;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
    }
    
    /* File info card */
    .info-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(59, 130, 246, 0.3);
        margin: 1rem 0;
    }
    
    .info-card h4 {
        color: #3b82f6;
        margin-top: 0;
    }
    
    /* Sidebar styling */
    .sidebar-section {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(37, 99, 235, 0.02) 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(59, 130, 246, 0.2);
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== INITIALIZE SESSION STATE ====================
if 'transcription_done' not in st.session_state:
    st.session_state.transcription_done = False
if 'transcript_text' not in st.session_state:
    st.session_state.transcript_text = ""
if 'output_files' not in st.session_state:
    st.session_state.output_files = {}

# ==================== PATHS ====================
BASE_DIR = Path(r"C:\Users\LKK\Desktop\Transcript Generator")
INPUT_DIR = BASE_DIR / "Input"
OUTPUT_DIR = BASE_DIR / "Output"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==================== HEADER ====================
st.markdown("""
<div class="header-title">
    <h1>🎙️ Professional Audio Transcriber</h1>
    <p>Enterprise-grade speech-to-text powered by OpenAI Whisper</p>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR: SYSTEM INFORMATION ====================
with st.sidebar:
    st.markdown("### 💻 System Information")
    
    sys_info = get_system_info()
    
    with st.expander("🖥️ System Specs", expanded=True):
        st.markdown(f"""
        <div class="system-card">
            <div class="system-stat">
                <span><strong>OS</strong></span>
                <span>{sys_info.get('os')}</span>
            </div>
            <div class="system-stat">
                <span><strong>CPU Cores</strong></span>
                <span>{sys_info.get('cpu_count')} cores</span>
            </div>
            <div class="system-stat">
                <span><strong>CPU Speed</strong></span>
                <span>{sys_info.get('cpu_freq')}</span>
            </div>
            <div class="system-stat">
                <span><strong>Total RAM</strong></span>
                <span>{sys_info.get('ram_total')}</span>
            </div>
            <div class="system-stat">
                <span><strong>Available RAM</strong></span>
                <span>{sys_info.get('ram_available')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("🚀 GPU Information", expanded=True):
        if sys_info.get('gpu_available'):
            st.markdown(f"""
            <div class="system-card">
                <div class="system-stat" style="border-bottom: none;">
                    <span style="color: #22c55e;"><strong>✅ GPU Enabled</strong></span>
                </div>
                <div class="system-stat">
                    <span><strong>GPU</strong></span>
                    <span>{sys_info.get('gpu_name')}</span>
                </div>
                <div class="system-stat">
                    <span><strong>VRAM</strong></span>
                    <span>{sys_info.get('gpu_memory')}</span>
                </div>
                <div class="system-stat">
                    <span><strong>CUDA</strong></span>
                    <span>v{sys_info.get('cuda_version')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="system-card">
                <div class="system-stat" style="border-bottom: none; color: #f59e0b;">
                    <strong>⚠️ GPU Not Available</strong>
                </div>
                <p style="font-size: 0.9em; color: rgba(255, 255, 255, 0.7); margin-top: 0.5rem;">
                    Running in CPU mode. Processing will be slower.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # ==================== FILE SELECTION ====================
    st.markdown("### 📁 Audio File")
    audio_files = get_audio_files(INPUT_DIR)
    
    if not audio_files:
        st.warning("⚠️ No audio files found in Input folder")
        st.info(f"Place audio files in:\n\n`{INPUT_DIR}`")
        selected_file = None
    else:
        selected_file = st.selectbox(
            "Select audio file",
            audio_files,
            format_func=lambda x: f"🎵 {x}"
        )
    
    st.divider()
    
    # ==================== LANGUAGE SELECTION ====================
    st.markdown("### 🌍 Language")
    language_map = {
        "Auto-Detect (Recommended)": None,
        "English": "en",
        "Chinese (Mandarin)": "zh",
        "Cantonese": "yue",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Japanese": "ja",
        "Korean": "ko"
    }
    
    selected_language = st.radio(
        "Select language",
        list(language_map.keys()),
        index=0,
        help="Auto-detect usually works best"
    )
    
    language_code = language_map[selected_language]
    
    st.divider()
    
    # ==================== SETTINGS ====================
    st.markdown("### ⚙️ Settings")
    if not validate_ffmpeg():
        st.warning("❌ FFmpeg not found - MP4 conversion unavailable")
    
    st.info("""
    **Transcription Model**: Turbo
    - ⚡ Optimized for speed
    - 📊 ~95% accuracy
    - 🎯 Best for most use cases
    """)

# ==================== MAIN CONTENT ====================
if selected_file:
    file_path = INPUT_DIR / selected_file
    file_size = get_file_size(file_path)
    
    st.markdown(f"""
    <div class="info-card">
        <h4>📄 File Information</h4>
        <p><strong>Name:</strong> {selected_file}</p>
        <p><strong>Size:</strong> {file_size}</p>
        <p><strong>Language:</strong> {selected_language}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        start_button = st.button("🚀 Start Transcription", type="primary", use_container_width=True)
    
    if start_button:
        st.session_state.transcription_done = False
        st.session_state.transcript_text = ""
        start_time = time.time()
        
        try:
            # MP4 Conversion
            if file_path.suffix.lower() == '.mp4':
                st.markdown("### 🔄 Converting MP4 to MP3...")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                mp3_path = OUTPUT_DIR / f"{file_path.stem}_audio.mp3"
                
                def update_progress(percent):
                    progress_bar.progress(percent / 100)
                    status_text.text(f"Conversion: {percent}%")
                
                convert_mp4_to_mp3(str(file_path), str(mp3_path), update_progress)
                
                st.markdown('<div class="status-success">✅ MP3 conversion complete</div>', unsafe_allow_html=True)
                audio_file_path = mp3_path
            else:
                audio_file_path = file_path
            
            # Transcription
            st.markdown("### 🎙️ Transcribing Audio...")
            st.markdown('<div class="status-info">⏳ Processing... Please wait</div>', unsafe_allow_html=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_transcribe_progress(percent, message):
                progress_bar.progress(percent / 100)
                status_text.text(f"{message}")
            
            result = transcribe_audio(
                str(audio_file_path),
                model_name="turbo",
                language=language_code,
                progress_callback=update_transcribe_progress
            )
            
            # Save Results
            st.markdown("### 💾 Saving Results...")
            
            base_name = file_path.stem
            srt_path = OUTPUT_DIR / f"{base_name}_transcript.srt"
            txt_path = OUTPUT_DIR / f"{base_name}_transcript.txt"
            
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(result['srt'])
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(result['text'])
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            st.session_state.transcription_done = True
            st.session_state.transcript_text = result['text']
            st.session_state.output_files = {
                'srt': str(srt_path),
                'txt': str(txt_path),
                'mp3': str(audio_file_path) if file_path.suffix.lower() == '.mp4' else None
            }
            
            st.markdown(f"""
            <div class="status-success">
                <h4>🎉 Transcription Complete!</h4>
                <p><strong>Processing Time:</strong> {processing_time:.1f} seconds</p>
                <p><strong>Detected Language:</strong> {result.get('language', 'Unknown')}</p>
                <p><strong>Segments:</strong> {result.get('segments', 0)}</p>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.markdown(f'<div class="status-error">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
            st.error(f"Details: {str(e)}")
    
    # Display Results
    if st.session_state.transcription_done:
        st.markdown("---")
        st.markdown("### 📝 Transcription Result")
        
        st.markdown(f"""
        <div class="transcript-box">
        {st.session_state.transcript_text}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📦 Output Files")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="info-card">
                <h4>📄 Subtitle File (SRT)</h4>
                <code style="font-size: 0.85em;">{st.session_state.output_files['srt']}</code>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="info-card">
                <h4>📄 Text File (TXT)</h4>
                <code style="font-size: 0.85em;">{st.session_state.output_files['txt']}</code>
            </div>
            """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="status-warning">
        <h3>📁 Getting Started</h3>
        <p>Add audio files to the Input folder to begin:</p>
        <code>C:\\Users\\LKK\\Desktop\\Transcript Generator\\Input\\</code>
        <p style="margin-top: 1rem;"><strong>Supported formats:</strong> MP3, MP4, WAV, M4A, FLAC, OGG</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📚 Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>⚡ Fast Processing</h4>
            <p>GPU-accelerated transcription with optimized Whisper model</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>🌍 Multi-Language</h4>
            <p>Support for 10+ languages with automatic detection</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card">
            <h4>📊 Multiple Formats</h4>
            <p>Export to SRT subtitles and plain text</p>
        </div>
        """, unsafe_allow_html=True)
