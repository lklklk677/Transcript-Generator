@echo off
chcp 65001 >nul
cls
echo ========================================
echo   Audio Transcription Tool - Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not installed!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Python environment detected
echo.

REM Upgrade pip
echo [2/5] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo Done!
echo.

REM Install PyTorch with CUDA support
echo [3/5] Installing PyTorch with CUDA 12.1...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet
echo Done!
echo.

REM Install other dependencies
echo [4/5] Installing other packages...
pip install -r requirements.txt --quiet
echo Done!
echo.

REM Check FFmpeg
echo [5/5] Checking FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg not detected!
    echo.
    echo FFmpeg Installation Steps:
    echo 1. Download from: https://www.gyan.dev/ffmpeg/builds/
    echo 2. Extract to C:\ffmpeg
    echo 3. Add C:\ffmpeg\bin to System PATH
    echo 4. Restart Command Prompt
    echo.
) else (
    echo FFmpeg detected!
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo IMPORTANT:
echo 1. If FFmpeg is not installed, MP4 conversion will not work
echo 2. First run will download Whisper model (approx 3GB)
echo 3. Run run.bat to start the application
echo.
pause