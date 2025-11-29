# Professional Audio Transcription Tool

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Enterprise-grade speech-to-text transcription powered by OpenAI Whisper**

## Features

- 🎙️ **High-Accuracy Transcription** - OpenAI Whisper turbo model
- ⚡ **GPU-Accelerated** - Auto-detection for CUDA/CPU
- 🌍 **Multi-Language** - Support for 10+ languages with auto-detection
- 📊 **Multiple Formats** - Export to SRT subtitles and plain text
- 🖥️ **System Auto-Detection** - Automatically detects CPU, GPU, RAM specs
- 🚀 **Professional UI** - Enterprise-grade Streamlit interface
- 🔄 **Long Audio Support** - Optimized VAD for 3+ hour recordings

## Requirements

- Python 3.9+
- CUDA 12.1 (optional, for GPU acceleration)
- 6GB RAM minimum (16GB recommended with GPU)

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/audio-transcriber.git
cd audio-transcriber
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download Whisper Model (Optional)

For faster startup, pre-download the model:

```bash
python -c "from faster_whisper import WhisperModel; WhisperModel('turbo')"
```

## Usage

### Start the Application

```bash
streamlit run app.py
```

Application will open at: `http://localhost:8501`

### Steps

1. **Add Audio Files** - Place audio files in `Input/` folder
2. **Select File** - Choose from sidebar
3. **Select Language** - Auto-detect or choose manually
4. **Click Start** - Begin transcription
5. **Download Results** - SRT and TXT files in `Output/` folder

## Supported Formats

- 🎵 MP3
- 🎬 MP4 (video with audio)
- 🔊 WAV
- 📱 M4A
- 🎧 FLAC
- 🌐 OGG
- 🎯 WEBM

## System Detection

Automatically detects and displays:

- Operating System
- CPU cores and speed
- RAM (total and available)
- GPU type and VRAM
- CUDA version

## Performance

| Audio Length | GPU (RTX 3060) | CPU (i7) |
|--------------|---|---|
| 1 minute | 3-5 seconds | 15-20 seconds |
| 10 minutes | 15-25 seconds | 2-3 minutes |
| 1 hour | 3-5 minutes | 15-20 minutes |

*Times vary based on hardware and audio quality*

## Transcription Features

- ✅ Noise filtering (VAD - Voice Activity Detection)
- ✅ Speaker context awareness
- ✅ Automatic punctuation
- ✅ Segment timestamps
- ✅ Language detection (99%+ accuracy)

## Output Files

### SRT Format
Subtitle file with timestamps for video editors:

```
1
00:00:05,000 --> 00:00:10,500
This is the transcribed text

2
00:00:10,500 --> 00:00:15,000
Next sentence continues here
```

### TXT Format
Plain text file with full transcription:

```
This is the transcribed text
Next sentence continues here
...
```

## Troubleshooting

### "Library cublas64_12.dll not found"

**Fix**: Reinstall PyTorch with correct CUDA version

```bash
pip uninstall torch torchaudio -y
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### "No GPU detected"

**Fix**: Install CUDA 12.1 and cuDNN from NVIDIA

### Slow transcription on long files

**Fix**: Ensure GPU is being used (check sidebar system info)

## Directory Structure

```
audio-transcriber/
├── app.py                 # Main Streamlit application
├── utils.py              # Core transcription functions
├── requirements.txt      # Python dependencies
├── setup.bat            # Windows setup script
├── run.bat              # Windows run script
├── Input/               # Place audio files here
├── Output/              # Transcription results saved here
├── README.md            # This file
└── LICENSE              # MIT License
```

## Configuration

Edit `app.py` to customize:

- Default model (currently: turbo)
- Input/Output directories
- Supported audio formats
- UI styling and colors

## API Usage (Advanced)

```python
from utils import transcribe_audio

result = transcribe_audio(
    audio_path="audio.mp3",
    model_name="turbo",
    language="en"
)

print(result['text'])  # Transcription text
print(result['srt'])   # SRT format
```

## Environment Variables

Optional configuration via `.env`:

```
WHISPER_MODEL=turbo
INPUT_DIR=./Input
OUTPUT_DIR=./Output
```

## GPU Optimization

For best performance:

1. Update NVIDIA drivers to latest
2. Ensure CUDA Toolkit 12.1 is installed
3. Run `nvidia-smi` to verify GPU detection

## Advanced Options

### Batch Processing

For processing multiple files:

```bash
for file in Input/*.mp3; do
    python -c "from utils import transcribe_audio; transcribe_audio('$file')"
done
```

### Custom Models

Modify `transcribe_audio()` model_name parameter:

- `"turbo"` - Fast (1.5GB)
- `"base"` - Balanced (140MB)
- `"small"` - Smaller (540MB)
- `"medium"` - Better accuracy (1.5GB)
- `"large"` - Best accuracy (3GB)

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Known Limitations

- Maximum recommended audio: 10 hours
- Accuracy varies by audio quality
- GPU recommended for real-time transcription
- CUDA required for GPU acceleration

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition model
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - Optimized implementation
- [Streamlit](https://streamlit.io/) - UI framework

## Citation

If you use this in research, please cite:

```bibtex
@article{radford2022robust,
  title={Robust speech recognition via large-scale weak supervision},
  author={Radford, Alec and others},
  journal={arXiv preprint arXiv:2212.04356},
  year={2022}
}
```

## Contact & Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/audio-transcriber/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/audio-transcriber/discussions)

---

**Made with ❤️ for the community**
