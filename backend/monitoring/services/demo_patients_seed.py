"""8 ta stabil demo bemorni yaratish (4 reanimatsiya, 4 palata)."""
from __future__ import annotations

import time

from django.utils import timezone

from monitoring.models import Patient, VitalHistory
from monitoring.services.news2 import DEFAULT_ALARM_LIMITS

# Taqdimot: kritik signal yo'q, chegaralar standart
_SPECS: list[dict] = [
    {
        "id": "demo-p-01",
        "name": "A. Qodirova",
        "room": "Reanimatsiya - R1",
        "diagnosis": "Postoperatsion kuzatuv, holat barqaror",
        "doctor": "Dr. Karimov",
        "assigned_nurse": "Hamshira Tursunova",
        "hr": 72,
        "spo2": 98,
        "nibp_sys": 118,
        "nibp_dia": 76,
        "rr": 16,
        "temp": 36.6,
        "battery": 92.0,
    },
    {
        "id": "demo-p-02",
        "name": "B. Toshmatov",
        "room": "Reanimatsiya - R2",
        "diagnosis": "Nafas yetishmovchiligi — yengil, stabil",
        "doctor": "Dr. Nazarov",
        "assigned_nurse": "Hamshira Azimova",
        "hr": 78,
        "spo2": 97,
        "nibp_sys": 122,
        "nibp_dia": 78,
        "rr": 18,
        "temp": 36.7,
        "battery": 88.0,
    },
    {
        "id": "demo-p-03",
        "name": "D. Ahmadova",
        "room": "Reanimatsiya - R3",
        "diagnosis": "DM tip 2, kompensatsiya yaxshi",
        "doctor": "Dr. Saidov",
        "assigned_nurse": "Hamshira Ergasheva",
        "hr": 68,
        "spo2": 99,
        "nibp_sys": 115,
        "nibp_dia": 74,
        "rr": 15,
        "temp": 36.5,
        "battery": 95.0,
    },
    {
        "id": "demo-p-04",
        "name": "M. Umarov",
        "room": "Reanimatsiya - R4",
        "diagnosis": "Yurak urishi ritmi barqaror",
        "doctor": "Dr. Rahimov",
        "assigned_nurse": "Hamshira Hasanova",
        "hr": 82,
        "spo2": 96,
        "nibp_sys": 128,
        "nibp_dia": 82,
        "rr": 17,
        "temp": 36.8,
        "battery": 79.0,
    },
    {
        "id": "demo-p-05",
        "name": "F. Rahimova",
        "room": "Palata - 301",
        "diagnosis": "Yengil bronxit, holat yaxshi",
        "doctor": "Dr. Mirzayeva",
        "assigned_nurse": "Hamshira Olimova",
        "hr": 74,
        "spo2": 98,
        "nibp_sys": 120,
        "nibp_dia": 78,
        "rr": 16,
        "temp": 36.6,
        "battery": 91.0,
    },
    {
        "id": "demo-p-06",
        "name": "G. Saidova",
        "room": "Palata - 302",
        "diagnosis": "Gipertoniya, AD nazorat ostida",
        "doctor": "Dr. Yusupov",
        "assigned_nurse": "Hamshira Karimova",
        "hr": 76,
        "spo2": 97,
        "nibp_sys": 117,
        "nibp_dia": 75,
        "rr": 15,
        "temp": 36.7,
        "battery": 86.0,
    },
    {
        "id": "demo-p-07",
        "name": "H. Norimova",
        "room": "Palata - 303",
        "diagnosis": "Operatsiyadan keyin tiklanish",
        "doctor": "Dr. Tursunov",
        "assigned_nurse": "Hamshira Rustamova",
        "hr": 70,
        "spo2": 99,
        "nibp_sys": 119,
        "nibp_dia": 77,
        "rr": 14,
        "temp": 36.5,
        "battery": 94.0,
    },
    {
        "id": "demo-p-08",
        "name": "J. Melieva",
        "room": "Palata - 304",
        "diagnosis": "Kuzatuv, laboratoriya normada",
        "doctor": "Dr. Polatov",
        "assigned_nurse": "Hamshira Shodieva",
        "hr": 79,
        "spo2": 98,
        "nibp_sys": 121,
        "nibp_dia": 79,
        "rr": 16,
        "temp": 36.6,
        "battery": 83.0,
    },
]


def seed_demo_patients(*, refresh_history: bool = True) -> int:
    """
    8 ta bemorni yaratadi yoki yangilaydi.
    Qaytaradi: yozilgan/yangilangan bemorlar soni.
    """
    now_ms = int(time.time() * 1000)
    count = 0
    for spec in _SPECS:
        pid = spec["id"]
        defaults = {
            "name": spec["name"],
            "room": spec["room"],
            "diagnosis": spec["diagnosis"],
            "doctor": spec["doctor"],
            "assigned_nurse": spec["assigned_nurse"],
            "device_battery": spec["battery"],
            "admission_date": timezone.now(),
            "hr": spec["hr"],
            "spo2": spec["spo2"],
            "nibp_sys": spec["nibp_sys"],
            "nibp_dia": spec["nibp_dia"],
            "rr": spec["rr"],
            "temp": spec["temp"],
            "nibp_time_ms": now_ms,
            "last_real_vitals_ms": now_ms,
            "alarm_level": Patient.ALARM_NONE,
            "alarm_message": "",
            "alarm_limits": {**DEFAULT_ALARM_LIMITS},
            "scheduled_check": None,
            "is_pinned": False,
            "bed": None,
        }
        Patient.objects.update_or_create(id=pid, defaults=defaults)
        count += 1

        if refresh_history:
            VitalHistory.objects.filter(patient_id=pid).delete()
            rows: list[VitalHistory] = []
            base_hr = float(spec["hr"])
            base_spo2 = float(spec["spo2"])
            for step in range(12, 0, -1):
                ts = now_ms - step * 30_000
                jitter = (step % 3) - 1
                rows.append(
                    VitalHistory(
                        patient_id=pid,
                        timestamp_ms=ts,
                        hr=max(60.0, base_hr + jitter * 2),
                        spo2=max(95.0, min(99.0, base_spo2 + jitter * 0.5)),
                        nibp_sys=float(spec["nibp_sys"]) + jitter,
                        nibp_dia=float(spec["nibp_dia"]) + jitter,
                        rr=float(spec["rr"]) + jitter * 0.5,
                        temp=float(spec["temp"]) + jitter * 0.05,
                    )
                )
            VitalHistory.objects.bulk_create(rows)

    return count
