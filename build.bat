@echo off
echo ==============================================
echo YouTube Fast Saver - Build Script for Windows
echo ==============================================

:: Detect python executable
set PYTHON_CMD=python
%PYTHON_CMD% --version >nul 2>&1
if %ERRORLEVEL% equ 0 goto check_ffmpeg

set PYTHON_CMD=py
%PYTHON_CMD% --version >nul 2>&1
if %ERRORLEVEL% equ 0 goto check_ffmpeg

:: If we reach here, neither python nor py works
echo ERROR: Python is not installed or not added to PATH!
echo.
echo Please install Python 3.10+ from python.org
echo IMPORTANT: During installation, make sure to check the box:
echo "Add Python to PATH" or "Add python.exe to PATH"
echo.
pause
exit /b 1

:check_ffmpeg
if exist "ffmpeg.exe" goto has_ffmpeg

echo [1/3] Downloading ffmpeg from GitHub (BtbN/FFmpeg-Builds)...
powershell -Command "$ErrorActionPreference = 'Stop'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $url = 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip'; $zip = 'ffmpeg.zip'; Invoke-WebRequest -Uri $url -OutFile $zip; Expand-Archive -Path $zip -DestinationPath 'ffmpeg_temp' -Force; Move-Item -Path 'ffmpeg_temp\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe' -Destination '.\ffmpeg.exe' -Force; Remove-Item -Path $zip -Force; Remove-Item -Path 'ffmpeg_temp' -Recurse -Force"

if not exist "ffmpeg.exe" goto failed_ffmpeg

:has_ffmpeg
echo [1/3] ffmpeg.exe is present.

echo.
echo [2/3] Installing dependencies using %PYTHON_CMD%...
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install -r requirements.txt
%PYTHON_CMD% -m pip install pyinstaller

echo.
echo [3/3] Building executable with PyInstaller...
%PYTHON_CMD% -m PyInstaller --noconfirm --noconsole --icon "src\assets\YTFS.ico" --add-binary "ffmpeg.exe;." --name "YouTubeFastSaver" "src\main.py"

if %ERRORLEVEL% neq 0 goto failed_build

echo.
echo ==============================================
echo Build Process Finished Successfully!
echo Check the "dist" folder for your executable.
echo ==============================================
pause
exit /b 0

:failed_build
echo.
echo ==============================================
echo ERROR: Build failed! Check the console output above for details.
echo ==============================================
pause
exit /b 1

:failed_ffmpeg
echo ERROR: Failed to download ffmpeg.exe. Please download it manually and place it in this folder.
pause
exit /b 1
