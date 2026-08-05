@echo off
echo Cleaning up old builds...
rmdir /s /q build dist 2>nul
del /q *.spec 2>nul

echo Installing dependencies...
pip install -r requirements.txt

echo Building executable...
rem Using --windowed to hide console and --noconfirm to overwrite previous builds
rem We also need to ensure yt-dlp dependencies and PyQt6-WebEngine resources are bundled correctly.
pyinstaller --noconfirm --windowed --name "YouTubeFastSaver" --icon=NONE --hidden-import="src" src/main.py

echo Build complete! The executable is located in the dist\YouTubeFastSaver directory.
pause
