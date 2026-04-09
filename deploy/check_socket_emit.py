"""Socket emit bo'lyaptimi tekshirish (device online heartbeat)."""
import sys, time
try:
    import paramiko
except ImportError:
    print("pip install paramiko"); sys.exit(1)

PASSWORD = "Ziyrak2025Ai"
HOST = "167.71.53.238"
USER = "root"
APP = "/opt/clinicmonitoring/backend"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Ulanish: {USER}@{HOST}")
client.connect(HOST, username=USER, password=PASSWORD, timeout=30)

def run(cmd, label='', timeout=60):
    if label:
        print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode(errors='replace').strip()
    err = stderr.read().decode(errors='replace').strip()
    if out: print(out[:2000].encode('ascii', errors='replace').decode())
    return out

# Device va patient holati
CHECK = """
from monitoring.models import Device, Patient
dev = Device.objects.filter(id='dev1775709079856').first()
if dev:
    print(f"Device: {dev.id}")
    print(f"  status={dev.status}")
    print(f"  last_seen_ms={dev.last_seen_ms}")
    print(f"  last_vitals_applied_ms={dev.last_vitals_applied_ms}")
    print(f"  bed_id={dev.bed_id}")
    print(f"  nat_ip={dev.hl7_nat_source_ip}")
else:
    print("Device topilmadi!")

pat = Patient.objects.filter(bed_id='b1775706715328').first()
if pat:
    print(f"Patient: {pat.id} {pat.name}")
    print(f"  last_real_vitals_ms={pat.last_real_vitals_ms}")
    print(f"  HR={pat.hr} SpO2={pat.spo2}")
else:
    print("Patient topilmadi!")
"""

import tempfile, os
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
    f.write(CHECK)
    tmp = f.name

sftp = client.open_sftp()
sftp.put(tmp, "/tmp/check_socket.py")
sftp.close()
os.unlink(tmp)

run(f"cd {APP} && .venv/bin/python manage.py shell < /tmp/check_socket.py 2>&1 | grep -v 'HL7 server\\|Address already\\|imported'", "Device + Patient holati")
run("rm -f /tmp/check_socket.py")

# journalctl socket emit loglar
run("journalctl -u clinicmonitoring-backend -n 60 --no-pager 2>&1 | grep -iE 'socket|emit|payload|vitals_update' | tail -10", "Socket emit loglar")

client.close()
