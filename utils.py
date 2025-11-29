"""
ULTIMATE TRANSCRIPTION FIX - Complete Corrupted Audio Handler
Works with: 60+ minute lectures, silences, VAD artifacts, "you..." repeats
INCLUDES: All required helper functions for app.py
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Callable, List, Dict
import torch
import logging
import psutil
import platform
import gc
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LOCAL_MODEL_DIR = Path.home() / ".cache" / "whisper"

# ==================== SYSTEM DETECTION ====================

def get_system_info() -> Dict[str, str]:
    """Detect host system specifications"""
    info = {
        "os": platform.system(),
        "cpu_count": psutil.cpu_count(logical=False),
        "cpu_freq": f"{psutil.cpu_freq().max / 1000:.1f} GHz" if psutil.cpu_freq() else "Unknown",
        "ram_total": f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
        "ram_available": f"{psutil.virtual_memory().available / (1024**3):.1f} GB",
    }
    
    if torch.cuda.is_available():
        info["gpu_available"] = True
        info["gpu_name"] = torch.cuda.get_device_name(0)
        info["gpu_memory"] = f"{torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB"
        info["cuda_version"] = torch.version.cuda
    else:
        info["gpu_available"] = False
        info["gpu_name"] = "None (CPU mode)"
    
    return info

def validate_ffmpeg() -> bool:
    """Verify FFmpeg installation"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_gpu_available() -> bool:
    """Check if CUDA GPU is available"""
    return torch.cuda.is_available()

def get_file_size(file_path: Path) -> str:
    """Format file size for display"""
    size_bytes = file_path.stat().st_size
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

# ==================== FILE MANAGEMENT ====================

def get_audio_files(input_dir: Path) -> List[str]:
    """Get all audio files from input directory - REQUIRED BY app.py"""
    audio_extensions = {'.mp3', '.mp4', '.wav', '.m4a', '.flac', '.ogg', '.webm'}
    files = []
    
    if not input_dir.exists():
        return files
    
    for file in input_dir.iterdir():
        if file.suffix.lower() in audio_extensions:
            files.append(file.name)
    
    return sorted(files)

def convert_mp4_to_mp3(
    input_path: str,
    output_path: str,
    progress_callback: Optional[Callable[[int], None]] = None
) -> None:
    """Convert MP4 to MP3 using FFmpeg - REQUIRED BY app.py"""
    if not validate_ffmpeg():
        raise RuntimeError("FFmpeg not installed. Cannot convert MP4 files.")
    
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-vn',
        '-acodec', 'libmp3lame',
        '-q:a', '2',
        '-ar', '16000',
        '-ac', '1',
        '-y',
        output_path
    ]
    
    try:
        if progress_callback:
            progress_callback(0)
        
        logger.info(f"Converting: {input_path} → {output_path}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        stdout, stderr = process.communicate()
        
        if progress_callback:
            progress_callback(100)
        
        if process.returncode != 0:
            error_msg = stderr.decode('utf-8', errors='ignore')
            raise RuntimeError(f"FFmpeg conversion failed: {error_msg}")
        
        logger.info("Conversion complete")
            
    except Exception as e:
        logger.error(f"MP4 conversion failed: {str(e)}")
        raise RuntimeError(f"MP4 conversion failed: {str(e)}")

# ==================== TEXT PROCESSING ====================

def filter_garbage_segments(text: str) -> str:
    """Remove corrupted VAD artifacts like repeated 'you...' or 'uh...'"""
    lines = text.strip().split('\n\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip if more than 5 consecutive repetitions of same pattern
        if re.search(r'(you\.\.\.\s*){6,}|( uh\.\.\.){6,}| \.\.\.|you\.\.\.\.\.\.|uh uh uh uh uh', line):
            continue
        # Skip if line is ONLY repetitions
        if re.match(r'^(you\.\.\.\s*)+$|^( uh\.\.\.)+$', line):
            continue
        # Skip empty or very short garbage
        if len(line.strip()) < 3:
            continue
        cleaned_lines.append(line.strip())
    
    return '\n\n'.join(cleaned_lines)

def merge_short_segments(text: str, min_length: int = 20) -> str:
    """Merge very short segments that are likely VAD errors"""
    lines = text.strip().split('\n\n')
    merged_lines = []
    current_merge = ""
    
    for line in lines:
        if len(line.strip()) < min_length and current_merge:
            # Try to merge with previous
            current_merge += " " + line.strip()
        else:
            if current_merge:
                merged_lines.append(current_merge.strip())
            current_merge = line.strip()
    
    if current_merge:
        merged_lines.append(current_merge.strip())
    
    return '\n\n'.join(merged_lines)

def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

# ==================== MODEL CACHING ====================

_MODEL_CACHE = {}

def check_local_model_exists(model_name: str) -> bool:
    """Check if local model exists"""
    model_path = LOCAL_MODEL_DIR / model_name
    if not model_path.exists():
        return False
    
    required_files = ['model.bin', 'config.json', 'tokenizer.json', 'vocabulary.json']
    for file in required_files:
        if not (model_path / file).exists():
            return False
    
    return True

def get_cached_model(model_name: str, device: str, compute_type: str):
    """Get or load model with intelligent caching"""
    cache_key = f"{model_name}_{device}_{compute_type}"
    
    if cache_key not in _MODEL_CACHE:
        from faster_whisper import WhisperModel
        
        local_model_path = LOCAL_MODEL_DIR / model_name
        
        if check_local_model_exists(model_name):
            logger.info(f"✅ Using local model: {local_model_path}")
            model_path = str(local_model_path)
        else:
            logger.info(f"⚠️ Downloading {model_name} model...")
            model_path = model_name
        
        logger.info(f"Loading model {model_name}...")
        
        _MODEL_CACHE[cache_key] = WhisperModel(
            model_path,
            device=device,
            compute_type=compute_type,
            download_root=str(LOCAL_MODEL_DIR),
            num_workers=1,
            cpu_threads=2
        )
        
        logger.info(f"✅ Model {model_name} loaded successfully")
    else:
        logger.info(f"Using cached model {model_name}")
    
    return _MODEL_CACHE[cache_key]

# ==================== MAIN TRANSCRIPTION ====================

def transcribe_audio(
    audio_path: str,
    model_name: str = "turbo",
    language: Optional[str] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Dict[str, str]:
    """
    ULTIMATE TRANSCRIPTION ENGINE
    
    ✅ Handles 60+ minute lectures
    ✅ Removes VAD corruption ("you..." repeats)
    ✅ Merges incomplete segments
    ✅ Produces CLEAN output
    ✅ Works with RTX 4050 GPU
    """
    
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise RuntimeError("Faster-Whisper not installed!")
    
    if progress_callback:
        progress_callback(0, "Initializing GPU...")
    
    device = "cuda" if check_gpu_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    
    sys_info = get_system_info()
    logger.info(f"System: {sys_info['os']} | CPU: {sys_info['cpu_count']} cores | RAM: {sys_info['ram_available']}/{sys_info['ram_total']}")
    
    if sys_info.get('gpu_available'):
        logger.info(f"GPU: {sys_info.get('gpu_name')} ({sys_info.get('gpu_memory')} VRAM)")
    
    if progress_callback:
        progress_callback(10, f"Loading {model_name} model...")
    
    model = get_cached_model(model_name, device, compute_type)
    
    if progress_callback:
        progress_callback(30, "Starting transcription (removing VAD artifacts)...")
    
    logger.info(f"Transcribing: {audio_path}")
    logger.info(f"Language: {language or 'auto-detect'}")
    
    # ============== CRITICAL VAD SETTINGS ==============
    try:
        segments, info = model.transcribe(
            audio=audio_path,
            language=language,
            beam_size=2,
            best_of=1,
            temperature=0.0,
            chunk_length=15,
            vad_filter=True,
            vad_parameters=dict(
                threshold=0.4,
                min_silence_duration_ms=3000,
                min_speech_duration_ms=100,
                max_speech_duration_s=240,
            ),
            condition_on_previous_text=False,
            word_timestamps=False,
            compression_ratio_threshold=2.0,
            log_prob_threshold=-0.5,
            no_speech_threshold=0.6,
            language_detection_threshold=0.5,
        )
    except TypeError:
        logger.warning("Using fallback transcription parameters...")
        segments, info = model.transcribe(
            audio=audio_path,
            language=language,
            beam_size=2,
            temperature=0.0,
            vad_filter=True,
        )
    
    if progress_callback:
        progress_callback(50, f"Detected language: {info.language}")
    
    logger.info(f"Detected language: {info.language}")
    
    full_text = []
    srt_content = []
    segment_index = 1
    total_duration = getattr(info, 'duration', 0)
    
    for segment in segments:
        try:
            segment_duration = segment.end - segment.start
        except:
            continue
        
        if segment_duration < 0.1:
            continue
        
        try:
            segment_text = segment.text.strip() if hasattr(segment, 'text') else ""
        except:
            continue
        
        if not segment_text or len(segment_text) < 2:
            continue
        
        # CRITICAL: Skip VAD garbage
        if re.search(r'^(you\.\.\.\s*){3,}$|^( uh\.\.\.){3,}$|^\.{5,}$', segment_text):
            logger.debug(f"Skipped garbage segment: {segment_text[:50]}")
            continue
        
        full_text.append(segment_text)
        
        start_time = format_timestamp(segment.start)
        end_time = format_timestamp(segment.end)
        
        srt_content.append(f"{segment_index}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(segment_text)
        srt_content.append("")
        
        segment_index += 1
        
        # Memory management
        if segment_index % 10 == 0:
            gc.collect()
            if device == "cuda":
                torch.cuda.empty_cache()
        
        if progress_callback and total_duration > 0:
            progress_percent = min(50 + int((segment.end / total_duration) * 45), 95)
            progress_callback(progress_percent, f"Processing segment {segment_index}... ({segment.end:.1f}/{total_duration:.1f}s)")
    
    if progress_callback:
        progress_callback(95, "Cleaning up artifacts...")
    
    # ============== FINAL CLEANUP ==============
    transcript_text = '\n\n'.join(full_text)
    
    # Remove remaining garbage
    transcript_text = filter_garbage_segments(transcript_text)
    transcript_text = merge_short_segments(transcript_text, min_length=15)
    
    srt_text = '\n'.join(srt_content)
    
    if progress_callback:
        progress_callback(100, "✅ Transcription complete!")
    
    logger.info(f"✅ Transcription complete: {segment_index} segments")
    logger.info(f"Total duration: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
    logger.info(f"Final transcript length: {len(transcript_text)} characters (after cleanup)")
    
    return {
        'text': transcript_text,
        'srt': srt_text,
        'language': info.language if hasattr(info, 'language') else 'unknown',
        'segments': segment_index,
        'device': device,
        'compute_type': compute_type,
        'duration': total_duration
    }
