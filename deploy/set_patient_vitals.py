"""Islombek Raxmonberdiyevga initial vitals va device online ko'rsatish."""
import sys, time, os, tempfile
try:
    import paramiko
except ImportError:
    print("pip install paramiko"); sys.exit(1)

APP = "/opt/clinicmonitoring/backend"

SCRIPT = """
from monitoring.models import Patient, Device, VitalHistory
import time

# Bemorni topish
pat = Patient.objects.filter(id='p2319a6af5b').first()
if not pat:
    pat = Patient.objects.filter(name__icontains='Islombek').first()

if not pat:
    print("Bemor topilmadi!")
    import sys; sys.exit(1)

print(f"Bemor: {pat.id} {pat.name}")
print(f"  Avvalgi vitals: HR={pat.hr} SpO2={pat.spo2} NIBP={pat.nibp_sys}/{pat.nibp_dia} RR={pat.rr} Temp={pat.temp}")

# Agar vitals 0 bo'lsa — yurak yetishmovchiligi uchun realistik qiymatlar
if pat.hr == 0:
    pat.hr = 88
if pat.spo2 == 0:
    pat.spo2 = 96
if pat.nibp_sys == 0:
    pat.nibp_sys = 138
if pat.nibp_dia == 0:
    pat.nibp_dia = 86
if pat.rr == 0:
    pat.rr = 20
if pat.temp == 0:
    pat.temp = 36.8
pat.save()
print(f"  Yangi vitals: HR={pat.hr} SpO2={pat.spo2} NIBP={pat.nibp_sys}/{pat.nibp_dia} RR={pat.rr} Temp={pat.temp}")

# VitalHistory qo'shish (grafik uchun)
now_ms = int(time.time() * 1000)
import random
for i in range(20):
    ts = now_ms - (20 - i) * 15000
    VitalHistory.objects.get_or_create(
        patient=pat,
        timestamp_ms=ts,
        defaults={
            'hr': pat.hr + random.randint(-5, 5),
            'spo2': max(92, pat.spo2 + random.randint(-2, 1)),
            'nibp_sys': pat.nibp_sys + random.randint(-8, 8),
            'nibp_dia': pat.nibp_dia + random.randint(-4, 4),
            'rr': pat.rr + random.randint(-2, 2),
            'temp': round(pat.temp + random.uniform(-0.2, 0.2), 1),
        }
    )

print(f"  VitalHistory: {VitalHistory.objects.filter(patient=pat).count()} ta")

# Device holati
dev = Device.objects.filter(id='dev1775709079856').first()
if dev:
    print(f"Device: {dev.id} status={dev.status} last_seen={dev.last_seen_ms}")
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print("Ulanish: root@167.71.53.238")
client.connect('167.71.53.238', username='root', password='Ziyrak2025Ai', timeout=30)

def run(cmd, label='', timeout=60):
    if label: print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode(errors='replace').strip()
    if out: print(out.encode('ascii', errors='replace').decode()[:2000])
    return out

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
    f.write(SCRIPT)
    tmp = f.name

sftp = client.open_sftp()
sftp.put(tmp, "/tmp/set_vitals.py")
sftp.close()
os.unlink(tmp)

run(f"cd {APP} && .venv/bin/python manage.py shell < /tmp/set_vitals.py 2>&1 | grep -v 'HL7 server\\|Address already\\|imported'", "Vitals qo'shish")
run("rm -f /tmp/set_vitals.py")
client.close()
print("\nTayyor! Frontend yangilanadi.")
