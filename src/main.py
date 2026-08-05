import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from src.ui.main_window import MainWindow

# Provide early, explicit imports for WebEngine components to guarantee PyInstaller hooks run.
import PyQt6.QtWebEngineCore
import PyQt6.QtWebEngineWidgets

def exception_hook(exc_type, exc_value, exc_traceback):
    """Global exception handler that shows a message box."""
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(error_msg, file=sys.stderr)
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle("Fatal Error")
    msg_box.setText("An unexpected error occurred!")
    msg_box.setDetailedText(error_msg)
    msg_box.exec()

def main():
    sys.excepthook = exception_hook
    app = QApplication(sys.argv)

    window = MainWindow(app)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
