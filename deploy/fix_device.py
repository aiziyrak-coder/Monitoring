"""
Serverda: mavjud qurilmani o'chirish va Creative K12 ni haqiqiy NAT IP bilan qayta qo'shish.
Haqiqiy peer: 144.124.192.133
"""
import sys, os, tempfile

try:
    import paramiko
except ImportError:
    print("pip install paramiko")
    sys.exit(1)

PASSWORD = "Ziyrak2025Ai"
HOST = "167.71.53.238"
USER = "root"
APP = "/opt/clinicmonitoring/backend"

MONITOR_LOCAL_IP  = "192.168.88.104"
MONITOR_MAC       = "02:01:08:C1:83:4B"
MONITOR_MODEL     = "Creative Medical K12"
BED_NAME          = "Joy-5"
REAL_NAT_IP       = "144.124.192.133"

FIX_SCRIPT = """
from monitoring.models import Device, Bed, Patient

# 1. Eski qurilmalar
print("Eski qurilmalar:", Device.objects.count())
for d in Device.objects.all():
    print("  DEL:", d.id, d.ip_address, getattr(d, 'hl7_nat_source_ip', '?'), d.status)
Device.objects.all().delete()

# 2. Joy-5
bed = Bed.objects.filter(name__icontains='Joy-5').first()
if not bed:
    print("XATO: Joy-5 topilmadi!")
    for b in Bed.objects.select_related('room__department').all()[:15]:
        print(" ", b.id, b.name, b.room.name, b.room.department.name)
    import sys; sys.exit(1)
print("Karavat:", bed.id, bed.name, "xona:", bed.room.name)

# 3. Yangi qurilma
dev = Device(
    ip_address='192.168.88.104',
    mac_address='02:01:08:C1:83:4B',
    model='Creative Medical K12',
    bed=bed,
    hl7_nat_source_ip='144.124.192.133',
    hl7_sending_application='',
)
dev.save()
print("Yangi qurilma:", dev.id, "IP:", dev.ip_address, "NAT:", dev.hl7_nat_source_ip, "BED:", dev.bed_id)

# 4. Bemor
pat = Patient.objects.filter(bed=bed).first()
if pat:
    print("Bemor:", pat.id, pat.name)
else:
    print("DIQQAT: Joy-5 da bemor yo'q — Bemorlar > Qabul qiling")
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Ulanish: {USER}@{HOST} ...")
client.connect(HOST, username=USER, password=PASSWORD, timeout=30)

def run(cmd, label=""):
    if label:
        print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode(errors="replace").strip()
    err = stderr.read().decode(errors="replace").strip()
    if out:
        print(out)
    if err and "warning" not in err.lower() and "deprecat" not in err.lower():
        print("[ERR]", err[:800])
    return out

# manage.py shell -c orqali ishlatamiz
shell_cmd = FIX_SCRIPT.replace('"', '\\"').replace('\n', '\\n').replace("'", "\\'")

# Faylga yozib sftp orqali uzatamiz
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
    f.write(FIX_SCRIPT)
    tmp = f.name

sftp = client.open_sftp()
sftp.put(tmp, "/tmp/clinic_fix.py")
sftp.close()
os.unlink(tmp)

# manage.py shell < /tmp/clinic_fix.py
run(f"cd {APP} && .venv/bin/python manage.py shell < /tmp/clinic_fix.py 2>&1", "Qurilmani o'chirib qayta qo'shish")
run("curl -s http://127.0.0.1:8010/api/health | python3 -c \""
    "import sys,json; d=json.load(sys.stdin); i=d.get('ingest',{}); "
    "print('External accepts:', i.get('hl7TcpExternalAccepts',0)); "
    "print('No device match:', i.get('hl7TcpExternalNoDeviceMatch',0)); "
    "print('Last peer IP:', i.get('hl7LastExternalPeerIp','?'))"
    "\"", "Health tekshiruv")
run("journalctl -u clinicmonitoring-backend -n 20 --no-pager | grep -i HL7 | tail -10", "HL7 loglar")
run("rm -f /tmp/clinic_fix.py")
client.close()
print(f"\nTayyor! NAT IP {REAL_NAT_IP} bilan qurilma qayta qo'shildi.")
