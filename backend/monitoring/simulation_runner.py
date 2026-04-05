import logging
import threading
import time

log = logging.getLogger(__name__)
_lock = threading.Lock()
_started = False


def ensure_simulation_started() -> None:
    global _started
    with _lock:
        if _started:
            return
        _started = True
        threading.Thread(target=_loop, name="clinic-vitals-sim", daemon=True).start()


def _loop() -> None:
    time.sleep(0.3)
    while True:
        try:
            time.sleep(1.0)
            from monitoring.services.simulation_tick import run_simulation_tick

            run_simulation_tick()
        except Exception:
            log.exception("Vitals simulation tick failed")
