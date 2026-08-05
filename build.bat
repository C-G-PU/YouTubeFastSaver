@echo off
echo ==============================================
echo YouTube Fast Saver - Build Script for Windows
echo ==============================================

if exist "ffmpeg.exe" goto has_ffmpeg

echo [1/3] Downloading ffmpeg from GitHub (BtbN/FFmpeg-Builds)...
powershell -Command "$ErrorActionPreference = 'Stop'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $url = 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip'; $zip = 'ffmpeg.zip'; Invoke-WebRequest -Uri $url -OutFile $zip; Expand-Archive -Path $zip -DestinationPath 'ffmpeg_temp' -Force; Move-Item -Path 'ffmpeg_temp\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe' -Destination '.\ffmpeg.exe' -Force; Remove-Item -Path $zip -Force; Remove-Item -Path 'ffmpeg_temp' -Recurse -Force"

if not exist "ffmpeg.exe" goto failed_ffmpeg

:has_ffmpeg
echo [1/3] ffmpeg.exe is present.

echo.
echo [2/3] Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo.
echo [3/3] Building executable with PyInstaller...
python -m PyInstaller --noconfirm --noconsole --icon "src\assets\YTFS.ico" --add-binary "ffmpeg.exe;." --name "YouTubeFastSaver" "src\main.py"

echo.
echo ==============================================
echo Build Process Finished!
echo Check the "dist" folder for your executable.
echo ==============================================
pause
exit /b 0

:failed_ffmpeg
echo ERROR: Failed to download ffmpeg.exe. Please download it manually and place it in this folder.
pause
exit /b 1
