"""
Django + Socket.IO (threading) — bitta portda REST va /socket.io.

Windows: python run_dev.py
Linux: waitress-serve yoki gunicorn (1 worker) bilan shu modulni bering.
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from monitoring.io_bus import sio
from monitoring.socket_events import register_socket_handlers

register_socket_handlers(sio)

from django.core.wsgi import get_wsgi_application

django_app = get_wsgi_application()

import socketio

application = socketio.WSGIApp(sio, django_app)
