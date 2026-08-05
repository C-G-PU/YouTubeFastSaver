import os
import yt_dlp
import time
from PyQt6.QtCore import QThread, pyqtSignal

class DownloadWorker(QThread):
    progress_updated = pyqtSignal(float)
    status_updated = pyqtSignal(str)
    download_finished = pyqtSignal(bool, str)

    def __init__(self, url, preset_name, download_dir, cookies_file, force_download=False):
        super().__init__()
        self.url = url
        self.preset_name = preset_name
        self.download_dir = download_dir
        self.cookies_file = cookies_file
        self.force_download = force_download
        self.is_running = True

    def run(self):
        while self.is_running:
            try:
                self.status_updated.emit(f"Starting download for {self.url}...")
                self._download()
                self.download_finished.emit(True, "Download completed successfully.")
                break # Success, exit loop
            except Exception as e:
                if not self.is_running:
                    break

                if self.force_download:
                    self.status_updated.emit(f"Error: {e}. Force download enabled. Retrying in 1 second...")
                    time.sleep(1)
                else:
                    self.download_finished.emit(False, str(e))
                    break

    def _get_format_string(self):
        if "Video" in self.preset_name:
            if "4K" in self.preset_name:
                return "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
            elif "1080p" in self.preset_name:
                return "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
            elif "720p" in self.preset_name:
                return "bestvideo[height<=720]+bestaudio/best[height<=720]"
            elif "480p" in self.preset_name:
                return "bestvideo[height<=480]+bestaudio/best[height<=480]"
            elif "360p" in self.preset_name:
                return "bestvideo[height<=360]+bestaudio/best[height<=360]"
        elif "Audio" in self.preset_name:
            # We will use postprocessors to convert to mp3 in yt-dlp options
            return "bestaudio/best"

        return "best"

    def _download(self):
        ydl_opts = {
            'format': self._get_format_string(),
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'noprogress': True,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False, # We want to catch errors to retry
        }

        # Add cookies if the file exists
        if os.path.exists(self.cookies_file):
            ydl_opts['cookiefile'] = self.cookies_file

        if "Audio" in self.preset_name:
            abr = "320" if "320kbps" in self.preset_name else "128"
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': abr,
            }]

        # This requires ffmpeg on system path for audio extraction or video merging
        # If ffmpeg is not available, it might fail.
        import sys
        if getattr(sys, 'frozen', False):
            # Running as compiled PyInstaller executable
            ffmpeg_path = os.path.join(sys._MEIPASS, 'ffmpeg.exe')
            if os.path.exists(ffmpeg_path):
                ydl_opts['ffmpeg_location'] = ffmpeg_path

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # First extract info to check if requested format is available exactly
            info = ydl.extract_info(self.url, download=False)
            if not info:
                 raise Exception("Could not extract video information.")

            title = info.get('title', 'Video')
            self.status_updated.emit(f"Metadata fetched. Downloading: {title}")

            # Determine if the exact requested format is available
            format_str = self._get_format_string()

            requested_quality = None
            if "Video" in self.preset_name:
                if "4K" in self.preset_name: requested_quality = 2160
                elif "1080p" in self.preset_name: requested_quality = 1080
                elif "720p" in self.preset_name: requested_quality = 720
                elif "480p" in self.preset_name: requested_quality = 480
                elif "360p" in self.preset_name: requested_quality = 360

            if requested_quality:
                # Find best video format available
                formats = info.get('formats', [])
                video_formats = [f for f in formats if f.get('vcodec') != 'none']
                best_available_height = max([f.get('height', 0) or 0 for f in video_formats] + [0])

                if best_available_height > 0 and requested_quality > best_available_height:
                    self.status_updated.emit(f"Warning: Requested quality {requested_quality}p not available. Falling back to {best_available_height}p.")

            # Run the actual download
            ydl.download([self.url])

    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percent = (downloaded / total) * 100
                self.progress_updated.emit(percent)
        elif d['status'] == 'finished':
            self.progress_updated.emit(100)
            self.status_updated.emit("Download finished. Processing...")

    def stop(self):
        self.is_running = False
        self.force_download = False
