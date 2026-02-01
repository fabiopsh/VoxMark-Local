@echo off
echo Starting VoxMark Local POC (Automated Python 3.10 Environment)...

:: Check if .venv exists, if not, create it (Bootstrap on first run)
if not exist .venv (
    echo [INFO] First run detected. Setting up Python 3.10 environment...
    echo [INFO] Installing 'uv' package manager...
    pip install uv >nul 2>&1
    echo [INFO] Downloading Python 3.10 and creating virtualenv...
    uv venv .venv --python 3.10
    echo [INFO] Installing project dependencies...
    uv pip install -r voxmark-backend/requirements.txt --python .venv
    echo [INFO] Setup complete!
)

:: Start Backend using the Managed Python (in .venv)
start "VoxMark Backend (Python 3.10)" powershell -NoExit -Command "& '.venv\Scripts\python.exe' voxmark-backend/main.py"

:: Wait a bit
timeout /t 3

:: Start Frontend in current window (or new one)
cd voxmark-frontend
npm run tauri dev
