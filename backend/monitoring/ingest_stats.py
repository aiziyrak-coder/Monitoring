"""HL7/REST qabul statistikasi (jarayon boshidan; diagnostika)."""
from __future__ import annotations

import threading
import time
from typing import Any

_lock = threading.Lock()
_hl7_messages_with_device = 0
_hl7_batches_with_obx = 0
_hl7_obx_segments = 0
_hl7_parse_nonempty = 0
_hl7_parse_empty_with_obx = 0
_vitals_written_to_patient = 0
_hl7_tcp_sessions_with_device = 0
# Tashqi HL7 ulanishlari (127.0.0.1 / ::1 hisoblanmaydi)
_hl7_tcp_external_accepts = 0
_hl7_tcp_external_no_device = 0
_hl7_last_external_peer: str | None = None
_hl7_last_external_peer_ms: int | None = None


def record_hl7_tcp_external_accept(peer: str) -> None:
    """Klinikadan kelgan TCP (peer — server ko‘radigan manzil; NAT tekshiruvi uchun)."""
    global _hl7_tcp_external_accepts, _hl7_last_external_peer, _hl7_last_external_peer_ms
    with _lock:
        _hl7_tcp_external_accepts += 1
        _hl7_last_external_peer = peer
        _hl7_last_external_peer_ms = int(time.time() * 1000)


def record_hl7_tcp_external_no_device() -> None:
    """TCP bor, lekin NAT / IP / MSH-3 bo‘yicha Device topilmadi."""
    global _hl7_tcp_external_no_device
    with _lock:
        _hl7_tcp_external_no_device += 1


def record_hl7_tcp_session_with_device() -> None:
    """Port 6006 da TCP ochilib, peer bo‘yicha qurilma topilganda (HL7 matni bo‘lmasa ham)."""
    global _hl7_tcp_sessions_with_device
    with _lock:
        _hl7_tcp_sessions_with_device += 1


def record_hl7_device_message(*, obx_segment_count: int, vitals_non_empty: bool) -> None:
    global _hl7_messages_with_device, _hl7_batches_with_obx, _hl7_obx_segments
    global _hl7_parse_nonempty, _hl7_parse_empty_with_obx
    with _lock:
        _hl7_messages_with_device += 1
        if obx_segment_count > 0:
            _hl7_batches_with_obx += 1
            _hl7_obx_segments += obx_segment_count
            if vitals_non_empty:
                _hl7_parse_nonempty += 1
            else:
                _hl7_parse_empty_with_obx += 1


def record_vitals_written_to_patient() -> None:
    global _vitals_written_to_patient
    with _lock:
        _vitals_written_to_patient += 1


def snapshot() -> dict[str, Any]:
    with _lock:
        return {
            "hl7MessagesWithResolvedDevice": _hl7_messages_with_device,
            "hl7TcpSessionsDeviceResolved": _hl7_tcp_sessions_with_device,
            "hl7BatchesWithObxSegments": _hl7_batches_with_obx,
            "hl7ObxSegmentTotal": _hl7_obx_segments,
            "hl7ParsedToVitalsNonEmpty": _hl7_parse_nonempty,
            "hl7ObxPresentButVitalsEmpty": _hl7_parse_empty_with_obx,
            "vitalUpdatesWrittenToPatientDb": _vitals_written_to_patient,
            "hl7TcpExternalAccepts": _hl7_tcp_external_accepts,
            "hl7TcpExternalNoDeviceMatch": _hl7_tcp_external_no_device,
            "hl7LastExternalPeerIp": _hl7_last_external_peer,
            "hl7LastExternalPeerWallclockMs": _hl7_last_external_peer_ms,
        }
