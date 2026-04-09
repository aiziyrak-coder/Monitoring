"""30 soniya kuzatib HL7 vitallari kelyaptimi tekshirish."""
import sys, time
try:
    import paramiko
except ImportError:
    print("pip install paramiko"); sys.exit(1)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('167.71.53.238', username='root', password='Ziyrak2025Ai', timeout=30)

def run(cmd, label=''):
    if label:
        print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode(errors='replace').strip()
    if out:
        print(out)
    return out

print("30 soniya kutilmoqda (monitor xabari kelsin)...")
time.sleep(30)

run('curl -s http://127.0.0.1:8010/api/health', 'Health ingest stats')
run('journalctl -u clinicmonitoring-backend -n 60 --no-pager | grep -E "HL7|OBX|vital|HR|SpO2|NIBP|parsed" | tail -25', 'HL7 + OBX loglar')

# Bemorning so'nggi vitallari
RUN_SCRIPT = """
from monitoring.models import Patient, VitalHistory
from django.utils import timezone
import datetime

pat = Patient.objects.filter(bed__name__icontains='Joy-5').first()
if pat:
    print(f"Bemor: {pat.id} {pat.name}")
    print(f"HR: {pat.hr} SpO2: {pat.spo2} NIBP: {pat.nibp_sys}/{pat.nibp_dia} RR: {pat.rr} Temp: {pat.temp}")
    last_ms = getattr(pat, 'last_real_vitals_ms', 0) or 0
    if last_ms:
        ago = (timezone.now().timestamp()*1000 - last_ms) / 1000
        print(f"So'nggi real vital: {ago:.0f} soniya oldin")
    else:
        print("Hali real vital kelmagan (last_real_vitals_ms=0)")
    hist = VitalHistory.objects.filter(patient=pat).order_by('-recorded_at')[:5]
    for h in hist:
        print(f"  {h.recorded_at} HR={h.hr} SpO2={h.spo2} source={h.source}")
else:
    print("XATO: Joy-5 da bemor topilmadi")
"""

import tempfile, os
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
    f.write(RUN_SCRIPT)
    tmp = f.name

sftp = client.open_sftp()
sftp.put(tmp, "/tmp/check_vitals.py")
sftp.close()
os.unlink(tmp)

run("cd /opt/clinicmonitoring/backend && .venv/bin/python manage.py shell < /tmp/check_vitals.py 2>&1", "Bemorning vitallari DB da")
run("rm -f /tmp/check_vitals.py")
client.close()
