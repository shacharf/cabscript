import threading
import webbrowser

import uvicorn

from cabinetry.app.main import app

PORT = 8765


def _open_browser() -> None:
    webbrowser.open(f"http://localhost:{PORT}")


def main() -> None:
    threading.Timer(1.5, _open_browser).start()
    uvicorn.run(app, host="127.0.0.1", port=PORT)


if __name__ == "__main__":
    main()
