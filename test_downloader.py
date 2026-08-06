import sys
from PyQt6.QtCore import QCoreApplication
from src.engine.downloader import DownloadWorker
import time

app = QCoreApplication(sys.argv)

def test_downloader():
    print("Testing downloader logic...")
    url = "https://www.youtube.com/watch?v=jNQXAC9IVRw" # Me at the zoo (first youtube video)

    worker = DownloadWorker(url, "Video - 360p", "./", "no_cookies.txt", client_spoofing="Android")

    metadata_fetched = False

    def on_status(status):
        print(f"STATUS: {status}")
        nonlocal metadata_fetched
        if "Metadata fetched" in status:
            metadata_fetched = True
            worker.stop() # Stop before actual download

    worker.status_updated.connect(on_status)

    worker.start()

    for _ in range(15):
        if metadata_fetched:
            break
        QCoreApplication.processEvents()
        time.sleep(1)

    worker.stop()
    worker.wait()

    if metadata_fetched:
        print("Test Passed: Metadata successfully fetched.")
    else:
        print("Test Failed: Could not fetch metadata.")

if __name__ == "__main__":
    test_downloader()
