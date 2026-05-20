"""Servidor local para el dashboard del pipeline.

Ejecuta el pipeline al iniciar y tambien permite refrescarlo desde el boton
del dashboard. No requiere Streamlit, Dash ni dependencias externas.
"""

from __future__ import annotations

import http.server
import json
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "dashboard_server.log"

from run_pipeline import DASHBOARD_JSON, run_pipeline  # noqa: E402


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        clean_path = unquote(path.split("?", 1)[0].split("#", 1)[0])
        if clean_path == "/":
            return str(ROOT / "dashboard" / "index.html")
        if clean_path.startswith("/data/"):
            return str(ROOT / clean_path.lstrip("/"))
        if clean_path.startswith("/dashboard/"):
            return str(ROOT / clean_path.lstrip("/"))
        return str(ROOT / "dashboard" / clean_path.lstrip("/"))

    def do_GET(self) -> None:
        if self.path.startswith("/api/refresh"):
            self.send_json(run_pipeline())
            return
        if self.path.startswith("/api/status"):
            if not DASHBOARD_JSON.exists():
                run_pipeline()
            self.send_json(json.loads(DASHBOARD_JSON.read_text(encoding="utf-8")))
            return
        super().do_GET()

    def send_json(self, payload: object) -> None:
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    LOG_DIR.mkdir(exist_ok=True)
    try:
        if not DASHBOARD_JSON.exists():
            run_pipeline()
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 8000), DashboardHandler)
        LOG_FILE.write_text("Dashboard disponible en http://127.0.0.1:8000\n", encoding="utf-8")
        print("Dashboard disponible en http://127.0.0.1:8000", flush=True)
        server.serve_forever()
    except Exception as exc:
        LOG_FILE.write_text(f"Error al iniciar dashboard: {exc}\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
