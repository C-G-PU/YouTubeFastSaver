from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QComboBox, QTextEdit,
    QLabel, QFileDialog, QCheckBox, QProgressBar,
    QScrollArea
)
from PyQt6.QtCore import Qt
from src.utils.settings import load_settings, save_settings
from src.utils.themes import apply_theme

class DownloadsListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def add_download(self, title):
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)

        title_label = QLabel(title)
        progress_bar = QProgressBar()
        progress_bar.setValue(0)

        cancel_btn = QPushButton("X")
        cancel_btn.setFixedWidth(30)

        item_layout.addWidget(title_label)
        item_layout.addWidget(progress_bar)
        item_layout.addWidget(cancel_btn)

        self.layout.addWidget(item_widget)
        return progress_bar, cancel_btn, item_widget

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.settings = load_settings()
        self.setWindowTitle("YouTube Fast Saver")
        self.setMinimumSize(800, 600)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.setup_ui()
        self.apply_current_settings()

    def setup_ui(self):
        # Top Bar: URL, Paste, Force Download
        top_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube video or playlist URL here...")
        top_layout.addWidget(self.url_input)

        self.paste_btn = QPushButton("Paste")
        self.paste_btn.clicked.connect(self.paste_url)
        top_layout.addWidget(self.paste_btn)

        self.force_dl_btn = QPushButton("Start Force DL")
        self.force_dl_btn.setCheckable(True)
        self.force_dl_btn.setToolTip("Toggle to keep trying to download if it fails initially")
        self.force_dl_btn.clicked.connect(self.toggle_force_download)
        top_layout.addWidget(self.force_dl_btn)

        self.active_force_worker = None

        self.layout.addLayout(top_layout)

        # Settings Bar: Dir selection, Theme, Login
        settings_layout = QHBoxLayout()

        self.dir_label = QLabel(f"Dir: {self.settings['download_dir']}")
        settings_layout.addWidget(self.dir_label)

        self.change_dir_btn = QPushButton("Change Dir")
        self.change_dir_btn.clicked.connect(self.select_directory)
        settings_layout.addWidget(self.change_dir_btn)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark", "blue"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        settings_layout.addWidget(QLabel("Theme:"))
        settings_layout.addWidget(self.theme_combo)

        self.login_btn = QPushButton("Login to YouTube")
        self.login_btn.clicked.connect(self.open_login_browser)
        settings_layout.addWidget(self.login_btn)

        self.layout.addLayout(settings_layout)

        # Presets Bar
        presets_layout = QHBoxLayout()
        presets_layout.addWidget(QLabel("Format:"))

        self.preset_combo = QComboBox()
        presets = [
            ("Video - 4K", "Best quality video (4K) with audio"),
            ("Video - 1080p", "High quality video (1080p) with audio"),
            ("Video - 720p", "Standard quality video (720p) with audio"),
            ("Video - 480p", "Medium quality video (480p) with audio"),
            ("Video - 360p", "Low quality video (360p) with audio"),
            ("Audio - MP3 320kbps", "High quality audio only (MP3 320kbps)"),
            ("Audio - MP3 128kbps", "Standard quality audio only (MP3 128kbps)")
        ]
        for name, tooltip in presets:
            self.preset_combo.addItem(name)
            self.preset_combo.setItemData(self.preset_combo.count()-1, tooltip, Qt.ItemDataRole.ToolTipRole)

        presets_layout.addWidget(self.preset_combo)

        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.start_download)
        presets_layout.addWidget(self.download_btn)

        self.layout.addLayout(presets_layout)

        # Main Area: Downloads list and Log
        main_area_layout = QHBoxLayout()

        # Downloads List
        self.downloads_scroll = QScrollArea()
        self.downloads_scroll.setWidgetResizable(True)
        self.downloads_list = DownloadsListWidget()
        self.downloads_scroll.setWidget(self.downloads_list)

        main_area_layout.addWidget(self.downloads_scroll, stretch=2)

        # Log Output
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        main_area_layout.addWidget(self.log_text, stretch=1)

        self.layout.addLayout(main_area_layout)

    def apply_current_settings(self):
        self.theme_combo.setCurrentText(self.settings["theme"])
        # We no longer apply force_download setting on startup since it's an action per URL now
        apply_theme(self.app, self.settings["theme"])

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Download Directory", self.settings["download_dir"])
        if dir_path:
            self.settings["download_dir"] = dir_path
            self.dir_label.setText(f"Dir: {dir_path}")
            self.save_current_settings()

    def change_theme(self, theme_name):
        self.settings["theme"] = theme_name
        apply_theme(self.app, theme_name)
        self.save_current_settings()

    def save_current_settings(self):
        # self.settings["force_download"] = self.force_download_cb.isChecked() # Removing from settings as it's a toggle action now
        save_settings(self.settings)

    def log(self, message):
        self.log_text.append(message)

    def open_login_browser(self):
        from src.ui.browser_window import BrowserWindow
        self.browser_window = BrowserWindow()
        self.browser_window.cookies_saved.connect(self.on_cookies_saved)
        self.browser_window.show()
        self.log("Opened login window. Please sign in to Google/YouTube.")

    def on_cookies_saved(self, cookies_file):
        self.log(f"Cookies saved to {cookies_file}. These will be used for restricted videos.")

    def paste_url(self):
        from PyQt6.QtWidgets import QApplication
        clipboard_text = QApplication.clipboard().text()
        if clipboard_text:
            self.url_input.setText(clipboard_text)

    def toggle_force_download(self, checked):
        if checked:
            self.force_dl_btn.setText("Stop Force DL")
            self.start_download(force=True)
        else:
            self.force_dl_btn.setText("Start Force DL")
            if self.active_force_worker and hasattr(self.active_force_worker, 'stop'):
                self.log("Stopping active force download...")
                self.active_force_worker.stop()
                self.active_force_worker = None

    def start_download(self, force=False):
        url = self.url_input.text().strip()
        if not url:
            self.log("Error: Please enter a URL.")
            # Uncheck button if it was a force download trigger
            if force:
                self.force_dl_btn.setChecked(False)
                self.force_dl_btn.setText("Start Force DL")
            return

        preset = self.preset_combo.currentText()
        download_dir = self.settings["download_dir"]
        from src.ui.browser_window import COOKIES_FILE

        # UI update
        self.log(f"Initializing download for: {url}")
        self.log(f"Preset: {preset}, Force: {force}")

        progress_bar, cancel_btn, item_widget = self.downloads_list.add_download(url)

        from src.engine.downloader import DownloadWorker
        worker = DownloadWorker(url, preset, download_dir, COOKIES_FILE, force_download=force)

        if force:
            self.active_force_worker = worker

        # Store a reference to avoid garbage collection
        if not hasattr(self, 'workers'):
            self.workers = []
        self.workers.append(worker)

        worker.progress_updated.connect(progress_bar.setValue)
        worker.status_updated.connect(self.log)

        def on_finished(success, message):
            self.log(f"Download {'Success' if success else 'Failed'}: {message}")
            if success:
                progress_bar.setValue(100)
            # Remove worker from list
            if worker in self.workers:
                self.workers.remove(worker)

            # Reset UI if force download finishes or errors out (when not forcing anymore)
            if force and worker == self.active_force_worker:
                self.force_dl_btn.setChecked(False)
                self.force_dl_btn.setText("Start Force DL")
                self.active_force_worker = None

        worker.download_finished.connect(on_finished)

        def cancel_download():
            self.log(f"Cancelling download for: {url}")
            worker.stop()
            # Remove from UI
            item_widget.setParent(None)
            item_widget.deleteLater()

            # Start a thread to wait for it to finish and then delete the file
            import threading
            import os

            # Uncheck UI if it was the active force download
            if force and worker == self.active_force_worker:
                self.force_dl_btn.setChecked(False)
                self.force_dl_btn.setText("Start Force DL")
                self.active_force_worker = None

            def cleanup_files():
                worker.wait() # wait for the thread to actually stop
                if worker.current_filename:
                    # yt-dlp might leave a .part or .ytdl file
                    possible_files = [
                        worker.current_filename,
                        worker.current_filename + '.part',
                        worker.current_filename + '.ytdl'
                    ]
                    for f in possible_files:
                        if os.path.exists(f):
                            try:
                                os.remove(f)
                                print(f"Cleaned up {f}")
                            except Exception as e:
                                print(f"Failed to clean up {f}: {e}")

            threading.Thread(target=cleanup_files, daemon=True).start()

        cancel_btn.clicked.connect(cancel_download)

        worker.start()
