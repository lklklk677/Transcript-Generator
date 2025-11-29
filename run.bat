@echo off
chcp 65001 >nul
cls
echo ========================================
echo   Audio Transcription Tool
echo ========================================
echo.

REM Check FFmpeg
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg not detected!
    echo.
    echo MP4 to MP3 conversion will not work.
    echo Only MP3 files are supported without FFmpeg.
    echo.
    echo To install FFmpeg:
    echo 1. Download: https://www.gyan.dev/ffmpeg/builds/
    echo 2. Extract to C:\ffmpeg
    echo 3. Add C:\ffmpeg\bin to System PATH
    echo 4. Restart Command Prompt
    echo.
    echo Press any key to continue with MP3 only support...
    pause >nul
    echo.
)

echo Starting Streamlit server...
echo.
echo The browser will open automatically.
echo If not, manually visit: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

streamlit run app.py