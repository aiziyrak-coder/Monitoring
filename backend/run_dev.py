"""
Django + Socket.IO serverini ishga tushirish (Windows va Linux).
Ishlatish: python run_dev.py
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.chdir(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

if __name__ == "__main__":
    from waitress import serve

    from config.wsgi_socket import application

    host = os.environ.get("BIND_HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    print(f"ClinicMonitoring backend: http://127.0.0.1:{port} (API /api, Socket.IO /socket.io)")
    serve(application, host=host, port=port, threads=8)
