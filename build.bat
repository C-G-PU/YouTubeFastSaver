@echo off
setlocal enabledelayedexpansion

echo ==============================================
echo YouTube Fast Saver - Build Script for Windows
echo ==============================================

:: Check if ffmpeg.exe exists, download if not
if not exist "ffmpeg.exe" (
    echo [1/3] Downloading ffmpeg...
    echo Downloading from GitHub (BtbN/FFmpeg-Builds)...

    :: We use a temporary PowerShell script to download and extract ffmpeg
    powershell -Command "$ErrorActionPreference = 'Stop'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $url = 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip'; $zip = 'ffmpeg.zip'; Invoke-WebRequest -Uri $url -OutFile $zip; Expand-Archive -Path $zip -DestinationPath 'ffmpeg_temp' -Force; Move-Item -Path 'ffmpeg_temp\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe' -Destination '.\ffmpeg.exe' -Force; Remove-Item -Path $zip -Force; Remove-Item -Path 'ffmpeg_temp' -Recurse -Force"

    if exist "ffmpeg.exe" (
        echo ffmpeg.exe downloaded successfully.
    ) else (
        echo ERROR: Failed to download ffmpeg.exe. Please download it manually and place it in this folder.
        pause
        exit /b 1
    )
) else (
    echo [1/3] ffmpeg.exe already exists.
)

echo.
echo [2/3] Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo.
echo [3/3] Building executable with PyInstaller...
:: Build options:
:: --noconfirm: overwrite existing build folders
:: --noconsole: hide the terminal window (windowed mode)
:: --icon: set the application icon
:: --add-binary: bundle ffmpeg.exe into the root of the _MEIPASS folder
:: --name: output executable name
pyinstaller --noconfirm --noconsole --icon "src\assets\YTFS.ico" --add-binary "ffmpeg.exe;." --name "YouTubeFastSaver" "src\main.py"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ==============================================
    echo Build Successful!
    echo Executable is located in the "dist" folder.
    echo ==============================================
) else (
    echo.
    echo ==============================================
    echo Build Failed! Check the error messages above.
    echo ==============================================
)

pause
