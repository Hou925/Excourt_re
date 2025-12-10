import threading
import time
import requests

from app import create_app, socketio
from app.sync_courtinfo import sync_court_info

app = create_app()


def start_sync_task():
    def run_sync():
        while True:
            try:
                sync_court_info()
            except Exception as e:
                print(f"Sync task encountered an error: {e}")
                time.sleep(5)

    sync_thread = threading.Thread(target=run_sync, daemon=True)
    sync_thread.start()


if __name__ == "__main__":
    start_sync_task()
    socketio.run(app, host="0.0.0.0", port=8000, debug=False)
