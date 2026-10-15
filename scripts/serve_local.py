"""One local process serves the actual built frontend and API; open only after HTTP readiness."""

import argparse
import threading
import time
import urllib.error
import urllib.request
import webbrowser

import uvicorn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    from backend.app.main import app

    url = "http://127.0.0.1:8000/"

    def open_when_ready():
        for _ in range(90):
            try:
                with urllib.request.urlopen(url, timeout=1) as response:
                    if b"<title>MatchWeave" in response.read(4096):
                        webbrowser.open(url)
                        return
            except (OSError, urllib.error.URLError):
                pass
            time.sleep(0.5)

    if not args.no_browser:
        threading.Thread(target=open_when_ready, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
