import os
import sys

from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "monitoring"
    verbose_name = "Klinik monitoring"

    def ready(self):
        if "migrate" in sys.argv or "makemigrations" in sys.argv:
            return
        if "runserver" in sys.argv and os.environ.get("RUN_MAIN") != "true":
            return
        # HL7 MLLP faqat ASGI (uvicorn run_dev.py) ishga tushganda — config.asgi on_startup.
        # ready() da ham chaqirilsa, ba'zan ikki marta / port band bo'lganda qayta urinmaslik xatosi bo'lardi.

        from django.conf import settings

        if not settings.DEBUG:
            return
        if os.environ.get("SKIP_SIMULATION") == "1":
            return
        from monitoring.simulation_runner import ensure_simulation_started

        ensure_simulation_started()
