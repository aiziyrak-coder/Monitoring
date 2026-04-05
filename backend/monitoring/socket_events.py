"""Socket.IO hodisalari — frontend socket.io-client bilan mos."""
from __future__ import annotations

import random
import time
from django.db import transaction
from django.utils import timezone

from monitoring.models import ClinicalNote, Patient
from monitoring.services.news2 import (
    DEFAULT_ALARM_LIMITS,
    calculate_news2,
    merge_alarm_limits,
    vitals_from_patient_row,
)
from monitoring.services.patient_payload import all_patients_wire, patient_to_wire_dict


def register_socket_handlers(sio) -> None:
    @sio.event
    def connect(sid, environ):
        sio.emit("initial_state", all_patients_wire(), room=sid)

    @sio.event
    def set_schedule(sid, data):
        if not isinstance(data, dict):
            return
        patient_id = data.get("patientId")
        interval_ms = int(data.get("intervalMs") or 0)
        p = Patient.objects.filter(pk=patient_id).first()
        if not p:
            return
        if interval_ms > 0:
            now = int(time.time() * 1000)
            p.scheduled_check = {
                "intervalMs": interval_ms,
                "nextCheckTime": now + interval_ms,
            }
        else:
            p.scheduled_check = None
        p.save(update_fields=["scheduled_check"])

    @sio.event
    def set_all_schedules(sid, data):
        if not isinstance(data, dict):
            return
        interval_ms = int(data.get("intervalMs") or 0)
        now = int(time.time() * 1000)
        qs = list(Patient.objects.all())
        if not qs:
            return
        if interval_ms > 0:
            for p in qs:
                p.scheduled_check = {
                    "intervalMs": interval_ms,
                    "nextCheckTime": now + interval_ms,
                }
        else:
            for p in qs:
                p.scheduled_check = None
        Patient.objects.bulk_update(qs, ["scheduled_check"])
        sio.emit("initial_state", all_patients_wire())

    @sio.event
    def clear_alarm(sid, data):
        if not isinstance(data, dict):
            return
        p = Patient.objects.filter(pk=data.get("patientId")).first()
        if p and p.alarm_level == Patient.ALARM_PURPLE:
            p.alarm_level = Patient.ALARM_NONE
            p.alarm_message = ""
            p.save(update_fields=["alarm_level", "alarm_message"])

    @sio.event
    def update_limits(sid, data):
        if not isinstance(data, dict):
            return
        p = Patient.objects.filter(pk=data.get("patientId")).first()
        limits = data.get("limits")
        if not p or not isinstance(limits, dict):
            return
        base = p.alarm_limits or {**DEFAULT_ALARM_LIMITS}
        p.alarm_limits = merge_alarm_limits(base, limits)
        p.save(update_fields=["alarm_limits"])

    @sio.event
    def measure_nibp(sid, data):
        if not isinstance(data, dict):
            return
        p = Patient.objects.filter(pk=data.get("patientId")).first()
        if not p:
            return
        p.nibp_sys = random.randint(100, 139)
        p.nibp_dia = random.randint(60, 89)
        p.nibp_time_ms = int(time.time() * 1000)
        p.save(update_fields=["nibp_sys", "nibp_dia", "nibp_time_ms"])

    @sio.event
    def discharge_patient(sid, data):
        if not isinstance(data, dict):
            return
        pid = data.get("patientId")
        if Patient.objects.filter(pk=pid).exists():
            Patient.objects.filter(pk=pid).delete()
            sio.emit("patient_discharged", pid)

    @sio.event
    def admit_patient(sid, data):
        if not isinstance(data, dict):
            return
        now_ms = int(time.time() * 1000)
        with transaction.atomic():
            p = Patient(
                name=data.get("name") or "Noma'lum",
                room=data.get("room") or "",
                diagnosis=data.get("diagnosis") or "",
                doctor=data.get("doctor") or "",
                assigned_nurse=data.get("assignedNurse") or "",
                device_battery=100.0,
                admission_date=timezone.now(),
                hr=75,
                spo2=98,
                nibp_sys=120,
                nibp_dia=80,
                rr=16,
                temp=36.6,
                nibp_time_ms=now_ms,
                alarm_level=Patient.ALARM_NONE,
                alarm_message="",
                alarm_limits={**DEFAULT_ALARM_LIMITS},
                scheduled_check={
                    "intervalMs": 60000,
                    "nextCheckTime": now_ms + 60000,
                },
                news2_score=0,
                is_pinned=False,
            )
            p.save()
            v = vitals_from_patient_row(p)
            p.news2_score = calculate_news2(v)
            p.save(update_fields=["news2_score"])
        sio.emit("patient_admitted", patient_to_wire_dict(p))

    @sio.event
    def toggle_pin(sid, data):
        if not isinstance(data, dict):
            return
        p = Patient.objects.filter(pk=data.get("patientId")).first()
        if p:
            p.is_pinned = not p.is_pinned
            p.save(update_fields=["is_pinned"])

    @sio.event
    def add_note(sid, data):
        if not isinstance(data, dict):
            return
        p = Patient.objects.filter(pk=data.get("patientId")).first()
        note = data.get("note")
        if not p or not isinstance(note, dict):
            return
        ClinicalNote.objects.create(
            patient=p,
            text=note.get("text") or "",
            author=note.get("author") or "",
            time_ms=int(time.time() * 1000),
        )

    @sio.event
    def acknowledge_alarm(sid, data):
        if not isinstance(data, dict):
            return
        p = Patient.objects.filter(pk=data.get("patientId")).first()
        if not p or p.alarm_level == Patient.ALARM_NONE:
            return
        if p.alarm_level in (Patient.ALARM_YELLOW, Patient.ALARM_PURPLE):
            p.alarm_level = Patient.ALARM_NONE
            p.alarm_message = ""
            p.save(update_fields=["alarm_level", "alarm_message"])
