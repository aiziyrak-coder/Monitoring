"""NEWS2 balli (oldingi Node server bilan bir xil qoidalar)."""


def calculate_news2(v: dict) -> int:
    hr = int(v["hr"])
    spo2 = int(v["spo2"])
    nibp_sys = int(v["nibpSys"])
    rr = int(v["rr"])
    temp = float(v["temp"])

    score = 0
    if rr <= 8:
        score += 3
    elif 9 <= rr <= 11:
        score += 1
    elif 21 <= rr <= 24:
        score += 2
    elif rr >= 25:
        score += 3

    if spo2 <= 91:
        score += 3
    elif 92 <= spo2 <= 93:
        score += 2
    elif 94 <= spo2 <= 95:
        score += 1

    if nibp_sys <= 90:
        score += 3
    elif 91 <= nibp_sys <= 100:
        score += 2
    elif 101 <= nibp_sys <= 110:
        score += 1
    elif nibp_sys >= 220:
        score += 3

    if hr <= 40:
        score += 3
    elif 41 <= hr <= 50:
        score += 1
    elif 91 <= hr <= 110:
        score += 1
    elif 111 <= hr <= 130:
        score += 2
    elif hr >= 131:
        score += 3

    if temp <= 35.0:
        score += 3
    elif 35.1 <= temp <= 36.0:
        score += 1
    elif 38.1 <= temp <= 39.0:
        score += 1
    elif temp >= 39.1:
        score += 2

    return score


DEFAULT_ALARM_LIMITS: dict = {
    "hr": {"low": 50, "high": 120},
    "spo2": {"low": 90, "high": 100},
    "nibpSys": {"low": 90, "high": 160},
    "nibpDia": {"low": 50, "high": 100},
    "rr": {"low": 8, "high": 30},
    "temp": {"low": 35.5, "high": 38.5},
}


def merge_alarm_limits(base: dict, patch: dict) -> dict:
    out = {**base}
    for key, val in patch.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = {**out[key], **val}
        else:
            out[key] = val
    return out


def vitals_from_patient_row(p) -> dict:
    return {
        "hr": p.hr,
        "spo2": p.spo2,
        "nibpSys": p.nibp_sys,
        "nibpDia": p.nibp_dia,
        "rr": p.rr,
        "temp": float(p.temp),
    }
